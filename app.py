from flask import Flask, render_template, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image
import io

app = Flask(__name__)

# Load a pre-trained model (MobileNetV2)
model = tf.keras.applications.MobileNetV2(weights='imagenet')

# Load crop suggestions
import json
with open('suggestions.json', 'r') as f:
    suggestions = json.load(f)

def prepare_image(image):
    image = image.resize((224, 224))  # Resize to match model input
    image = np.array(image)
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        image = Image.open(io.BytesIO(file.read()))
    except Exception as e:
        return jsonify({"error": f"Error processing image: {str(e)}"}), 500

    image = prepare_image(image)

    try:
        preds = model.predict(image)
        decoded_preds = tf.keras.applications.mobilenet_v2.decode_predictions(preds, top=1)[0]
        recognized_crop = decoded_preds[0][1]  # Get the predicted label
    except Exception as e:
        return jsonify({"error": f"Error making prediction: {str(e)}"}), 500

    suggestion = suggestions.get(recognized_crop.lower(), "No suggestion available for this crop.")
    return jsonify({"recognized_crop": recognized_crop, "suggestion": suggestion})
