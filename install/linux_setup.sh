#!/bin/bash

echo "Installing AI Surveillance System..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for root privileges
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root or with sudo"
    exit 1
fi

# Check Python version
REQUIRED_PYTHON="3.8"
if command_exists python3; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if (( $(echo "$PYTHON_VERSION < $REQUIRED_PYTHON" | bc -l) )); then
        echo "Python version $REQUIRED_PYTHON or higher is required"
        exit 1
    fi
else
    echo "Python 3 is not installed"
    exit 1
fi

# Install system dependencies
if command_exists apt-get; then
    echo "Detected Debian/Ubuntu system..."
    apt-get update
    apt-get install -y python3 python3-pip python3-venv libgl1-mesa-glx libglib2.0-0 \
                      libsm6 libxext6 libxrender-dev libgstreamer1.0-0 \
                      gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
                      gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly
elif command_exists yum; then
    echo "Detected RHEL/CentOS system..."
    yum update -y
    yum install -y python3 python3-pip python3-devel mesa-libGL glib2 \
                   libSM libXext libXrender gstreamer1 gstreamer1-plugins-base \
                   gstreamer1-plugins-good gstreamer1-plugins-bad-free
elif command_exists pacman; then
    echo "Detected Arch Linux system..."
    pacman -Syu --noconfirm
    pacman -S --noconfirm python python-pip mesa glib2 \
              libsm libxext libxrender gstreamer gst-plugins-base \
              gst-plugins-good gst-plugins-bad
else
    echo "Unsupported package manager. Please install dependencies manually."
    exit 1
fi

# Check disk space
MIN_SPACE_MB=1000
AVAILABLE_SPACE_MB=$(df -m . | awk 'NR==2 {print $4}')
if [ "$AVAILABLE_SPACE_MB" -lt "$MIN_SPACE_MB" ]; then
    echo "Insufficient disk space. Need at least ${MIN_SPACE_MB}MB"
    exit 1
fi

# Create and setup project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR" || exit 1

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify pip is available
if ! command_exists pip; then
    echo "pip not found in virtual environment"
    exit 1
fi

# Install packages from local directory
echo "Installing dependencies..."
if [ -d "install/packages" ]; then
    pip install --no-index --find-links=install/packages -r requirements.txt
else
    echo "Package directory not found!"
    exit 1
fi

# Create necessary directories
echo "Creating project directories..."
mkdir -p recordings models logs

# Set permissions
chmod 755 recordings models logs

# Copy AI models if they exist
if [ -d "install/dependencies/models" ]; then
    echo "Copying AI models..."
    cp -r install/dependencies/models/* models/
fi

# Create test file to verify write permissions
if ! touch recordings/test.txt 2>/dev/null; then
    echo "Warning: Cannot write to recordings directory"
fi
rm -f recordings/test.txt

echo "Installation complete!"
echo "To start the system:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the application: python3 src/main.py"

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "Setup completed successfully!"
else
    echo "Setup failed! Please check the error messages above."
    exit 1
fi
