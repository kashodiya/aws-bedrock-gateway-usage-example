# AWS CLI and Claude 3.7 Integration Guide

This repository contains scripts and examples for working with AWS CLI and Claude 3.7 through AWS Bedrock.

## Contents

1. [Quick Start](#quick-start)
2. [AWS CLI Installation](#aws-cli-installation)
3. [Bedrock Access Gateway Installation](#bedrock-access-gateway-installation)
4. [S3 Bucket Operations](#s3-bucket-operations)
5. [Claude 3.7 Integration](#claude-37-integration)
6. [Bedrock Access Gateway Usage](#bedrock-access-gateway-usage)

## Quick Start

### Install AWS CLI
```bash
# Make the script executable and run
chmod +x install_aws_cli.sh
./install_aws_cli.sh
```

### Install and Run Bedrock Access Gateway
```bash
# Make the script executable and run
chmod +x install_run_bedrock_gateway.sh
./install_run_bedrock_gateway.sh
```

This will:
- Check AWS credentials
- Install Python dependencies
- Clone the Bedrock Access Gateway repository
- Create a test script
- Run the gateway on port 8000

## AWS CLI Installation

The `install_aws_cli.sh` script provides an automated way to install AWS CLI on various Linux distributions:

```bash
# Make the script executable
chmod +x install_aws_cli.sh

# Run the script
./install_aws_cli.sh
```

The script automatically detects your package manager (apt, yum, dnf, or apk) and installs AWS CLI accordingly. If no package manager is detected, it falls back to installing AWS CLI directly from AWS's official source.

## Bedrock Access Gateway Installation

The `install_run_bedrock_gateway.sh` script provides a comprehensive solution for installing and running the AWS Bedrock Access Gateway:

### Features

- **Automated Installation**: Installs all required Python dependencies
- **Repository Management**: Clones or updates the Bedrock Access Gateway repository
- **AWS Credential Check**: Verifies AWS credentials and offers to configure them
- **Multiple Run Modes**: Run in foreground, background, or install-only mode
- **Test Script Creation**: Automatically creates a test script to verify the gateway
- **Port Configuration**: Allows custom port specification

### Usage Options

```bash
# Install and run the gateway (interactive mode)
./install_run_bedrock_gateway.sh

# Install dependencies only (don't run the gateway)
./install_run_bedrock_gateway.sh --install-only

# Run the gateway in the background
./install_run_bedrock_gateway.sh --background

# Run on a custom port
./install_run_bedrock_gateway.sh --port 8080

# Run only (skip installation)
./install_run_bedrock_gateway.sh --run-only

# Show help
./install_run_bedrock_gateway.sh --help
```

### What the Script Does

1. **Checks AWS Credentials**: Verifies that AWS CLI is installed and credentials are configured
2. **Installs Dependencies**: Installs required Python packages (FastAPI, uvicorn, boto3, etc.)
3. **Clones Repository**: Downloads the latest Bedrock Access Gateway from GitHub
4. **Creates Test Script**: Generates `test_bedrock_gateway.py` for testing the gateway
5. **Runs Gateway**: Starts the gateway server on the specified port (default: 8000)

### Testing the Gateway

After installation, you can test the gateway using the generated test script:

```bash
# Test with default prompt
python3 test_bedrock_gateway.py

# Test with custom prompt
python3 test_bedrock_gateway.py "What is the capital of France?"
```

## S3 Bucket Operations

### Using AWS CLI

List S3 buckets:

```bash
aws s3 ls
```

### Using Python (boto3)

The `list_s3_buckets.py` script demonstrates how to list S3 buckets using boto3:

```bash
python3 list_s3_buckets.py
```

## Claude 3.7 Integration

### Direct AWS Bedrock Integration

The `claude_bedrock_example.py` script provides an example of how to call Claude 3.7 through AWS Bedrock:

```bash
python3 claude_bedrock_example.py
```

To use this script in production, you need:
1. AWS credentials with access to Bedrock
2. Access to Claude 3.7 model in your AWS account
3. Proper IAM permissions to invoke the model

Example code for calling Claude 3.7:

```python
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
```

Common model IDs for Claude:
- anthropic.claude-3-7-sonnet-20240620-v1:0
- anthropic.claude-3-5-sonnet-20240620-v1:0
- anthropic.claude-3-opus-20240229-v1:0
- anthropic.claude-3-sonnet-20240229-v1:0
- anthropic.claude-3-haiku-20240307-v1:0

## Bedrock Access Gateway Usage

The [Bedrock Access Gateway](https://github.com/aws-samples/bedrock-access-gateway) provides OpenAI-compatible RESTful APIs for Amazon Bedrock, allowing you to use OpenAI SDKs and tools with Amazon Bedrock models.

### Automated Setup

Use the `install_run_bedrock_gateway.sh` script for automated installation and setup (see [Bedrock Access Gateway Installation](#bedrock-access-gateway-installation) section above).

### Manual Setup

If you prefer to set up manually:

```bash
cd bedrock-access-gateway/src
pip install -r requirements.txt
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```

The API base URL will be `http://localhost:8000/api/v1`.

### Using the Gateway

The `claude_gateway.py` script demonstrates how to call Claude models through the Bedrock Access Gateway:

```bash
python3 claude_gateway.py "What is the capital of France?"
```

This script:
1. Gets a list of available models from the gateway
2. Finds a Claude model to use
3. Sends the prompt to the model
4. Returns the response

### OpenAI SDK Compatibility

You can use the gateway with the OpenAI SDK:

```python
from openai import OpenAI

# Configure the client to use the Bedrock Access Gateway
client = OpenAI(
    api_key="bedrock",  # Default API key for the gateway
    base_url="http://localhost:8000/api/v1"
)

# Use any Claude model available in your AWS account
response = client.chat.completions.create(
    model="anthropic.claude-3-5-sonnet-20240620-v1:0",
    messages=[
        {"role": "user", "content": "Hello, Claude!"}
    ]
)

print(response.choices[0].message.content)
```

## AWS Configuration

Before using these scripts, configure your AWS credentials:

```bash
aws configure
```

You'll need to provide:
- AWS Access Key ID
- AWS Secret Access Key
- Default region name (e.g., us-east-1)
- Default output format (e.g., json)

If you're running on an EC2 instance with an IAM role, credentials will be automatically available.
