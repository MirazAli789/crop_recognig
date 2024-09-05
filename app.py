from flask import Flask, render_template, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import logging
from threading import Thread
import json
import os

# Initialize Flask app
app = Flask(__name__)

# Load a pre-trained model (MobileNetV2)
model = tf.keras.applications.MobileNetV2(weights='imagenet')

# Load crop suggestions
with open('suggestions.json', 'r') as f:
    suggestions = json.load(f)

# Set up logging
logging.basicConfig(level=logging.INFO)

def prepare_image(image):
    try:
        image = image.resize((224, 224))  # Resize to match model input
        image = np.array(image)
        image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
        image = np.expand_dims(image, axis=0)  # Add batch dimension
        return image
    except Exception as e:
        logging.error(f"Error preparing image: {str(e)}")
        raise

def async_predict(image, result_holder):
    try:
        preds = model.predict(image)
        result_holder['preds'] = preds
    except Exception as e:
        logging.error(f"Error during prediction: {str(e)}")
        result_holder['error'] = str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        logging.error("No file part")
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        logging.error("No selected file")
        return jsonify({"error": "No selected file"}), 400

    try:
        image = Image.open(io.BytesIO(file.read()))
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        return jsonify({"error": f"Error processing image: {str(e)}"}), 500

    try:
        image = prepare_image(image)
    except Exception as e:
        return jsonify({"error": f"Error preparing image: {str(e)}"}), 500

    result_holder = {}
    prediction_thread = Thread(target=async_predict, args=(image, result_holder))
    prediction_thread.start()
    prediction_thread.join()

    preds = result_holder.get('preds')
    if 'error' in result_holder:
        logging.error(f"Error making prediction: {result_holder['error']}")
        return jsonify({"error": f"Error making prediction: {result_holder['error']}"}), 500

    try:
        decoded_preds = tf.keras.applications.mobilenet_v2.decode_predictions(preds, top=1)[0]
        recognized_crop = decoded_preds[0][1]
        suggestion = suggestions.get(recognized_crop.lower(), "No suggestion available for this crop.")
    except Exception as e:
        logging.error(f"Error decoding predictions: {str(e)}")
        return jsonify({"error": f"Error decoding predictions: {str(e)}"}), 500

    return jsonify({"recognized_crop": recognized_crop, "suggestion": suggestion})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use PORT environment variable or default to 5000
    app.run(host='0.0.0.0', port=port, debug=True)
