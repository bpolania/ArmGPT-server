# 🍓 TinyLLM Serial Client - Raspberry Pi Setup Guide

Complete setup guide for running the TinyLLM Serial Client on Raspberry Pi with Ollama.

## 📋 Prerequisites

- **Raspberry Pi 4** (8GB RAM recommended, 4GB minimum)
- **64-bit Raspberry Pi OS** (required for Ollama)
- **USB-to-USB serial cable** for Pi-to-Pi communication
- **Internet connection** for initial setup

## 🚀 Quick Setup

### Step 1: Install TinyLLM (Ollama)

```bash
# Copy the project to your Raspberry Pi
scp -r ArmGPT-server/ pi@your-pi-ip:~/

# SSH to your Pi
ssh pi@your-pi-ip

# Run the installation script
cd ~/ArmGPT-server
./install_tinyllm_rpi.sh
```

### Step 2: Verify Installation

```bash
# Check Ollama service
sudo systemctl status ollama

# Test TinyLlama model
ollama run tinyllama "Hello from Raspberry Pi"

# Run integration test
python3 test_ollama.py
```

### Step 3: Test the Client

```bash
# Test with simulated messages
python3 main.py --config config/rpi_config.yaml --test-mode

# Test serial reception only
python3 main.py --config config/rpi_config.yaml --serial-test

# Run in production mode
python3 main.py --config config/rpi_config.yaml
```

## 🔧 Detailed Setup Instructions

### System Requirements Check

```bash
# Check architecture (should be aarch64 or arm64)
uname -m

# Check available memory (4GB+ recommended)
free -h

# Check disk space (10GB+ free recommended)
df -h

# Check OS version (64-bit required)
cat /etc/os-release
```

### Manual Ollama Installation

If the automatic script fails:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y curl wget git python3-pip

# Install Ollama manually
curl -fsSL https://ollama.ai/install.sh | sh

# Start and enable service
sudo systemctl enable ollama
sudo systemctl start ollama

# Pull TinyLlama model (this may take 10-30 minutes)
ollama pull tinyllama

# Test installation
ollama run tinyllama "Test message"
```

### Python Dependencies

```bash
cd ~/ArmGPT-server

# Install Python packages
pip3 install -r requirements.txt

# Add user to dialout group for serial access
sudo usermod -a -G dialout $USER

# Logout and login again for group changes to take effect
```

## 📡 Serial Port Configuration

### Find Your Serial Device

```bash
# List USB devices
lsusb

# List serial devices
ls -la /dev/ttyUSB* /dev/ttyACM*

# Test serial port (if ARM sender is connected)
sudo screen /dev/ttyUSB0 9600
# Press Ctrl+A then K to exit screen
```

### Update Configuration

Edit `config/rpi_config.yaml`:

```yaml
serial:
  port: "/dev/ttyUSB0"  # Update if your device is different
  baudrate: 9600
```

## 🧪 Testing and Validation

### 1. Test Ollama Directly

```bash
# Test API endpoint
curl http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tinyllama",
    "prompt": "Hello from Raspberry Pi",
    "stream": false
  }'
```

### 2. Test Python Integration

```bash
# Run comprehensive test
python3 test_ollama.py

# Expected output:
# ✅ Ollama is running
# ✅ TinyLlama model found
# ✅ Generated response: Hello! ...
# ✅ All tests passed!
```

### 3. Test Serial Client Components

```bash
# Test message processing only
python3 -c "
import sys, os
sys.path.insert(0, 'src')
from message_processor import MessageProcessor
p = MessageProcessor()
result = p.process('TEST MESSAGE FROM ACORN SYSTEM')
print('✅ Message processed:', result['cleaned'] if result else 'Failed')
"
```

## 🔍 Troubleshooting

### Ollama Issues

**Problem**: `ollama: command not found`
```bash
# Check if Ollama is in PATH
which ollama

# If not found, try manual installation
export PATH=$PATH:/usr/local/bin
echo 'export PATH=$PATH:/usr/local/bin' >> ~/.bashrc
```

**Problem**: `model 'tinyllama' not found`
```bash
# Pull the model
ollama pull tinyllama

# List available models
ollama list

# If pull fails, try smaller model
ollama pull tinyllama:1.1b-chat-q4_0
```

**Problem**: `connection refused`
```bash
# Check Ollama service
sudo systemctl status ollama
sudo systemctl restart ollama

# Check if port is open
netstat -tlnp | grep 11434

# Check logs
sudo journalctl -u ollama -f
```

### Serial Port Issues

**Problem**: `Permission denied: '/dev/ttyUSB0'`
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Or run with sudo temporarily
sudo python3 main.py --config config/rpi_config.yaml --serial-test
```

