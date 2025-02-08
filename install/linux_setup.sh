#!/bin/bash

echo "Installing AI Surveillance System..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install system dependencies
if command_exists apt-get; then
    echo "Detected Debian/Ubuntu system..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv libgl1-mesa-glx libglib2.0-0
elif command_exists yum; then
    echo "Detected RHEL/CentOS system..."
    sudo yum update -y
    sudo yum install -y python3 python3-pip python3-devel mesa-libGL glib2
elif command_exists pacman; then
    echo "Detected Arch Linux system..."
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm python python-pip mesa glib2
else
    echo "Unsupported package manager. Please install Python 3 and required dependencies manually."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv ../venv

# Activate virtual environment
source ../venv/bin/activate

# Install packages from local directory
echo "Installing dependencies..."
pip install --no-index --find-links=packages -r ../requirements.txt

# Create necessary directories
mkdir -p ../recordings
mkdir -p ../models

# Copy AI models if they exist
if [ -d "dependencies/models" ]; then
    echo "Copying AI models..."
    cp -r dependencies/models/* ../models/
fi

echo "Setup complete! Run 'python3 src/main.py' to start the system."
