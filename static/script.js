async function uploadImage() {
    const input = document.getElementById('imageInput');
    const file = input.files[0];

    if (!file) {
        alert('Please select a file.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        const cropSuggestionBox = document.getElementById('cropSuggestion');
        if (data.error) {
            cropSuggestionBox.innerText = `Error: ${data.error}`;
        } else {
            cropSuggestionBox.innerText = `Recognized Crop: ${data.recognized_crop}\nSuggestion: ${data.suggestion}`;
        }

        cropSuggestionBox.style.opacity = 0;
        cropSuggestionBox.classList.remove('animate');
        void cropSuggestionBox.offsetWidth; // Trigger reflow
        cropSuggestionBox.classList.add('animate');
        cropSuggestionBox.style.opacity = 1;
    } catch (error) {
        console.error('Error uploading image:', error);
        alert('An error occurred. Please try again.');
    }
}
