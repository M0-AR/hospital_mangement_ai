# AI Surveillance System

A robust, cross-platform AI surveillance system designed for offline environments. This system automatically detects and connects to existing security cameras on your network, providing real-time AI-powered monitoring capabilities.

## 🚀 Features

### Core Capabilities
- **Auto-Discovery**: Automatically finds and connects to IP cameras on your network
- **Multi-Camera Support**: Handles multiple camera feeds simultaneously
- **Offline Operation**: Works without internet connection
- **Cross-Platform**: Runs on both Windows and Linux

### AI Detection
- **Face Detection**: Identifies and tracks faces in real-time
- **Motion Detection**: Intelligent motion tracking and alerts
- **Person Detection**: Detects and tracks people in camera feeds

### Recording & Storage
- **Motion-Triggered Recording**: Automatically saves video when motion is detected
- **Local Storage**: All data stored locally for security
- **Organized Archives**: Recordings saved with timestamps

## 📋 Requirements

### Minimum System Requirements
- CPU: Dual-core processor (Quad-core recommended)
- RAM: 4GB minimum (8GB recommended)
- Storage: 1GB for installation + space for recordings
- Network: Local network access to IP cameras
- OS: Windows 7+ or Linux (Ubuntu 18.04+, CentOS 7+)

### Software Requirements
- Python 3.8 or higher
- OpenCV dependencies (automatically installed)
- Network access to cameras

## 🔧 Installation

### Windows Installation
1. Copy the entire project folder to your target machine
2. Open Command Prompt as Administrator
3. Navigate to the project directory
4. Run the setup script:
   ```batch
   install\windows_setup.bat
   ```

### Linux Installation
1. Copy the entire project folder to your target machine
2. Open terminal
3. Navigate to the project directory
4. Make the setup script executable and run it:
   ```bash
   chmod +x install/linux_setup.sh
   ./install/linux_setup.sh
   ```

## 🎮 Usage

### Starting the System
```bash
# Windows
python src/main.py

# Linux
python3 src/main.py
```

### Available Commands
- `q`: Quit the application
- `h`: Show help menu
- `s`: Show system status
- `r`: Rescan for new cameras

### System Operation
1. On startup, the system will:
   - Scan your network for IP cameras
   - Connect to found cameras
   - Start processing video feeds
   - Display camera feeds in a grid

2. Motion Detection:
   - Automatically starts recording when motion is detected
   - Saves recordings with timestamps
   - Continues recording until motion stops

3. AI Processing:
   - Continuously analyzes video feeds
   - Highlights detected faces and people
   - Marks areas with motion

## ⚙️ Configuration

### Configuration File
Edit `config/default_config.yaml` to customize:

```yaml
# Camera Settings
camera_scan:
  ip_ranges:
    - "192.168.1"
    - "192.168.0"
  ports:
    - 554   # RTSP
    - 8000  # HTTP
    - 8080  # HTTP Alt

# AI Settings
ai:
  face_detection:
    enabled: true
    min_size: 30
  motion_detection:
    enabled: true
    threshold: 20
  person_detection:
    enabled: true
```

### Recording Settings
```yaml
recording:
  motion_trigger: true
  format: "avi"
  retention_days: 7
```

## 🔍 Troubleshooting

### Common Issues

1. No Cameras Found
   - Check if cameras are powered on
   - Verify network connectivity
   - Confirm camera IP addresses
   - Check camera credentials in config

2. System Performance
   - Reduce number of simultaneous camera feeds
   - Lower AI processing settings
   - Check system resources

3. Recording Issues
   - Verify sufficient disk space
   - Check write permissions
   - Confirm recording path in config

### Logs
- Check `surveillance.log` for detailed system logs
- Error messages include timestamps and details
- Log level configurable in config file

## 🛟 Support

### Getting Help
1. Check the logs in `surveillance.log`
2. Review configuration in `config/default_config.yaml`
3. Verify system requirements
4. Check network connectivity

### Best Practices
- Regularly check available disk space
- Monitor system resource usage
- Keep configuration file backed up
- Test camera connections periodically

## 🔒 Security Notes

### Network Security
- System operates on local network only
- No external internet connection required
- Camera credentials stored in config file

### Data Security
- All recordings stored locally
- No cloud uploads
- Access controlled by OS permissions

## 📝 License

This project is proprietary software. All rights reserved.

## 🤝 Contributing

For internal use only. Not open for external contributions.
