# PyAudio Installation Guide

PyAudio is required for voice recognition features in this application. Follow the platform-specific instructions below:

## Windows

### Method 1: Standard pip installation
```bash
pip install PyAudio
```

### Method 2: If pip fails, install Microsoft Visual C++ Build Tools
1. Download and install [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Then run:
```bash
pip install PyAudio
```

### Method 3: Use pre-compiled wheel
```bash
pip install pipwin
pipwin install pyaudio
```

### Method 4: Use conda (if you have Anaconda/Miniconda)
```bash
conda install pyaudio
```

## macOS

### Install PortAudio first
```bash
brew install portaudio
pip install PyAudio
```

### Alternative with conda
```bash
conda install pyaudio
```

## Linux

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio
pip install PyAudio
```

### CentOS/RHEL/Fedora
```bash
sudo yum install portaudio-devel
# or for newer versions:
sudo dnf install portaudio-devel
pip install PyAudio
```

### Arch Linux
```bash
sudo pacman -S portaudio
pip install PyAudio
```

## Troubleshooting

### Common Issues

1. **"Microsoft Visual C++ 14.0 is required" (Windows)**
   - Install Microsoft Visual C++ Build Tools
   - Or use Method 3 or 4 above

2. **"portaudio.h: No such file or directory" (Linux/macOS)**
   - Install PortAudio development headers as shown above

3. **Permission errors**
   - Use `pip install --user PyAudio` instead
   - Or use virtual environment

### Alternative: Use without PyAudio

If PyAudio installation continues to fail, you can:

1. Comment out PyAudio in requirements.txt
2. The voice recognition features will be disabled
3. All other app features will work normally

### Verification

Test if PyAudio is working:
```python
import pyaudio
print("PyAudio installed successfully!")
```

## Docker Alternative

If you're using Docker, add this to your Dockerfile:
```dockerfile
# For Ubuntu-based images
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    && rm -rf /var/lib/apt/lists/*

RUN pip install PyAudio
```