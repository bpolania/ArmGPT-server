# Python TinyLLM Serial Listener Client - Development Prompt

## 🎯 **Project Overview**

You are tasked with creating a Python client that receives serial data from an ARM assembly program running on a Raspberry Pi and forwards the messages to TinyLLM for AI processing. This is part of a dual-Pi communication system where one Pi sends data via ARM assembly and the other Pi (your Python client) receives and processes it with AI.

---

## 🏗️ **System Architecture**

### **Current Working System**
```
┌─────────────────┐    USB Serial   ┌─────────────────┐    Your Task    ┌─────────────────┐
│   SENDER PI     │     Cable       │   RECEIVER PI   │   ────────────▶ │    TinyLLM      │
│                 │ ──────────────▶ │                 │                 │                 │
│ ARM Assembly    │  /dev/ttyUSB0   │ Python Client   │                 │ AI Processing   │
│ Program         │   9600 baud     │ (Your Code)     │                 │ Response Gen    │
│                 │                 │                 │                 │                 │
│ • Menu System   │                 │ • Serial Listen │                 │ • Text Analysis │
│ • Test Messages │                 │ • Data Parse    │                 │ • AI Response   │
│ • Custom Input  │                 │ • LLM Forward   │                 │ • Generation    │
│ • Continuous    │                 │ • Response Log  │                 │ • Processing    │
└─────────────────┘                 └─────────────────┘                 └─────────────────┘
```

### **Hardware Setup**
- **Connection**: USB Male-to-Male Serial Cable between two Raspberry Pis
- **Device**: `/dev/ttyUSB0` on both Pis
- **Protocol**: 9600 baud, 8N1 (8 data bits, no parity, 1 stop bit)
- **Flow Control**: None

---

## 📡 **ARM Assembly Sender System Details**

### **Message Types and Formats**
The ARM assembly program sends these message types:

#### **1. Test Message**
```
TEST MESSAGE FROM ACORN SYSTEM\n
```

#### **2. Custom Messages**
```
[User input up to 255 characters]\n
```

#### **3. Continuous Data**
```
TEST MESSAGE FROM ACORN SYSTEM\n
TEST MESSAGE FROM ACORN SYSTEM\n
[...repeats 10 times with timing delays]
```

### **ARM Assembly Program Features**
- **Menu-driven interface** with 4 options:
  1. Send test message
  2. Send continuous data (10 iterations)
  3. Send custom message (user input)
  4. Exit
- **Robust error handling** with fallback mechanisms
- **Hardware buffer flushing** using SYS_FSYNC for reliable transmission
- **Comprehensive logging** to `acorn_comm.log`

### **Message Characteristics**
- **Encoding**: ASCII text
- **Termination**: `\n` (newline character)
- **Length**: Variable (test message ~31 chars, custom up to 255 chars)
- **Frequency**: On-demand (user triggered) or continuous (10 messages with delays)
- **Reliability**: Hardware-confirmed transmission with buffer flushing

---

## 🤖 **TinyLLM Integration Requirements**

### **Your Task**
Create a Python client that:
1. **Monitors** `/dev/ttyUSB0` for incoming serial data
2. **Receives** messages from the ARM assembly sender
3. **Processes** and cleans the message format
4. **Forwards** messages to TinyLLM for AI processing
5. **Captures** and logs TinyLLM responses
6. **Provides** comprehensive logging and diagnostics

### **Unknown TinyLLM Details** (You Need to Ask User)
- **Installation method**: How is TinyLLM installed/accessed?
- **Interface type**: Command line, Python API, HTTP API, or interactive mode?
- **Input format**: Plain text, JSON, special formatting requirements?
- **Response format**: stdout, file output, API response format?
- **Example usage**: What's the exact command/method to send a message?

---

## 🔧 **Technical Specifications**

### **Python Client Requirements**

#### **Core Functionality**
```python
# Essential features your client must implement:

1. Serial Communication
   - Connect to /dev/ttyUSB0 at 9600 baud
   - Handle connection errors and device detection
   - Implement proper serial port configuration
   - Real-time message reception with proper buffering

2. Message Processing
   - Parse incoming serial data
   - Clean message format (remove extra whitespace, handle newlines)
   - Validate message content
   - Handle different message types (test vs custom)

3. TinyLLM Integration
   - Forward cleaned messages to TinyLLM
   - Handle TinyLLM API/interface properly
   - Capture AI responses
   - Error handling for LLM failures

4. Logging and Monitoring
   - Comprehensive logging (timestamp, message, response)
   - Real-time console output with color coding
   - File-based logging for analysis
   - Performance monitoring (message rate, response time)

5. Error Handling
   - Serial port disconnection/reconnection
   - TinyLLM failures or timeouts
   - Malformed message handling
   - Graceful shutdown (Ctrl+C)
```

