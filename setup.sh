#!/bin/bash

# Setup script for ArmGPT-server
# Cleans log files and prepares environment

echo "🧹 ArmGPT-server Setup Script"
echo "=============================="

# Function to clean log files
clean_logs() {
    echo "📁 Cleaning log files..."
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Find and clean all log files
    if [ -d "logs" ]; then
        log_count=$(find logs -name "*.log" 2>/dev/null | wc -l)
        
        if [ $log_count -gt 0 ]; then
            echo "Found $log_count log file(s)"
            
            # Clean each log file
            for logfile in logs/*.log; do
                if [ -f "$logfile" ]; then
                    echo "  ✓ Cleaning: $logfile"
                    > "$logfile"  # Empty the file but keep it
                fi
            done
            
            echo "✅ Log files cleaned"
        else
            echo "  No log files found to clean"
        fi
    fi
}

# Function to check Python dependencies
check_dependencies() {
    echo ""
    echo "📦 Checking Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        missing_deps=0
        while IFS= read -r package; do
            # Skip empty lines and comments
            [[ -z "$package" || "$package" =~ ^# ]] && continue
            
            # Extract package name (before any version specifier)
            pkg_name=$(echo "$package" | sed 's/[<>=!].*//')
            
            if ! python3 -c "import $pkg_name" 2>/dev/null; then
                echo "  ❌ Missing: $package"
                missing_deps=$((missing_deps + 1))
            else
                echo "  ✅ Found: $pkg_name"
            fi
        done < requirements.txt
        
        if [ $missing_deps -gt 0 ]; then
            echo ""
            echo "⚠️  Missing $missing_deps dependencies"
            echo "Run: pip3 install -r requirements.txt"
        else
            echo "✅ All dependencies installed"
        fi
    fi
}

# Function to check configuration files
check_config() {
    echo ""
    echo "⚙️  Checking configuration files..."
    
    configs=("config/client_config.yaml" "config/rpi_config.yaml")
    
    for config in "${configs[@]}"; do
        if [ -f "$config" ]; then
            echo "  ✅ Found: $config"
        else
            echo "  ❌ Missing: $config"
        fi
    done
}

# Function to show system info
show_system_info() {
    echo ""
    echo "💻 System Information:"
    echo "  OS: $(uname -s)"
    echo "  Architecture: $(uname -m)"
    echo "  Python: $(python3 --version 2>&1)"
    
    # Check if running on Raspberry Pi
    if [ -f /proc/device-tree/model ]; then
        echo "  Device: $(cat /proc/device-tree/model)"
    fi
}

# Main execution
main() {
    # Parse command line arguments
    case "$1" in
        --logs-only)
            clean_logs
            ;;
        --check)
            check_dependencies
            check_config
            show_system_info
            ;;
        --help|-h)
            echo "Usage: $0 [option]"
            echo "Options:"
            echo "  --logs-only    Clean only log files"
            echo "  --check        Check dependencies and config only"
            echo "  --help         Show this help message"
            echo "  (no option)    Run full setup"
            ;;
        *)
            # Full setup
            clean_logs
            check_dependencies
            check_config
            show_system_info
            
            echo ""
            echo "✅ Setup complete!"
            echo ""
            echo "📚 Quick start commands:"
            echo "  Test mode:        python3 main.py --test-mode"
            echo "  Serial test:      python3 main.py --serial-test"
            echo "  Production (Pi):  python3 main.py --config config/rpi_config.yaml"
            ;;
    esac
}

# Run main function with all arguments
main "$@"