#!/bin/bash

# Script to install AWS CLI
# This script detects the package manager and installs AWS CLI accordingly

echo "AWS CLI Installation Script"
echo "=========================="

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to install AWS CLI using apt (Debian/Ubuntu)
install_with_apt() {
    echo "Installing AWS CLI using apt..."
    sudo apt-get update
    sudo apt-get install -y awscli
    echo "AWS CLI installed successfully using apt."
}

# Function to install AWS CLI using yum (RHEL/CentOS/Amazon Linux)
install_with_yum() {
    echo "Installing AWS CLI using yum..."
    sudo yum update -y
    sudo yum install -y awscli
    echo "AWS CLI installed successfully using yum."
}

# Function to install AWS CLI using dnf (Fedora/newer RHEL)
install_with_dnf() {
    echo "Installing AWS CLI using dnf..."
    sudo dnf update -y
    sudo dnf install -y awscli
    echo "AWS CLI installed successfully using dnf."
}

# Function to install AWS CLI using apk (Alpine Linux)
install_with_apk() {
    echo "Installing AWS CLI using apk..."
    sudo apk update
    sudo apk add aws-cli
    echo "AWS CLI installed successfully using apk."
}

# Function to install AWS CLI directly from AWS (for any Linux)
install_from_aws() {
    echo "Installing AWS CLI v2 directly from AWS..."
    
    # Install dependencies
    if command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install -y unzip curl
    elif command_exists yum; then
        sudo yum update -y
        sudo yum install -y unzip curl
    elif command_exists dnf; then
        sudo dnf update -y
        sudo dnf install -y unzip curl
    elif command_exists apk; then
        sudo apk update
        sudo apk add unzip curl
    else
        echo "Could not install dependencies. Please install unzip and curl manually."
        exit 1
    fi
    
    # Download and install AWS CLI v2
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    
    # Clean up
    rm -rf aws awscliv2.zip
    
    echo "AWS CLI v2 installed successfully from AWS."
}

# Check if AWS CLI is already installed
if command_exists aws; then
    echo "AWS CLI is already installed."
    aws --version
    exit 0
fi

# Detect package manager and install AWS CLI
if command_exists apt-get; then
    install_with_apt
elif command_exists yum; then
    install_with_yum
elif command_exists dnf; then
    install_with_dnf
elif command_exists apk; then
    install_with_apk
else
    echo "Could not detect package manager. Trying direct installation from AWS..."
    install_from_aws
fi

# Verify installation
if command_exists aws; then
    echo "AWS CLI installation verified:"
    aws --version
    echo "Installation completed successfully."
else
    echo "AWS CLI installation failed. Please try installing manually."
    exit 1
fi