#### **Recommended Libraries**
```python
import serial          # PySerial for serial communication
import logging         # Comprehensive logging
import argparse        # Command-line arguments
import json           # JSON handling if needed
import time           # Timing and delays
import signal         # Graceful shutdown handling
import sys            # System operations
import colorama       # Colored terminal output
from datetime import datetime  # Timestamp formatting
```

#### **Serial Configuration**
```python
# Exact serial configuration to match ARM sender:
serial_config = {
    'port': '/dev/ttyUSB0',
    'baudrate': 9600,
    'bytesize': serial.EIGHTBITS,
    'parity': serial.PARITY_NONE,
    'stopbits': serial.STOPBITS_ONE,
    'timeout': 1,  # 1 second read timeout
    'xonxoff': False,  # No software flow control
    'rtscts': False,   # No hardware flow control
    'dsrdtr': False    # No DTR/DSR flow control
}
```

### **Expected Message Processing Flow**
```python
# Message processing pipeline:
1. Raw serial data: b'TEST MESSAGE FROM ACORN SYSTEM\n'
2. Decode to string: 'TEST MESSAGE FROM ACORN SYSTEM\n'
3. Clean message: 'TEST MESSAGE FROM ACORN SYSTEM'
4. Validate content: Check for non-empty, reasonable length
5. Forward to TinyLLM: [Your LLM interface method]
6. Capture response: [LLM response handling]
7. Log transaction: Timestamp, input, output, processing time
```

---

## 📋 **Development Requirements**

### **Project Structure**
```
tinyllm-serial-client/
├── src/
│   ├── __init__.py
│   ├── serial_client.py      # Main client class
│   ├── llm_interface.py      # TinyLLM integration
│   ├── message_processor.py  # Message parsing/cleaning
│   └── logger.py            # Logging configuration
├── config/
│   └── client_config.yaml   # Configuration file
├── logs/                    # Log file directory
├── tests/                   # Unit tests
├── requirements.txt         # Python dependencies
├── README.md               # Project documentation
└── main.py                 # Entry point
```

### **Configuration File Example**
```yaml
# client_config.yaml
serial:
  port: "/dev/ttyUSB0"
  baudrate: 9600
  timeout: 1
  
tinyllm:
  # TinyLLM configuration (to be determined)
  api_endpoint: ""  # If HTTP API
  model_path: ""    # If local model
  command: ""       # If command line
  
logging:
  level: "INFO"
  file: "logs/serial_client.log"
  console: true
  
client:
  max_message_length: 512
  reconnect_attempts: 5
  reconnect_delay: 2
```

### **Command Line Interface**
```bash
# Expected usage:
python main.py --config config/client_config.yaml --verbose
python main.py --port /dev/ttyUSB0 --baudrate 9600 --log-level DEBUG
python main.py --test-mode  # For testing without TinyLLM
```

---

## 🎯 **Expected Behavior**

### **Startup Sequence**
1. **Configuration Loading**: Load settings from config file or command line
2. **Device Detection**: Check if `/dev/ttyUSB0` exists and is accessible
3. **Serial Connection**: Connect to serial port with proper configuration
4. **TinyLLM Verification**: Test TinyLLM availability and responsiveness
5. **Ready State**: Display "Ready to receive messages" with timestamp

### **Message Reception Flow**
```
[12:34:56.789] SERIAL: Waiting for data...
[12:34:57.123] SERIAL: Received: "TEST MESSAGE FROM ACORN SYSTEM"
[12:34:57.124] PROCESS: Cleaned message: "TEST MESSAGE FROM ACORN SYSTEM"
[12:34:57.125] LLM: Forwarding to TinyLLM...
[12:34:58.456] LLM: Response received (1.331s): "[AI response here]"
[12:34:58.457] LOG: Transaction logged to file
[12:34:58.458] SERIAL: Ready for next message...
```

### **Error Handling Examples**
```
[12:35:00.000] ERROR: Serial port /dev/ttyUSB0 not found
[12:35:00.001] INFO: Scanning for USB serial devices...
[12:35:00.002] INFO: Found /dev/ttyUSB1, updating configuration
[12:35:00.003] INFO: Reconnected successfully

[12:36:00.000] WARNING: TinyLLM timeout after 30 seconds
[12:36:00.001] INFO: Retrying TinyLLM request (attempt 2/3)
[12:36:05.000] INFO: TinyLLM response received on retry
```

