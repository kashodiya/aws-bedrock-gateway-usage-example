
#!/usr/bin/env python3

from flask import Flask, render_template_string, request, jsonify, send_file
import os
import glob
from datetime import datetime
import subprocess
import json

app = Flask(__name__)

# HTML template for the image gallery
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS Bedrock Image Generator</title>
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .generator-form {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], textarea, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        textarea {
            height: 100px;
            resize: vertical;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .image-card {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .image-card:hover {
            transform: translateY(-5px);
        }
        .image-card img {
            width: 100%;
            height: 250px;
            object-fit: cover;
        }
        .image-info {
            padding: 15px;
        }
        .image-info h3 {
            margin: 0 0 10px 0;
            color: #333;
        }
        .image-info p {
            margin: 5px 0;
            color: #666;
            font-size: 14px;
        }
        .status {
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .status.success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .status.info {
            background-color: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .loading {
            text-align: center;
            padding: 20px;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 AWS Bedrock Image Generator</h1>
        <p>Generate stunning images using Amazon Titan and Stable Diffusion models</p>
    </div>

    <div class="generator-form">
        <h2>Generate New Image</h2>
        <form id="generateForm">
            <div class="form-group">
                <label for="prompt">Image Prompt:</label>
                <textarea id="prompt" name="prompt" placeholder="Describe the image you want to generate..." required>A majestic dragon flying over a medieval castle at sunset, fantasy art style</textarea>
            </div>
            <div class="form-group">
                <label for="model">Model:</label>
                <select id="model" name="model">
                    <option value="amazon.titan-image-generator-v1">Amazon Titan Image Generator v1</option>
                    <option value="amazon.titan-image-generator-v2:0">Amazon Titan Image Generator v2</option>
                    <option value="stability.stable-diffusion-xl-v1">Stability AI SDXL 1.0</option>
                </select>
            </div>
            <button type="submit" id="generateBtn">🚀 Generate Image</button>
        </form>
        
        <div id="status"></div>
    </div>

    <div class="gallery">
        {% for image in images %}
        <div class="image-card">
            <img src="/image/{{ image.filename }}" alt="{{ image.prompt }}" loading="lazy">
            <div class="image-info">
                <h3>{{ image.model }}</h3>
                <p><strong>Prompt:</strong> {{ image.prompt[:100] }}{% if image.prompt|length > 100 %}...{% endif %}</p>
                <p><strong>Created:</strong> {{ image.created }}</p>
                <p><strong>Size:</strong> {{ image.size }}</p>
            </div>
        </div>
        {% endfor %}
    </div>

    <script>
        document.getElementById('generateForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const prompt = document.getElementById('prompt').value;
            const model = document.getElementById('model').value;
            const generateBtn = document.getElementById('generateBtn');
            const statusDiv = document.getElementById('status');
            
            // Show loading state
            generateBtn.disabled = true;
            generateBtn.textContent = '🔄 Generating...';
            statusDiv.innerHTML = `
                <div class="status info">
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Generating your image... This may take 30-60 seconds.</p>
                    </div>
                </div>
            `;
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ prompt, model })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    statusDiv.innerHTML = `
                        <div class="status success">
                            <p>✅ Image generated successfully! Refreshing gallery...</p>
                        </div>
                    `;
                    // Refresh the page to show the new image
                    setTimeout(() => window.location.reload(), 2000);
                } else {
                    statusDiv.innerHTML = `
                        <div class="status error">
                            <p>❌ Error: ${result.error}</p>
                        </div>
                    `;
                }
            } catch (error) {
                statusDiv.innerHTML = `
                    <div class="status error">
                        <p>❌ Network error: ${error.message}</p>
                    </div>
                `;
            } finally {
                generateBtn.disabled = false;
                generateBtn.textContent = '🚀 Generate Image';
            }
        });
    </script>
</body>
</html>
"""

def get_image_info(filename):
    """Get information about an image file"""
    try:
        filepath = os.path.join(os.getcwd(), filename)
        stat = os.stat(filepath)
        
        # Extract info from filename
        parts = filename.replace('.png', '').split('_')
        model = 'Unknown'
        timestamp = 'Unknown'
        
        if 'amazon' in filename:
            model = 'Amazon Titan Image Generator'
        elif 'stability' in filename:
            model = 'Stability AI SDXL'
        
        # Try to extract timestamp
        for part in parts:
            if len(part) == 8 and part.isdigit():  # Date part
                date_part = part
                time_part = parts[parts.index(part) + 1] if parts.index(part) + 1 < len(parts) else ''
                if len(time_part) == 6 and time_part.isdigit():
                    try:
                        dt = datetime.strptime(f"{date_part}_{time_part}", "%Y%m%d_%H%M%S")
                        timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass
                break
        
        return {
            'filename': filename,
            'model': model,
            'created': timestamp,
            'size': f"{stat.st_size:,} bytes",
            'prompt': 'Generated image'  # We'll try to extract this from a log file if available
        }
    except:
        return None

@app.route('/')
def index():
    """Main page showing the image gallery"""
    # Get all generated images
    image_files = glob.glob('generated_image_*.png')
    image_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)  # Sort by modification time, newest first
    
    images = []
    for filename in image_files:
        info = get_image_info(filename)
        if info:
            images.append(info)
    
    return render_template_string(HTML_TEMPLATE, images=images)

@app.route('/image/<filename>')
def serve_image(filename):
    """Serve generated images"""
    try:
        return send_file(filename)
    except:
        return "Image not found", 404

@app.route('/generate', methods=['POST'])
def generate_image():
    """Generate a new image"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        model = data.get('model', 'amazon.titan-image-generator-v1')
        
        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt is required'})
        
        # Run the image generation script
        cmd = ['python3', 'setup_stable_diffusion.py'] + prompt.split()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0 and 'Success!' in result.stdout:
            return jsonify({'success': True, 'message': 'Image generated successfully'})
        else:
            error_msg = result.stderr if result.stderr else result.stdout
            return jsonify({'success': False, 'error': error_msg})
            
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Image generation timed out'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🎨 Starting AWS Bedrock Image Generator Web Interface...")
    print("📍 Access the interface at: http://localhost:57798")
    print("🖼️  Generate images using Amazon Titan and Stable Diffusion models")
    print()
    
    app.run(host='0.0.0.0', port=57798, debug=True)

