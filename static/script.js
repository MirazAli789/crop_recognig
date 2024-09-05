async function uploadImage() {
    const input = document.getElementById('imageInput');
    const file = input.files[0];
    const spinner = document.getElementById('spinner');
    const cropSuggestionBox = document.getElementById('cropSuggestion');

    if (!file) {
        alert('Please select a file.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    // Show spinner and hide previous result
    spinner.style.display = 'block';
    cropSuggestionBox.classList.remove('show');

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        
        if (data.error) {
            cropSuggestionBox.innerText = `Error: ${data.error}`;
        } else {
            cropSuggestionBox.innerText = `Recognized Crop: ${data.recognized_crop}\nSuggestion: ${data.suggestion}`;
        }

        // Show the suggestion
        cropSuggestionBox.classList.add('show');
    } catch (error) {
        console.error('Error uploading image:', error);
        alert('An error occurred. Please try again.');
    } finally {
        spinner.style.display = 'none';
    }
}

function previewImage() {
    const input = document.getElementById('imageInput');
    const preview = document.getElementById('imagePreview');
    const file = input.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        }
        reader.readAsDataURL(file);
    }
}
