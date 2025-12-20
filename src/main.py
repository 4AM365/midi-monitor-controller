# src/main.py
"""Main entry point for Monitor Controller"""

import sys
import os
from midi_handler import MIDIHandler
from monitor_controller import MonitorController
from control_mapper import ControlMapper
from config import Config
from tray_icon import TrayIcon
from setup_wizard import SetupWizard

# Fix working directory for PyInstaller
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(__file__)

os.chdir(application_path)

def run_setup_wizard():
    """Run the setup wizard and return True if completed, False if cancelled"""
    wizard = SetupWizard()
    wizard.run()
    
    # Check if config was actually saved
    return Config.exists()

def main():
    """Run the monitor controller application"""
    
    # Check if this is first run
    if not Config.exists():
        print("=" * 50)
        print("First Run - Setup Required")
        print("=" * 50)
        print()
        
        # Run setup wizard
        if not run_setup_wizard():
            print("Setup cancelled. Exiting.")
            return 0
    
    # Load configuration
    config = Config.load()
    
    print("=" * 50)
    print("Monitor Controller v0.1.0")
    print("=" * 50)
    print()
    
    # Global reference for cleanup
    midi = None
    monitor = None
    tray = None
    
    def cleanup_and_exit():
        """Clean up resources and exit"""
        print("\nShutting down gracefully...")
        try:
            if midi:
                midi.disconnect()
            if monitor:
                monitor.disconnect()
            if tray:
                tray.stop()
        except:
            pass
        print("✓ Goodbye!")
        sys.exit(0)
    
    def rerun_setup():
        """Callback to re-run setup wizard from tray menu"""
        # This will be called from tray menu
        # Close current connections
        if midi:
            midi.disconnect()
        if monitor:
            monitor.disconnect()
        if tray:
            tray.stop()
        
        # Run wizard
        if run_setup_wizard():
            # Restart the application
            print("Configuration updated. Please restart the application.")
            sys.exit(0)
        else:
            print("Setup cancelled. Keeping existing configuration.")
            # Would need to restart connections here, but simpler to just exit
            sys.exit(0)
    
    try:
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
        print("Check system tray for icon")
        print("Right-click tray icon to reconfigure or exit")
        print("=" * 50)
        print()
        
        # Start system tray icon (with setup option)
        tray = TrayIcon(
            on_exit_callback=cleanup_and_exit,
            on_setup_callback=rerun_setup  # New parameter
        )
        tray.start()
        
        # Main event loop
        while tray.running:
            event = midi.read_event()
            if event:
                mapper.handle_event(event)
                
    except KeyboardInterrupt:
        cleanup_and_exit()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())