
#!/usr/bin/env python3

import boto3
import json
import sys

def call_claude_model(prompt, model_id="anthropic.claude-3-7-sonnet-20240620-v1:0"):
    """
    Call Claude 3.7 model through AWS Bedrock
    
    Args:
        prompt (str): The user prompt to send to Claude
        model_id (str): The model ID to use
        
    Returns:
        str: The model's response
    """
    # Create a Bedrock Runtime client with a specific region
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    # Prepare the request body for Claude 3.7
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        # Call the model
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        # Parse the response
        response_body = json.loads(response['body'].read().decode('utf-8'))
        return response_body['content'][0]['text']
        
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
