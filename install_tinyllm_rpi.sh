#!/bin/bash

# TinyLLM Setup Script for Raspberry Pi
# This script installs Ollama and configures TinyLlama for ARM hardware

echo "🍓 Setting up TinyLLM for Raspberry Pi..."

# Check if running on ARM64
ARCH=$(uname -m)
echo "Architecture: $ARCH"

if [[ "$ARCH" != "aarch64" && "$ARCH" != "arm64" ]]; then
    echo "⚠️  Warning: This script is optimized for ARM64 Raspberry Pi"
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install required dependencies
echo "🔧 Installing dependencies..."
sudo apt install -y curl wget git python3-pip

# Install Python dependencies for the serial client
echo "🐍 Installing Python dependencies..."
pip3 install -r requirements.txt

# Add user to dialout group for serial access
echo "👤 Adding user to dialout group for serial access..."
sudo usermod -a -G dialout $USER

# Install Ollama
echo "🚀 Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
echo "🔄 Starting Ollama service..."
sudo systemctl enable ollama
sudo systemctl start ollama

# Wait for Ollama to start
echo "⏳ Waiting for Ollama to start..."
sleep 5

# Pull TinyLlama model (optimized for resource-constrained devices)
echo "📥 Downloading TinyLlama model (this may take a while)..."
ollama pull tinyllama

# Test the installation
echo "🧪 Testing TinyLlama..."
echo "Response from TinyLlama:"
ollama run tinyllama "Hello, this is a test from Raspberry Pi" --verbose

echo ""
echo "✅ TinyLLM setup complete!"
echo ""
echo "Usage examples:"
echo "  ollama run tinyllama 'Your prompt here'"
echo "  curl http://localhost:11434/api/generate -d '{\"model\":\"tinyllama\",\"prompt\":\"Hello\"}'"
echo ""
echo "🔧 Next steps:"
echo "1. Test the integration: python3 test_ollama.py"
echo "2. Test serial connection: python3 main.py --config config/rpi_config.yaml --serial-test"
echo "3. Run production mode: python3 main.py --config config/rpi_config.yaml"
echo ""
echo "⚠️  Note: You may need to logout/login for dialout group changes to take effect"