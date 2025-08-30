#!/usr/bin/env python3

import boto3
import json
import sys
import base64
import os
from datetime import datetime

class StableDiffusionImageGenerator:
    def __init__(self, region='us-east-1'):
        self.region = region
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
        self.bedrock = boto3.client('bedrock', region_name=region)
        
    def list_available_models(self):
        """List all available foundation models in Bedrock"""
        try:
            response = self.bedrock.list_foundation_models()
            models = response.get('modelSummaries', [])
            
            print("=== Available Bedrock Models ===")
            image_models = []
            for model in models:
                if any(keyword in model['modelId'].lower() for keyword in ['stable', 'diffusion', 'image', 'titan']):
                    image_models.append(model)
                    print(f"Model ID: {model['modelId']}")
                    print(f"  Name: {model['modelName']}")
                    print(f"  Provider: {model['providerName']}")
                    print(f"  Input Modalities: {model.get('inputModalities', [])}")
                    print(f"  Output Modalities: {model.get('outputModalities', [])}")
                    print(f"  Inference Types: {model.get('inferenceTypesSupported', [])}")
                    print()
            
            return image_models
            
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def generate_image_stability_ai(self, prompt, model_id="stability.stable-diffusion-xl-v1:0"):
        """Generate image using Stability AI Stable Diffusion model"""
        try:
            # Request body for Stability AI models
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
                "height": 1024,
                "samples": 1
            }
            
            print(f"Generating image with Stability AI model: {model_id}")
            print(f"Prompt: {prompt}")
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json"
            )
            
            response_body = json.loads(response['body'].read().decode('utf-8'))
            return response_body
            
        except Exception as e:
            print(f"Error generating image with Stability AI: {e}")
            return None
    
    def generate_image_titan(self, prompt, model_id="amazon.titan-image-generator-v1"):
        """Generate image using Amazon Titan Image Generator"""
        try:
            # Request body for Titan Image Generator
            request_body = {
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {
                    "text": prompt,
                    "negativeText": "low quality, blurry, distorted"
                },
                "imageGenerationConfig": {
                    "numberOfImages": 1,
                    "height": 1024,
                    "width": 1024,
                    "cfgScale": 7.0,
                    "seed": 42
                }
            }
            
            print(f"Generating image with Titan model: {model_id}")
            print(f"Prompt: {prompt}")
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json"
            )
            
            response_body = json.loads(response['body'].read().decode('utf-8'))
            return response_body
            
        except Exception as e:
            print(f"Error generating image with Titan: {e}")
            return None
    
    def save_image_from_base64(self, base64_data, filename):
        """Save base64 encoded image to file"""
        try:
            # Remove data URL prefix if present
            if base64_data.startswith('data:image'):
                base64_data = base64_data.split(',')[1]
            
            # Decode and save
            image_data = base64.b64decode(base64_data)
            
            with open(filename, 'wb') as f:
                f.write(image_data)
            
            print(f"✓ Image saved as: {filename}")
            return True
            
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    def generate_image(self, prompt):
        """Try to generate an image using available models"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # List of models to try with their respective generation functions
        models_to_try = [
            ("stabilityai.stable-diffusion-3-5-large", self.generate_image_stability_ai),
            ("stability.stable-diffusion-xl-v1:0", self.generate_image_stability_ai),
            ("amazon.titan-image-generator-v1", self.generate_image_titan),
        ]
        
        for model_id, generate_func in models_to_try:
            print(f"\n--- Attempting with {model_id} ---")
            
            result = generate_func(prompt, model_id)
            
            if result:
                # Handle Stability AI response format
                if 'artifacts' in result:
                    for i, artifact in enumerate(result['artifacts']):
                        if 'base64' in artifact:
                            filename = f"generated_image_{model_id.replace(':', '_').replace('.', '_')}_{timestamp}_{i}.png"
                            if self.save_image_from_base64(artifact['base64'], filename):
                                return filename
                
                # Handle Titan response format
                elif 'images' in result:
                    for i, image_data in enumerate(result['images']):
                        filename = f"generated_image_{model_id.replace(':', '_').replace('.', '_')}_{timestamp}_{i}.png"
                        if self.save_image_from_base64(image_data, filename):
                            return filename
        
        return None

def print_setup_instructions():
    """Print instructions for setting up Stable Diffusion models"""
    print("""
=== Setup Instructions for Stable Diffusion Models ===

To use Stable Diffusion models with AWS Bedrock, you need to:

1. **Enable Model Access in AWS Console:**
   - Go to AWS Bedrock console: https://console.aws.amazon.com/bedrock/
   - Navigate to "Model access" in the left sidebar
   - Request access to Stability AI models:
     * stability.stable-diffusion-xl-v1:0
     * stabilityai.stable-diffusion-3-5-large (if available)
   - Request access to Amazon Titan Image Generator:
     * amazon.titan-image-generator-v1

2. **Check Regional Availability:**
   - Stable Diffusion models are available in limited regions
   - Try these regions: us-east-1, us-west-2, eu-west-1
   - Update your AWS region in the script if needed

3. **IAM Permissions:**
   Ensure your AWS credentials have these permissions:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "bedrock:InvokeModel",
                   "bedrock:ListFoundationModels"
               ],
               "Resource": "*"
           }
       ]
   }
   ```

4. **Provisioned Throughput (if required):**
   - Some models may require provisioned throughput
   - Check the Bedrock console for throughput requirements
   - Purchase provisioned throughput if needed

5. **Test Different Regions:**
   - Try running this script with different AWS regions
   - Use: python3 setup_stable_diffusion.py --region us-west-2

""")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate images using Stable Diffusion via AWS Bedrock')
    parser.add_argument('prompt', nargs='*', default=['A beautiful landscape with mountains and a lake, digital art style'], 
                       help='Text prompt for image generation')
    parser.add_argument('--region', default='us-east-1', help='AWS region to use')
    parser.add_argument('--list-models', action='store_true', help='List available models')
    parser.add_argument('--setup-help', action='store_true', help='Show setup instructions')
    
    args = parser.parse_args()
    
    if args.setup_help:
        print_setup_instructions()
        return
    
    # Initialize the generator
    generator = StableDiffusionImageGenerator(region=args.region)
    
    if args.list_models:
        generator.list_available_models()
        return
    
    # Generate image
    prompt = ' '.join(args.prompt)
    print(f"=== Stable Diffusion Image Generator ===")
    print(f"Region: {args.region}")
    print(f"Prompt: {prompt}")
    print()
    
    filename = generator.generate_image(prompt)
    
    if filename:
        print(f"\n🎉 Success! Image generated and saved as: {filename}")
        
        # Try to display image info
        try:
            import os
            size = os.path.getsize(filename)
            print(f"File size: {size:,} bytes")
        except:
            pass
            
    else:
        print(f"\n❌ Failed to generate image.")
        print(f"\nTroubleshooting steps:")
        print(f"1. Run with --setup-help to see setup instructions")
        print(f"2. Run with --list-models to see available models")
        print(f"3. Try a different region with --region us-west-2")
        print(f"4. Check AWS Bedrock console for model access")

if __name__ == "__main__":
    main()
