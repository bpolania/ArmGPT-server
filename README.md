# ArmGPT-Server: TinyLLM Serial Client

**✅ FULLY TESTED AND WORKING** - A Python client that receives serial data from an ARM assembly program and forwards prompts to TinyLLM for AI processing on Raspberry Pi.

## 🎯 Overview

This client is part of a dual-Pi communication system where:
- **Sender Pi**: Runs ARM assembly program that sends messages via serial
- **Receiver Pi**: Runs this Python client to receive and process with AI

```
┌─────────────────┐    USB Serial   ┌─────────────────┐    TinyLLM      ┌─────────────────┐
│   SENDER PI     │     Cable       │   RECEIVER PI   │   Processing    │    TinyLLM      │
│                 │ ──────────────▶ │                 │ ──────────────▶ │                 │
│ ARM Assembly    │  /dev/ttyUSB0   │ Python Client   │                 │ AI Response     │
│ Program         │   9600 baud     │ (This Code)     │                 │ Generation      │
└─────────────────┘                 └─────────────────┘                 └─────────────────┘
```

## 🚀 Quick Start

### 1. Deploy to Raspberry Pi

```bash
# Copy project to your Pi
scp -r ArmGPT-server/ pi@your-pi-ip:~/

# SSH to Pi and install
ssh pi@your-pi-ip
cd ~/ArmGPT-server
./install_tinyllm_rpi.sh
```

### 2. Test and Verify

```bash
# Test Ollama integration
python3 test_ollama.py

# Test serial connection (with ARM sender connected)
python3 main.py --config config/rpi_config.yaml --serial-test

# Test full pipeline with simulated messages
python3 main.py --config config/rpi_config.yaml --test-mode
```

### 3. Run Production Mode

```bash
# Start receiving ARM assembly prompts and processing with AI
python3 main.py --config config/rpi_config.yaml
```

## ✅ **Confirmed Working Setup**

This implementation has been **successfully tested** on Raspberry Pi 4 with:
- ✅ **Ollama + TinyLlama** running on ARM64 CPU-only mode
- ✅ **Serial communication** at 9600 baud via USB cable
- ✅ **ARM assembly messages** received and processed
- ✅ **AI responses** generated in 3-8 seconds
- ✅ **Complete pipeline** functioning end-to-end

### Example Working Output
```
[03:54:59.307] INFO     SERIAL: Simulating message 1/3: "Hello from ARM assembly on Raspberry Pi"
[03:54:59.307] INFO     PROCESS: Cleaned message: "Hello from ARM assembly on Raspberry Pi"
[03:54:59.307] INFO     LLM: Forwarding to TinyLLM (attempt 1/5)...
[03:55:03.398] INFO     LLM: Response received (4.091s): "Certainly! Here's an example of how you can use the Arm assembly command in Raspberry Pi..."
[03:55:03.398] INFO     LLM: Processing complete
```

## 📡 Supported Message Types

The client processes these message types from the ARM assembly sender:

### Test Messages
```
TEST MESSAGE FROM ACORN SYSTEM
```

### Custom Messages
```
[User input up to 255 characters]
```

### Continuous Data
```
TEST MESSAGE FROM ACORN SYSTEM
TEST MESSAGE FROM ACORN SYSTEM
[...repeats with timing delays]
```

## 🔧 Configuration

### Serial Configuration
```yaml
serial:
  port: "/dev/ttyUSB0"        # Serial device path
  baudrate: 9600              # Must match ARM sender
  timeout: 1                  # Read timeout in seconds
  reconnect_attempts: 5       # Auto-reconnection attempts
  reconnect_delay: 2          # Delay between reconnect attempts
```

### TinyLLM Configuration (Ollama)
```yaml
tinyllm:
  interface_type: "api"       # Using Ollama API
  api_endpoint: "http://localhost:11434/api/generate"
  model: "tinyllama"          # Ollama model name
  timeout: 60                 # Increased for Raspberry Pi
  max_retries: 3              # Retry attempts for failed requests
  retry_delay: 3              # Delay between retries
  max_tokens: 100             # Limit response length for performance
  temperature: 0.7
```

### Logging Configuration
```yaml
logging:
  level: "INFO"               # Console log level
  file_level: "DEBUG"         # File log level  
  file: "logs/serial_client.log"
  console: true               # Enable colored console output
```

## 🎨 Features

### Real-time Serial Communication
- ✅ 9600 baud USB serial communication
- ✅ Automatic device detection and reconnection
- ✅ Robust error handling and recovery
- ✅ Hardware buffer management

### Message Processing
- ✅ Message cleaning and validation
- ✅ Type classification (test vs custom messages)
- ✅ Content filtering and safety checks
- ✅ Statistics tracking

### TinyLLM Integration (Ollama)
- ✅ Ollama API integration with TinyLlama model
- ✅ Raspberry Pi optimized settings
- ✅ Automatic retry logic with exponential backoff
- ✅ Response time monitoring and failure recovery

### Logging and Monitoring
- ✅ Colored console output with component prefixes
- ✅ Comprehensive file logging
- ✅ Real-time performance statistics
- ✅ Transaction logging

## 🧪 Testing

### Run Component Tests
```bash
python3 tests/test_serial_client.py

# Test Ollama integration specifically
python3 test_ollama.py
```

### Test Modes

#### 1. Mock Test Mode
Test without hardware or LLM:
```bash
python3 main.py --config config/rpi_config.yaml --test-mode
```

#### 2. Serial Test Mode  
Test serial reception only:
```bash
python3 main.py --config config/rpi_config.yaml --serial-test
```

