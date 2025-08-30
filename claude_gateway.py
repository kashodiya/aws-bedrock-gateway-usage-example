
#!/usr/bin/env python3

import os
import requests
import json
import sys

def get_available_models():
    """
    Get a list of available models from the Bedrock Access Gateway
    
    Returns:
        list: List of available model IDs
    """
    api_key = "bedrock"
    api_base_url = "http://localhost:8000/api/v1"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.get(
            f"{api_base_url}/models",
            headers=headers
        )
        
        if response.status_code == 200:
            models_data = response.json()
            return [model["id"] for model in models_data.get("data", [])]
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"Error getting models: {e}")
        return []

def call_claude_model(prompt, model_id=None):
    """
    Call Claude 3.7 model through Bedrock Access Gateway
    
    Args:
        prompt (str): The user prompt to send to Claude
        model_id (str): The model ID to use. If None, will use the first available Claude model
        
    Returns:
        str: The model's response
    """
    # If no model_id is provided, get available models and find a Claude model
    if model_id is None:
        models = get_available_models()
        claude_models = [model for model in models if "claude" in model.lower()]
        
        if claude_models:
            model_id = claude_models[0]
            print(f"Using model: {model_id}")
        else:
            print("No Claude models available. Available models:")
            for model in models:
                print(f"- {model}")
            return None
    # API settings
    api_key = "bedrock"  # Default API key for Bedrock Access Gateway
    api_base_url = "http://localhost:8000/api/v1"
    
    # Prepare the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model_id,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 4096
    }
    
    try:
        # Make the API call
        response = requests.post(
            f"{api_base_url}/chat/completions",
            headers=headers,
            json=data
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
    except Exception as e:
        print(f"Error calling Claude model: {e}")
        return None

def main():
    """
    Main function to demonstrate calling Claude 3.7 model
    """
    # Check if a prompt was provided as a command-line argument
    if len(sys.argv) > 1:
        prompt = ' '.join(sys.argv[1:])
    else:
        prompt = "What are the three laws of robotics?"
    
    print(f"Sending prompt to Claude 3.7: '{prompt}'")
    print("\nWaiting for response...\n")
    
    # Call the model
    response = call_claude_model(prompt)
    
    if response:
        print("Claude's response:")
        print("-" * 50)
        print(response)
        print("-" * 50)
    else:
        print("Failed to get a response from Claude.")

if __name__ == "__main__":
    main()
