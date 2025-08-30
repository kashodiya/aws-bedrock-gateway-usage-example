#!/usr/bin/env python3

import os
import glob
from flask import Flask, render_template_string, send_file, url_for

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Generated Images - AWS Bedrock Stable Diffusion</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .image-gallery {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        .image-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .image-card img {
            width: 100%;
            height: auto;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .image-info {
            font-size: 14px;
            color: #666;
        }
        .no-images {
            text-align: center;
            padding: 40px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .generate-button {
            display: inline-block;
            background: #007bff;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 10px;
        }
        .generate-button:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 AWS Bedrock Image Generation</h1>
        <p>Generated images using Stable Diffusion and Amazon Titan models</p>
    </div>
    
    {% if images %}
        <div class="image-gallery">
            {% for image in images %}
            <div class="image-card">
                <img src="{{ url_for('serve_image', filename=image.filename) }}" alt="Generated Image">
                <div class="image-info">
                    <strong>File:</strong> {{ image.filename }}<br>
                    <strong>Size:</strong> {{ image.size_mb }} MB<br>
                    <strong>Model:</strong> {{ image.model }}<br>
                    <strong>Generated:</strong> {{ image.timestamp }}
                </div>
            </div>
            {% endfor %}
        </div>
    {% else %}
        <div class="no-images">
            <h2>No images generated yet</h2>
            <p>Run the image generation script to create some images!</p>
            <code>python3 setup_stable_diffusion.py "Your prompt here"</code>
        </div>
    {% endif %}
    
    <div style="text-align: center; margin-top: 30px;">
        <p>To generate more images, run:</p>
        <code style="background: #f8f9fa; padding: 10px; border-radius: 5px; display: inline-block;">
            python3 setup_stable_diffusion.py "Your creative prompt here"
        </code>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    # Find all generated images
    image_files = glob.glob('generated_image_*.png')
    
    images = []
    for filename in image_files:
        try:
            size_bytes = os.path.getsize(filename)
            size_mb = round(size_bytes / (1024 * 1024), 2)
            
            # Extract model name from filename
            model = "Unknown"
            if "titan" in filename:
                model = "Amazon Titan Image Generator"
            elif "stable" in filename:
                model = "Stability AI SDXL"
            
            # Extract timestamp from filename
            timestamp = "Unknown"
            parts = filename.split('_')
            if len(parts) >= 3:
                timestamp = f"{parts[-3]} {parts[-2]}"
            
            images.append({
                'filename': filename,
                'size_mb': size_mb,
                'model': model,
                'timestamp': timestamp
            })
        except:
            continue
    
    # Sort by filename (which includes timestamp)
    images.sort(key=lambda x: x['filename'], reverse=True)
    
    return render_template_string(HTML_TEMPLATE, images=images)

@app.route('/image/<filename>')
def serve_image(filename):
    return send_file(filename)

if __name__ == '__main__':
    print("🌐 Starting image viewer server...")
    print("📸 View your generated images at: http://localhost:57798")
    print("🔄 The page will automatically show new images as you generate them")
    print("⏹️  Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=57798, debug=True)
