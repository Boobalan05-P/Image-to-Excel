const uploadBox = document.getElementById('upload-box');
const fileInput = document.getElementById('fileInput');
const previewBox = document.getElementById('preview-box');
const imagePreview = document.getElementById('imagePreview');
const convertBtn = document.getElementById('convertBtn');
const loading = document.getElementById('loading');
if (uploadBox && fileInput) {
    uploadBox.addEventListener('click', function() {
        fileInput.click();
    });
}
if (fileInput) {
    fileInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                if (imagePreview && previewBox && uploadBox) {
                    imagePreview.src = e.target.result;
                    previewBox.style.display = 'block'; 
                    uploadBox.style.display = 'none'; 
                }
            }
            reader.readAsDataURL(file);
        }
    });
}
if (convertBtn) {
    convertBtn.addEventListener('click', function() {
        const file = fileInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('image', file);
        if (loading && previewBox) {
            loading.style.display = 'block';
            previewBox.style.display = 'none';
        }
        fetch('http://127.0.0.1:5000/api/convert', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) throw new Error('Conversion failed');
            return response.blob();
        })
        .then(blob => {
            if (loading && uploadBox) {
                loading.style.display = 'none'; 
                uploadBox.style.display = 'block'; 
            }
            fileInput.value = ''; 
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'Extracted_Table.xlsx';
            document.body.appendChild(a);
            a.click();
            a.remove();
            
            alert("Success! Excel file downloaded successfully. 🎉");
        })
        .catch(error => {
            if (loading && previewBox) {
                loading.style.display = 'none';
                previewBox.style.display = 'block';
            }
            console.error('Error:', error);
            alert("Something went wrong during conversion!");
        });
    });
}