#!/usr/bin/env python3

import requests
import json
import sys
import base64
import os
from datetime import datetime

def generate_image_via_gateway(prompt, model_id="stabilityai.stable-diffusion-xl-v1", width=1024, height=1024):
    """Generate an image using Stable Diffusion through the Bedrock Access Gateway"""
    api_key = "bedrock"  # Default API key for the gateway
    api_base_url = "http://localhost:50399/api/v1"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Try the OpenAI-compatible images endpoint first
    data = {
        "model": model_id,
        "prompt": prompt,
        "n": 1,
        "size": f"{width}x{height}",
        "response_format": "b64_json"
    }
    
    try:
        print(f"Attempting to generate image with model: {model_id}")
        print(f"Prompt: {prompt}")
        
        response = requests.post(
            f"{api_base_url}/images/generations",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error calling image generation API: {e}")
        return None

def generate_image_direct_bedrock(prompt, model_id="stabilityai.stable-diffusion-3-5-large"):
    """Generate an image using direct Bedrock API call"""
    import boto3
    
    try:
        # Create a Bedrock Runtime client
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Prepare the request body for Stable Diffusion
        request_body = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1.0
                }
            ],
            "cfg_scale": 7,
            "seed": 0,
            "steps": 30,
            "width": 1024,
            "height": 1024
        }
        
        print(f"Attempting direct Bedrock call with model: {model_id}")
        print(f"Prompt: {prompt}")
        
        # Call the model
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )
        
        # Parse the response
        response_body = json.loads(response['body'].read().decode('utf-8'))
        return response_body
        
    except Exception as e:
        print(f"Error with direct Bedrock call: {e}")
        return None

def save_image_from_base64(base64_data, filename):
    """Save a base64 encoded image to a file"""
    try:
        # Remove data URL prefix if present
        if base64_data.startswith('data:image'):
            base64_data = base64_data.split(',')[1]
        
        # Decode base64 data
        image_data = base64.b64decode(base64_data)
        
        # Save to file
        with open(filename, 'wb') as f:
            f.write(image_data)
        
        print(f"Image saved as: {filename}")
        return True
        
    except Exception as e:
        print(f"Error saving image: {e}")
        return False

def main():
    # Get user prompt
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "A beautiful sunset over a mountain landscape, digital art style"
    
    print("=== Stable Diffusion Image Generator ===")
    print(f"Generating image for prompt: '{prompt}'")
    print()
    
    # List of model IDs to try
    model_ids_to_try = [
        "stabilityai.stable-diffusion-3-5-large",
        "stabilityai.stable-diffusion-xl-v1",
        "stability.stable-diffusion-xl-v1:0",
        "amazon.titan-image-generator-v1"
    ]
    
    success = False
    
    # Try each model ID
    for model_id in model_ids_to_try:
        print(f"\n--- Trying model: {model_id} ---")
        
        # Try via gateway first
        result = generate_image_via_gateway(prompt, model_id)
        
        if result and 'data' in result:
            # Handle OpenAI-style response
            for i, image_data in enumerate(result['data']):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_image_{timestamp}_{i}.png"
                
                if 'b64_json' in image_data:
                    if save_image_from_base64(image_data['b64_json'], filename):
                        success = True
                        print(f"✓ Successfully generated image using {model_id}")
                        break
        
        if success:
            break
        
        # Try direct Bedrock API if gateway fails
        print(f"Gateway failed, trying direct Bedrock API...")
        result = generate_image_direct_bedrock(prompt, model_id)
        
        if result and 'artifacts' in result:
            # Handle Stability AI response format
            for i, artifact in enumerate(result['artifacts']):
                if 'base64' in artifact:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"generated_image_{timestamp}_{i}.png"
                    
                    if save_image_from_base64(artifact['base64'], filename):
                        success = True
                        print(f"✓ Successfully generated image using {model_id}")
                        break
        
        if success:
            break
    
    if not success:
        print("\n❌ Failed to generate image with any available model.")
        print("\nPossible solutions:")
        print("1. Check if Stable Diffusion models are enabled in your AWS Bedrock console")
        print("2. Verify your AWS region supports the requested models")
        print("3. Ensure you have proper IAM permissions for Bedrock image generation")
        print("4. Try a different model ID")
        
        # Show available models
        print("\nAvailable models from gateway:")
        try:
            response = requests.get(
                "http://localhost:50399/api/v1/models",
                headers={"Authorization": "Bearer bedrock"}
            )
            if response.status_code == 200:
                models = response.json()
                for model in models.get('data', []):
                    if 'stable' in model['id'].lower() or 'image' in model['id'].lower() or 'titan' in model['id'].lower():
                        print(f"  - {model['id']}")
        except:
            pass
    else:
        print(f"\n🎉 Image generation completed successfully!")
        print(f"Check the current directory for the generated image file.")

if __name__ == "__main__":
    main()