**Problem**: `No such file or directory: '/dev/ttyUSB0'`
```bash
# Check connected devices
dmesg | grep tty
lsusb

# Try different device
python3 main.py --port /dev/ttyACM0 --serial-test
```

### Performance Issues

**Problem**: Slow responses or timeouts
```bash
# Check system resources
htop

# Check temperature
vcgencmd measure_temp

# Increase timeout in config
# Edit config/rpi_config.yaml:
tinyllm:
  timeout: 120  # Increase from 60
```

**Problem**: Out of memory
```bash
# Check memory usage
free -h

# Enable swap if needed
sudo dphys-swapfile swapoff
sudo dphys-swapfile swapon

# Use smaller model responses
# Edit config/rpi_config.yaml:
tinyllm:
  max_tokens: 25  # Reduce from 50
```

## 📊 Performance Optimization

### Raspberry Pi 4 Recommended Settings

```yaml
# config/rpi_config.yaml optimizations
tinyllm:
  timeout: 60
  max_tokens: 50
  temperature: 0.7
  
client:
  max_message_length: 256
  buffer_size: 2048
  
logging:
  level: "INFO"  # Use INFO in production
  file_level: "WARNING"  # Reduce file logging
```

### Raspberry Pi 3 Settings (Limited Memory)

```yaml
tinyllm:
  timeout: 120
  max_tokens: 25
  max_retries: 2
  
client:
  max_message_length: 128
  buffer_size: 1024
```

### System Optimization

```bash
# Increase GPU memory split for better performance
sudo raspi-config
# Advanced Options > Memory Split > 128

# Enable hardware acceleration
echo 'gpu_mem=128' | sudo tee -a /boot/config.txt

# Reboot after changes
sudo reboot
```

## 🚀 Production Deployment

### Auto-start Service

Create systemd service:

```bash
sudo tee /etc/systemd/system/tinyllm-serial.service << EOF
[Unit]
Description=TinyLLM Serial Client
After=network.target ollama.service
Requires=ollama.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/ArmGPT-server
ExecStart=/usr/bin/python3 main.py --config config/rpi_config.yaml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable tinyllm-serial.service
sudo systemctl start tinyllm-serial.service

# Check status
sudo systemctl status tinyllm-serial.service
```

### Monitoring

```bash
# View real-time logs
sudo journalctl -u tinyllm-serial -f

# Check system resources
watch -n 1 "free -h && echo && vcgencmd measure_temp"

# Monitor serial client logs
tail -f logs/serial_client.log
```

## 📈 Expected Performance

### Raspberry Pi 4 (8GB)
- **Response time**: 2-8 seconds
- **Memory usage**: 1-2GB
- **CPU usage**: 20-60% during generation

### Raspberry Pi 4 (4GB)
- **Response time**: 5-15 seconds  
- **Memory usage**: 2-3GB
- **CPU usage**: 40-80% during generation

### Success Metrics
- ✅ Serial messages received and processed
- ✅ LLM responses generated within timeout
- ✅ No memory or connection errors
- ✅ Stable operation for hours/days

## 🔗 Integration with ARM Assembly Sender

The client is fully compatible with your ARM assembly sender:

1. **Same serial settings**: 9600 baud, `/dev/ttyUSB0`
2. **Same message format**: ASCII text with `\n` terminators  
3. **Handles all message types**: Test, custom, continuous
4. **Maintains bash tool compatibility**

## 🆘 Getting Help

If you encounter issues:

1. Run the test script: `python3 test_ollama.py`
2. Check the logs: `tail logs/serial_client.log`
3. Verify Ollama: `ollama list` and `ollama run tinyllama "test"`
4. Test serial: `python3 main.py --serial-test`

The client provides detailed error messages and suggestions for common issues.

---

## ✅ Quick Verification Checklist

- [ ] Raspberry Pi OS 64-bit installed
- [ ] Ollama service running (`sudo systemctl status ollama`)
- [ ] TinyLlama model downloaded (`ollama list`)
- [ ] Python dependencies installed (`pip3 list | grep -E "(serial|colorama|yaml|requests)"`)
- [ ] User in dialout group (`groups | grep dialout`)
- [ ] Serial device accessible (`ls /dev/ttyUSB*`)
- [ ] Test script passes (`python3 test_ollama.py`)
- [ ] Client starts successfully (`python3 main.py --test-mode`)

Once all items are checked, your Raspberry Pi is ready to receive prompts via serial and process them with TinyLLM! 🎉