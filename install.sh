#!/bin/bash

# Update the system
echo "Updating system..."
sudo apt update && sudo apt upgrade -y

# Install necessary system packages
echo "Installing necessary system packages..."
sudo apt install -y python3 python3-pip python3-dev libsndfile1

# Upgrade pip in the system environment
echo "Upgrading pip..."
sudo pip3 install --upgrade pip

# Install dependencies for the Billy Bass project
echo "Installing dependencies..."

# List of required packages
REQUIRED_PACKAGES=(
    pygame
    RPi.GPIO
    whisper
    pydub
    librosa
)

# Install each package
for pkg in "${REQUIRED_PACKAGES[@]}"
do
    sudo pip3 install "$pkg" --break-system-packages
done

# Print completion message
echo "Installation complete. Billy Bass should now be ready to run!"
