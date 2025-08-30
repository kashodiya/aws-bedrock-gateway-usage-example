
#!/usr/bin/env python3

import boto3
import json

def call_claude_model(prompt, model_id="anthropic.claude-3-7-sonnet-20240620-v1:0", region="us-east-1"):
    """
    Call Claude 3.7 model through AWS Bedrock
    
    Args:
        prompt (str): The user prompt to send to Claude
        model_id (str): The model ID to use
        region (str): AWS region where Bedrock is available
        
    Returns:
        str: The model's response
    """
    # Create a Bedrock Runtime client
    bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
    
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
    Example of how to use AWS Bedrock to call Claude 3.7
    """
    print("AWS Bedrock Claude 3.7 Example")
    print("==============================")
    print("\nThis script demonstrates how to call Claude 3.7 through AWS Bedrock.")
    print("To use this script, you need:")
    print("1. AWS credentials with access to Bedrock")
    print("2. Access to Claude 3.7 model in your AWS account")
    print("3. Proper IAM permissions to invoke the model")
    
    print("\nExample code:")
    print("""
import boto3
import json

# Create a Bedrock Runtime client
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

# Prepare the request body
request_body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 4096,
    "messages": [
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ]
}

# Call the model
response = bedrock_runtime.invoke_model(
    modelId="anthropic.claude-3-7-sonnet-20240620-v1:0",
    body=json.dumps(request_body)
)

# Parse the response
response_body = json.loads(response['body'].read().decode('utf-8'))
print(response_body['content'][0]['text'])
    """)
    
    print("\nCommon model IDs for Claude:")
    print("- anthropic.claude-3-7-sonnet-20240620-v1:0")
    print("- anthropic.claude-3-5-sonnet-20240620-v1:0")
    print("- anthropic.claude-3-opus-20240229-v1:0")
    print("- anthropic.claude-3-sonnet-20240229-v1:0")
    print("- anthropic.claude-3-haiku-20240307-v1:0")
    
    print("\nNote: Model availability may vary by region and account permissions.")

if __name__ == "__main__":
    main()
