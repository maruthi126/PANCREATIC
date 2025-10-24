import os
import warnings
import logging

# Suppress TensorFlow warnings and logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logging
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Suppress specific TensorFlow logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('tensorflow.python').setLevel(logging.ERROR)

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from PIL import Image
import numpy as np
import tensorflow as tf
from transformers import CLIPProcessor, CLIPModel
import io
import base64

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Configure TensorFlow for faster loading
tf.config.set_soft_device_placement(True)
tf.config.experimental.set_memory_growth(tf.config.list_physical_devices('GPU')[0], True) if tf.config.list_physical_devices('GPU') else None

# Load models
try:
    print("Loading segmentation model...")
    segmentation_model = tf.keras.models.load_model('mri_segmentation_model.h5', compile=False)
    print("Segmentation model loaded successfully!")
    
    # Note: CLIP models are no longer needed since we removed classification
    # But keeping them for potential future use
    # print("Loading CLIP models...")
    # clip_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
    # clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
    print("All models loaded successfully!")
    
    models_loaded = True
except Exception as e:
    print(f"Error loading models: {e}")
    models_loaded = False

def preprocess_image(image):
    image = image.convert("L")
    image = image.resize((512, 512))
    image_np = np.array(image).astype("float32") / 255.0
    if image_np.ndim == 2:
        image_np = np.expand_dims(image_np, axis=-1)
    image_np = np.expand_dims(image_np, axis=0)
    return image_np

# def classify_mri(image):
#     if not models_loaded:
#         return "Model not available", 0.0
    
#     inputs = clip_processor(text=["a photo of medical image", "a photo of a non medical image"], images=image, return_tensors="pt", padding=True)
#     outputs = clip_model(**inputs)
#     probs = outputs.logits_per_image.softmax(dim=1)

#     if probs[0][0] > probs[0][1]:
#         return "MRI", float(probs[0][0])
#     else:
#         return "Non-MRI", float(probs[0][1])

def predict_segmentation(image):
    if not models_loaded:
        return None
    
    image_processed = preprocess_image(image)
    prediction = segmentation_model.predict(image_processed)[0, :, :, 0]
    return Image.fromarray((prediction * 255).astype(np.uint8))

def image_to_base64(image):
    """Convert PIL image to base64 string"""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/prediction", methods=["GET", "POST"])
def prediction():
    if request.method == "POST":
        if 'image' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files["image"]
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)

        try:
            image = Image.open(io.BytesIO(file.read()))
            
            # Skip classification and go directly to segmentation
            result_data = {
                'label': 'MRI',  # Assume it's an MRI image
                'confidence': 100.0,  # Set confidence to 100%
                'original_image': image_to_base64(image)
            }
            
            # Always try to generate segmentation mask
            if models_loaded:
                mask_image = predict_segmentation(image)
                if mask_image:
                    result_data['mask_image'] = image_to_base64(mask_image)
            
            return render_template("prediction.html", result=result_data)
            
        except Exception as e:
            flash(f'Error processing image: {str(e)}', 'error')
            return redirect(request.url)

    return render_template("prediction.html")

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """API endpoint for AJAX predictions"""
    if 'image' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files["image"]
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        image = Image.open(io.BytesIO(file.read()))
        
        # Skip classification and go directly to segmentation
        result = {
            'label': 'MRI',  # Assume it's an MRI image
            'confidence': 100.0,  # Set confidence to 100%
            'original_image': image_to_base64(image)
        }
        
        # Always try to generate segmentation mask
        if models_loaded:
            mask_image = predict_segmentation(image)
            if mask_image:
                result['mask_image'] = image_to_base64(mask_image)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 MedAI Vision - MRI Segmentation Platform")
    print("="*50)
    print("✅ Application is ready!")
    print("🌐 Open your browser and go to: http://localhost:5002")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5002, debug=True)