---

## 🧪 **Testing and Validation**

### **Testing Modes**
```python
# Implement these testing modes:

1. Serial Test Mode
   - Connect to serial port
   - Display raw received data
   - No LLM processing
   - Validate message reception

2. LLM Test Mode  
   - Skip serial input
   - Test TinyLLM with predefined messages
   - Validate LLM integration
   - Performance testing

3. Integration Test Mode
   - Full pipeline testing
   - Simulated message injection
   - End-to-end validation
   - Performance metrics

4. Stress Test Mode
   - Rapid message processing
   - Continuous operation testing
   - Memory usage monitoring
   - Error recovery testing
```

### **Validation Against Working System**
The current bash-based system that achieved breakthrough used:
```bash
# test-listener.sh option 1 (the working method):
cat /dev/ttyUSB0

# This successfully received:
"TEST MESSAGE FROM ACORN SYSTEM"
```
Your Python client must at minimum replicate this functionality and then extend it with TinyLLM integration.

---

## 📊 **Performance Requirements**

### **Response Time Targets**
- **Serial Reception**: < 100ms from transmission to Python receipt
- **Message Processing**: < 50ms for cleaning and validation
- **TinyLLM Forward**: < 2 seconds for typical responses
- **Total Pipeline**: < 3 seconds from serial input to logged LLM response

### **Reliability Requirements**
- **99% Message Reception**: No lost messages under normal operation
- **Automatic Reconnection**: Handle USB cable disconnects
- **Graceful Degradation**: Continue operation if LLM temporarily unavailable
- **Memory Efficiency**: Stable memory usage during continuous operation

---

## 🔍 **Debugging and Diagnostics**

### **Debug Features to Implement**
```python
# Essential debugging capabilities:

1. Raw Serial Data Logging
   - Hex dump of received bytes
   - Timing information
   - Buffer state monitoring

2. Message Flow Tracing
   - Step-by-step processing logs
   - Pipeline timing breakdown
   - Error point identification

3. LLM Interface Debugging
   - Request/response logging
   - Timeout monitoring
   - Error classification

4. Performance Monitoring
   - Message rate tracking
   - Response time statistics
   - Resource usage monitoring
```

### **Compatibility with Existing Tools**
Your Python client should coexist with the existing bash testing tools:
- **test-listener.sh**: Should still work for basic testing
- **serial-monitor.sh**: Should still work for monitoring
- **Device detection scripts**: Should work with your client

---

## 🚀 **Implementation Phases**

### **Phase 1: Basic Serial Client**
1. Implement serial port connection and configuration
2. Basic message reception and display
3. Clean message processing pipeline
4. File-based logging
5. Command-line interface

### **Phase 2: TinyLLM Integration**
1. Research and implement TinyLLM interface
2. Message forwarding to TinyLLM
3. Response capture and processing
4. Error handling for LLM failures
5. Performance optimization

### **Phase 3: Advanced Features**
1. Configuration management
2. Advanced error recovery
3. Performance monitoring
4. Multiple LLM model support
5. Web interface (optional)

---

## 🔧 **Development Environment Setup**

### **Dependencies**
```bash
# Required Python packages:
pip install pyserial colorama pyyaml argparse
pip install [tinyllm-specific-packages]  # To be determined

# System requirements:
sudo usermod -a -G dialout $USER  # Serial port access
# Logout/login required after group change
```

### **Development Tools**
```bash
# Useful for testing:
sudo apt install screen minicom  # Serial debugging tools
pip install pytest pytest-cov    # Testing framework
pip install black flake8        # Code formatting/linting
```

---

## 📝 **First Steps**

1. **Ask the user** about TinyLLM setup and interface details
2. **Create the project structure** as outlined above
3. **Implement basic serial client** (Phase 1)
4. **Test message reception** against the working ARM assembly sender
5. **Implement TinyLLM integration** once interface details are known
6. **Validate end-to-end pipeline** with comprehensive testing

---

## 🎯 **Success Criteria**

Your Python client is successful when:
- ✅ **Receives all message types** from ARM assembly sender
- ✅ **Processes messages correctly** with proper cleaning
- ✅ **Forwards to TinyLLM** using correct interface
- ✅ **Captures AI responses** reliably
- ✅ **Provides comprehensive logging** for analysis
- ✅ **Handles errors gracefully** with automatic recovery
- ✅ **Performs within target response times**
- ✅ **Coexists with existing testing tools**

**Remember**: The ARM assembly system is already working perfectly. Your job is to replace only the receiver side while maintaining full compatibility with the sender.