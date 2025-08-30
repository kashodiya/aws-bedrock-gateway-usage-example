#!/bin/bash

# Script to install and run AWS Bedrock Access Gateway
# This script automates the process of setting up and running the Bedrock Access Gateway
# which provides OpenAI-compatible APIs for Amazon Bedrock models

set -e  # Exit immediately if a command exits with a non-zero status

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Function to print section headers
print_section() {
    echo -e "\n${BOLD}${BLUE}$1${NC}"
    echo -e "${BLUE}$(printf '=%.0s' {1..50})${NC}\n"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check AWS credentials
check_aws_credentials() {
    print_section "Checking AWS Credentials"
    
    if ! command_exists aws; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if AWS credentials are configured
    if ! aws sts get-caller-identity &>/dev/null; then
        print_warning "AWS credentials not found or not valid."
        print_warning "You will need valid AWS credentials with Bedrock access to use the gateway."
        
        # Ask if user wants to configure AWS credentials now
        read -p "Do you want to configure AWS credentials now? (y/n): " configure_aws
        if [[ $configure_aws == "y" || $configure_aws == "Y" ]]; then
            aws configure
        else
            print_warning "Proceeding without configuring AWS credentials."
            print_warning "You'll need to configure them later to use Bedrock models."
        fi
    else
        print_success "AWS credentials are configured."
        
        # Display account info
        account_info=$(aws sts get-caller-identity --query "Account" --output text)
        echo -e "Using AWS Account: ${BOLD}$account_info${NC}"
    fi
}

# Function to install Python dependencies
install_dependencies() {
    print_section "Installing Python Dependencies"
    
    # Check if pip is installed
    if ! command_exists pip || ! command_exists pip3; then
        print_error "pip is not installed. Please install Python and pip first."
        exit 1
    fi
    
    # Use pip3 if available, otherwise use pip
    if command_exists pip3; then
        PIP_CMD="pip3"
    else
        PIP_CMD="pip"
    fi
    
    # Install required packages
    echo "Installing required Python packages..."
    $PIP_CMD install fastapi==0.115.8 pydantic==2.7.1 uvicorn==0.29.0 mangum==0.17.0 \
                   tiktoken==0.6.0 requests==2.32.4 numpy==1.26.4 boto3==1.40.4 botocore==1.40.4
    
    print_success "Dependencies installed successfully."
}

# Function to clone the Bedrock Access Gateway repository
clone_repository() {
    print_section "Cloning Bedrock Access Gateway Repository"
    
    # Check if git is installed
    if ! command_exists git; then
        print_error "git is not installed. Please install git first."
        exit 1
    fi
    
    # Define the repository directory
    REPO_DIR="bedrock-access-gateway"
    
    # Check if the repository already exists
    if [ -d "$REPO_DIR" ]; then
        echo "Repository already exists. Updating..."
        cd "$REPO_DIR"
        git pull
        cd ..
    else
        echo "Cloning repository..."
        git clone https://github.com/aws-samples/bedrock-access-gateway.git
    fi
    
    print_success "Repository is ready."
}

# Function to run the Bedrock Access Gateway
run_gateway() {
    print_section "Running Bedrock Access Gateway"
    
    # Define the port to run the gateway on
    PORT=${1:-8000}
    
    echo "Starting Bedrock Access Gateway on port $PORT..."
    echo "API base URL will be: http://localhost:$PORT/api/v1"
    
    # Change to the src directory
    cd bedrock-access-gateway/src
    
    # Run the gateway
    echo -e "\n${YELLOW}Press Ctrl+C to stop the gateway${NC}\n"
    python3 -m uvicorn api.app:app --host 0.0.0.0 --port $PORT
}

# Function to run the gateway in the background
run_gateway_background() {
    print_section "Running Bedrock Access Gateway in Background"
    
    # Define the port to run the gateway on
    PORT=${1:-8000}
    LOG_FILE="bedrock_gateway.log"
    
    echo "Starting Bedrock Access Gateway on port $PORT in the background..."
    echo "API base URL will be: http://localhost:$PORT/api/v1"
    echo "Logs will be written to $LOG_FILE"
    
    # Change to the src directory
    cd bedrock-access-gateway/src
    
    # Run the gateway in the background
    nohup python3 -m uvicorn api.app:app --host 0.0.0.0 --port $PORT > ../../$LOG_FILE 2>&1 &
    
    # Save the PID
    GATEWAY_PID=$!
    echo $GATEWAY_PID > ../../.gateway_pid
    
    print_success "Gateway is running in the background with PID: $GATEWAY_PID"
    echo "To stop the gateway, run: kill \$(cat .gateway_pid)"
}

# Function to create a test script
create_test_script() {
    print_section "Creating Test Script"
    
    # Define the test script path
    TEST_SCRIPT="test_bedrock_gateway.py"
    
    # Create the test script
    cat > $TEST_SCRIPT << 'EOF'
#!/usr/bin/env python3

import requests
import json
import sys
import os

def get_available_models():
    """Get available models from the Bedrock Access Gateway"""
    api_key = "bedrock"  # Default API key
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
            return response.json()
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error getting models: {e}")
        return None

def call_model(prompt, model_id):
    """Call a model through the Bedrock Access Gateway"""
    api_key = "bedrock"  # Default API key
    api_base_url = "http://localhost:8000/api/v1"
    
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
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(
            f"{api_base_url}/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error calling model: {e}")
        return None

def main():
    # Get available models
    print("Getting available models...")
    models_response = get_available_models()
    
    if not models_response:
        print("Failed to get models. Make sure the gateway is running.")
        sys.exit(1)
    
    # Print available models
    print("\nAvailable models:")
    models = models_response.get("data", [])
    for i, model in enumerate(models):
        print(f"{i+1}. {model['id']}")
    
    # Select a model
    if not models:
        print("No models available.")
        sys.exit(1)
    
    # Try to find a Claude model
    claude_models = [model for model in models if "claude" in model["id"].lower()]
    
    if claude_models:
        selected_model = claude_models[0]["id"]
        print(f"\nAutomatically selected Claude model: {selected_model}")
    else:
        # If no Claude model, use the first available model
        selected_model = models[0]["id"]
        print(f"\nNo Claude models available. Using: {selected_model}")
    
    # Get user prompt
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "What are the three laws of robotics?"
    
    print(f"\nSending prompt: '{prompt}'")
    
    # Call the model
    response = call_model(prompt, selected_model)
    
    if response:
        print("\nResponse:")
        print("-" * 50)
        print(response["choices"][0]["message"]["content"])
        print("-" * 50)
    else:
        print("Failed to get a response.")

if __name__ == "__main__":
    main()
EOF
    
    # Make the test script executable
    chmod +x $TEST_SCRIPT
    
    print_success "Test script created: $TEST_SCRIPT"
    echo "To test the gateway, run: python3 $TEST_SCRIPT \"Your prompt here\""
}

# Function to display usage information
show_usage() {
    print_section "Usage Information"
    
    echo -e "Usage: $0 [OPTION]"
    echo -e "Install and run AWS Bedrock Access Gateway\n"
    echo -e "Options:"
    echo -e "  --install-only    Install dependencies and clone repository, but don't run the gateway"
    echo -e "  --run-only        Run the gateway without installing dependencies"
    echo -e "  --background      Run the gateway in the background"
    echo -e "  --port PORT       Specify the port to run the gateway on (default: 8000)"
    echo -e "  --help            Display this help message and exit\n"
    echo -e "Examples:"
    echo -e "  $0                Install dependencies, clone repository, and run the gateway"
    echo -e "  $0 --background   Run the gateway in the background"
    echo -e "  $0 --port 8080    Run the gateway on port 8080"
}

# Main function
main() {
    # Parse command line arguments
    INSTALL=true
    RUN=true
    BACKGROUND=false
    PORT=8000
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --install-only)
                RUN=false
                shift
                ;;
            --run-only)
                INSTALL=false
                shift
                ;;
            --background)
                BACKGROUND=true
                shift
                ;;
            --port)
                PORT=$2
                shift 2
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Display banner
    echo -e "${BOLD}${BLUE}"
    echo "  ____           _                _      _____       _                         "
    echo " |  _ \         | |              | |    / ____|     | |                        "
    echo " | |_) | ___  __| |_ __ ___   ___| | __| |  __  __ _| |_ _____      ____ _ _   _ "
    echo " |  _ < / _ \/ _\` | '__/ _ \ / __| |/ /| | |_ |/ _\` | __/ _ \ \ /\ / / _\` | | | |"
    echo " | |_) |  __/ (_| | | | (_) | (__|   < | |__| | (_| | ||  __/\ V  V / (_| | |_| |"
    echo " |____/ \___|\__,_|_|  \___/ \___|_|\_\ \_____|\__,_|\__\___| \_/\_/ \__,_|\__, |"
    echo "                                                                             __/ |"
    echo "                                                                            |___/ "
    echo -e "${NC}"
    echo -e "${BOLD}AWS Bedrock Access Gateway Installer and Runner${NC}"
    echo -e "Provides OpenAI-compatible APIs for Amazon Bedrock models\n"
    
    # Check AWS credentials
    check_aws_credentials
    
    # Install dependencies and clone repository if needed
    if [ "$INSTALL" = true ]; then
        install_dependencies
        clone_repository
        create_test_script
    fi
    
    # Run the gateway if needed
    if [ "$RUN" = true ]; then
        if [ "$BACKGROUND" = true ]; then
            run_gateway_background $PORT
        else
            run_gateway $PORT
        fi
    fi
    
    # If only installing, show next steps
    if [ "$INSTALL" = true ] && [ "$RUN" = false ]; then
        print_section "Next Steps"
        echo "To run the gateway:"
        echo "  $0 --run-only"
        echo ""
        echo "To run the gateway in the background:"
        echo "  $0 --run-only --background"
        echo ""
        echo "To test the gateway:"
        echo "  python3 test_bedrock_gateway.py \"Your prompt here\""
    fi
}

# Run the main function
main "$@"
