// 1. HTML எலிமெண்ட்டுகளை சரியாக இணைத்தல்
const uploadBox = document.getElementById('upload-box');
const fileInput = document.getElementById('fileInput');
const previewBox = document.getElementById('preview-box');
const imagePreview = document.getElementById('imagePreview');
const convertBtn = document.getElementById('convertBtn');
const loading = document.getElementById('loading');

// 2. நீல நிற பாக்ஸைக் கிளிக் செய்யும் போது ஃபைல் செலக்டர் ஓப்பன் ஆக
if (uploadBox && fileInput) {
    uploadBox.addEventListener('click', function() {
        fileInput.click();
    });
}

// 3. இமேஜைத் தேர்ந்தெடுத்தவுடன் பிரிவியூ காட்டுதல்
if (fileInput) {
    fileInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                if (imagePreview && previewBox && uploadBox) {
                    imagePreview.src = e.target.result;
                    previewBox.style.display = 'block'; // பிரிவியூ பாக்ஸ் காட்டும்
                    uploadBox.style.display = 'none';   // நீல பாக்ஸை மறைக்கும்
                }
            }
            reader.readAsDataURL(file);
        }
    });
}

// 4. பட்டனை கிளிக் செய்யும் போது பைத்தான் சர்வருக்கு அனுப்பி எக்செல் டவுன்லோடு செய்தல்
if (convertBtn) {
    convertBtn.addEventListener('click', function() {
        const file = fileInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('image', file);

        // லோடிங் அனிமேஷனைக் காட்டு
        if (loading && previewBox) {
            loading.style.display = 'block';
            previewBox.style.display = 'none';
        }

        // 🎯 இங்கிருந்த பிழைகள் அனைத்தும் கீழே முழுமையாகச் சரிசெய்யப்பட்டுள்ளது
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

            // எக்செல் கோப்பை கணினியில் டவுன்லோடு செய்ய வைக்கும் லாஜிக்
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