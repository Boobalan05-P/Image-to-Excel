import io
import os
import pandas as pd
from PIL import Image
import pytesseract
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/convert', methods=['GET', 'POST'])
def convert_image_to_excel():
    if request.method == 'GET':
        return jsonify({'message': 'Server is ready.'}), 200
    file = request.files.get('image') or request.files.get('formdata')
    if not file and len(request.files) > 0:
        first_key = list(request.files.keys())[0]
        file = request.files[first_key]

    if not file or file.filename == '':
        return jsonify({'error': 'No file received'}), 400

    try:
        img_bytes = file.read()
        raw_image = Image.open(io.BytesIO(img_bytes))
        image = raw_image.convert('RGB') 
        extracted_text = pytesseract.image_to_string(image)
        rows = []
        for line in extracted_text.strip().split('\n'):
            if line.strip():
                columns = line.split('\t') if '\t' in line else line.split()
                rows.append(columns)
        if not rows:
            rows = [["The table in the image cannot be read accurately.Please upload a clearly image."]]

        df = pd.DataFrame(rows)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, header=False)
        output.seek(0)

        print("🔥 SUCCESS: Excel file generated successfully! 🎉")
        return send_file(
            output, 
            as_attachment=True, 
            download_name='ConvertedTable.xlsx', 
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        print("Backend Error during conversion:", str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)