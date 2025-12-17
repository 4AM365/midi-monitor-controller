# src/main.py
"""Main entry point for Monitor Controller"""

import sys
import os
from midi_handler import MIDIHandler
from monitor_controller import MonitorController
from control_mapper import ControlMapper
from config import Config

def main():
    """Run the monitor controller application"""
    print("=" * 50)
    print("Monitor Controller v0.1.0")
    print("=" * 50)
    print()
    
    try:
        # Load configuration
        config = Config.load()
        
        # Initialize components
        print("Connecting to devices...")
        midi = MIDIHandler(
            device_name=config.midi_device,
            knob_sensitivity=config.knob_sensitivity
        )
        monitor = MonitorController(monitor_index=config.monitor_index)
        
        midi.connect()
        monitor.connect()
        
        # Create control mapper
        mapper = ControlMapper(midi, monitor, config)
        mapper.initialize()
        
        print()
        print("=" * 50)
        print("System Ready!")
        print("=" * 50)
        print(f"Knob {config.knob_brightness} = Brightness")
        print(f"Knob {config.knob_night_mode} = Night Mode")
        print(f"Button {config.button_local_dimming} = Local Dimming")
        print(f"Button {config.button_hdr} = HDR Toggle")
        print()
        print("Press Ctrl+C to exit")
        print("=" * 50)
        print()
        
        # Main event loop
        while True:
            event = midi.read_event()
            if event:
                mapper.handle_event(event)
                
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # Cleanup
        try:
            midi.disconnect()
            monitor.disconnect()
        except:
            pass
        
        print("✓ Goodbye!")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

# Fix working directory for PyInstaller
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    application_path = os.path.dirname(sys.executable)
else:
    # Running as script
    application_path = os.path.dirname(__file__)

os.chdir(application_path)