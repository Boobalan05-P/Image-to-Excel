import io
import os
import pandas as pd
from PIL import Image
import pytesseract
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# விண்டோஸ் கம்ப்யூட்டரில் Tesseract OCR இன்ஸ்டால் ஆகியிருக்கும் பாதை
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/convert', methods=['GET', 'POST'])
def convert_image_to_excel():
    if request.method == 'GET':
        return jsonify({'message': 'Server is ready.'}), 200

    # 1. ரிக்வஸ்ட்டில் ஃபைல் வருகிறதா என்று பார்க்கிறது
    file = request.files.get('image') or request.files.get('formdata')
    if not file and len(request.files) > 0:
        first_key = list(request.files.keys())[0]
        file = request.files[first_key]

    if not file or file.filename == '':
        return jsonify({'error': 'No file received'}), 400

    try:
        # 🎯 2. எரர் வராமல் தடுக்க இமேஜை பாதுகாப்பான முறையில் 'RGB' ஆக மாற்றி மெமரியில் லோடு செய்கிறோம்
        img_bytes = file.read()
        raw_image = Image.open(io.BytesIO(img_bytes))
        image = raw_image.convert('RGB') 
        
        # 3. Tesseract மூலம் இமேஜை உரை வடிவாக மாற்றுகிறோம்
        extracted_text = pytesseract.image_to_string(image)

        # 4. வரிகளை எக்செல் கட்டங்களாக பிரிக்கிறோம்
        rows = []
        for line in extracted_text.strip().split('\n'):
            if line.strip():
                # டாப் அல்லது கமா இருந்தால் பிரிக்க, இல்லையெனில் ஸ்பேஸ் மூலம் பிரிக்கிறது
                columns = line.split('\t') if '\t' in line else line.split()
                rows.append(columns)

        # ஒருவேளை இமேஜ் மங்கலாக இருந்து படிக்க முடியாவிட்டால் வெற்று எக்செல் வராமல் தடுக்க ஒரு டெக்ஸ்ட் வைக்கிறோம்
        if not rows:
            rows = [["இமேஜில் உள்ள அட்டவணையைத் துல்லியமாகப் படிக்க முடியவில்லை. தெளிவான இமேஜை அப்லோடு செய்யவும்."]]

        df = pd.DataFrame(rows)
        
        # 5. எக்செல் கோப்பை தற்காலிக நினைவகத்தில் உருவாக்குகிறது
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