#### 3. Integration Test
Test full pipeline with mock LLM:
```bash
python3 main.py --config config/client_config.yaml
# (Uses mock interface by default in client_config.yaml)
```

## 📊 Example Output

```
[12:34:56.789] INFO     SERIAL: Waiting for data...
[12:34:57.123] INFO     SERIAL: Received: "TEST MESSAGE FROM ACORN SYSTEM"
[12:34:57.124] INFO     PROCESS: Cleaned message: "TEST MESSAGE FROM ACORN SYSTEM"
[12:34:57.125] INFO     LLM: Forwarding to TinyLLM...
[12:34:58.456] INFO     LLM: Response received (1.331s): "[AI response here]"
[12:34:58.457] INFO     LOG: Transaction logged to file
[12:34:58.458] INFO     SERIAL: Ready for next message...
```

## 🔧 Command Line Options

```bash
python3 main.py [OPTIONS]

Options:
  -c, --config PATH         Configuration file path (default: config/client_config.yaml)
  -t, --test-mode          Run with simulated messages
  -s, --serial-test        Test serial reception only
  -p, --port DEVICE        Override serial port (e.g., /dev/ttyUSB0)
  -b, --baudrate RATE      Override baudrate (e.g., 9600)
  -l, --log-level LEVEL    Override log level (DEBUG, INFO, WARNING, ERROR)
  -v, --verbose            Enable verbose output (DEBUG level)
  -h, --help               Show help message
```

## 🔍 Troubleshooting

### Serial Connection Issues

**Problem**: `Permission denied` on `/dev/ttyUSB0`
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Logout and login again
```

**Problem**: Device not found
```bash
# Check available devices
ls -la /dev/ttyUSB*
ls -la /dev/ttyACM*

# Test with different device
python3 main.py --config config/rpi_config.yaml --port /dev/ttyUSB1
```

### TinyLLM Integration Issues

**Problem**: Ollama not running
```bash
# Check Ollama service
sudo systemctl status ollama
sudo systemctl start ollama

# Test Ollama manually
ollama run tinyllama "test message"
```

**Problem**: TinyLlama model not found
```bash
# Pull the model
ollama pull tinyllama

# Test API endpoint
curl http://localhost:11434/api/generate \
  -d '{"model":"tinyllama","prompt":"test","stream":false}'
```

### Performance Issues

**Problem**: High response times
- Increase timeout values in config
- Check TinyLLM model size and hardware
- Monitor system resources

**Problem**: Message loss
- Check serial cable quality
- Verify baud rate matches sender
- Enable DEBUG logging for detailed analysis

## 📁 Project Structure

```
ArmGPT-server/
├── src/
│   ├── __init__.py
│   ├── serial_client.py      # Serial communication
│   ├── message_processor.py  # Message cleaning/validation
│   ├── llm_interface.py      # Ollama/TinyLLM integration
│   └── logger.py            # Colored logging system
├── config/
│   ├── client_config.yaml   # Default configuration
│   └── rpi_config.yaml      # Raspberry Pi optimized
├── logs/                    # Log files (auto-created)
├── tests/
│   └── test_serial_client.py
├── main.py                  # Main application entry
├── test_ollama.py           # Ollama integration testing
├── install_tinyllm_rpi.sh   # Raspberry Pi setup script
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── README_RASPBERRY_PI.md  # Pi-specific setup guide
├── CHANGELOG.md             # Project changelog
└── python_prompt.md        # Original project prompt
```

## 🤝 Integration with ARM Assembly Sender

This client is designed to work with the existing ARM assembly program that:

- Sends messages via `/dev/ttyUSB0` at 9600 baud
- Uses ASCII encoding with `\n` terminators
- Implements hardware buffer flushing for reliability
- Provides menu-driven interface with test/custom/continuous modes

The client maintains full compatibility with existing bash testing tools like `test-listener.sh`.

## 📈 Performance Monitoring

The client tracks comprehensive statistics:

### Message Statistics
- Total messages received
- Valid vs invalid messages
- Message type distribution
- Processing success rate

### LLM Statistics  
- Request/response counts
- Average response times
- Failure rates and retry patterns
- Timeout occurrences

### System Statistics
- Serial connection uptime
- Reconnection events
- Error rates by component
- Memory usage patterns

## 🔒 Security Considerations

- Input validation prevents malformed messages
- No code execution from serial input
- Configurable message length limits
- Safe error handling prevents crashes
- Optional transaction logging for audit trails

## 📝 License

This project is part of the ArmGPT-server system for educational and research purposes.

---

## 🎯 Next Steps

1. **Install on Raspberry Pi**: Run `./install_tinyllm_rpi.sh` to set up Ollama
2. **Test Integration**: Run `python3 test_ollama.py` to verify Ollama works
3. **Test Hardware**: Verify serial connection with `python3 main.py --config config/rpi_config.yaml --serial-test`
4. **Go Live**: Connect to ARM sender and run `python3 main.py --config config/rpi_config.yaml`

**📖 For detailed Raspberry Pi setup, see [README_RASPBERRY_PI.md](README_RASPBERRY_PI.md)**

**📋 For complete change history, see [CHANGELOG.md](CHANGELOG.md)**

For questions or issues, check the troubleshooting section or review the logs in the `logs/` directory.

## 🏆 **Project Status: Production Ready**

- **✅ Fully implemented** and tested on Raspberry Pi 4
- **✅ ARM assembly integration** confirmed working
- **✅ TinyLlama AI responses** generating successfully  
- **✅ Serial communication** stable at 9600 baud
- **✅ Automated deployment** with installation script
- **✅ Comprehensive documentation** and troubleshooting guides