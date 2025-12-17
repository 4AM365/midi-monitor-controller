## Building from Source

### Prerequisites
- Python 3.10 or later
- Windows OS (for DDC/CI support)
- Git

### Setup

1. **Clone the repository**
```bash
   git clone https://github.com/yourusername/midi-monitor-controller.git
   cd midi-monitor-controller
```

2. **Create a virtual environment**
```bash
   python -m venv venv
   venv\Scripts\activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Install as editable package** (optional, for development)
```bash
   pip install -e .
```

### Running from Source
```bash
# Activate virtual environment (if not already active)
venv\Scripts\activate

# Run the application
python src/main.py
```

### Building the Executable

1. **Ensure dependencies are installed**
```bash
   pip install pyinstaller
```

2. **Build the executable**
```bash
   pyinstaller MonitorController.spec
```

3. **Find the executable**
```
   The built executable will be in: dist/MonitorController.exe
```

### Development

For interactive testing and development:
```bash
# Install Jupyter (optional)
pip install jupyter

# Run Jupyter notebook
jupyter notebook
```

Test files are located in `tests/` directory.

### Project Structure
```
midi-monitor-controller/
├── src/
│   ├── main.py              # Entry point
│   ├── config.py            # Configuration
│   ├── midi_handler.py      # MIDI I/O
│   ├── monitor_controller.py # DDC/CI control
│   ├── control_mapper.py    # Event routing
│   └── virtual_knob.py      # Knob position tracking
├── tests/                   # Test notebooks
├── MonitorController.spec   # PyInstaller build spec
├── requirements.txt         # Python dependencies
└── README.md
```

### Troubleshooting Build Issues

**Issue: "No module named '_rtmidi'"**
- Solution: Make sure `python-rtmidi` is installed: `pip install python-rtmidi`

**Issue: "No DDC-capable monitors found"**
- Solution: Ensure your monitor supports DDC/CI and the video cable supports it (DisplayPort or HDMI, not VGA)

**Issue: "X-Touch Mini not found"**
- Solution: 
  1. Check that X-Touch Mini is connected via USB
  2. Install Behringer drivers if needed
  3. Verify device appears in Windows Device Manager under "Sound, video and game controllers"

**Issue: EXE doesn't run / silent failure**
- Solution: Build with `console=True` in the spec file to see error messages