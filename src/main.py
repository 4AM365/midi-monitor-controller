"""Application entry point"""

import json
import sys
from midi_handler import MIDIHandler, ControlType
from monitor_controller import MonitorController
from control_mappings import ControlMapper
from config import Config

def main():
    # Load configuration
    config = Config.load()
    
    # Load discovered VCP codes
    with open('data/vcp_codes.json') as f:
        vcp_codes = json.load(f)
    
    # Initialize components
    monitor = MonitorController(config.monitor_name, vcp_codes)
    midi = MIDIHandler(config.midi_device)
    mapper = ControlMapper(monitor, midi)
    
    # Restore or initialize state
    if config.always_start_calibrated:
        mapper.night_mode.position = 100
        mapper.monitor.set_blue_gain(100)
    else:
        mapper.load_state()
    
    # Initialize LEDs to match state
    mapper.sync_leds()
    
    print("Monitor Controller running. Press Ctrl+C to exit.")
    
    try:
        # Main event loop
        while True:
            event = midi.read_event()
            
            # Route to appropriate handler
            if event.control_id == config.brightness_knob_cc:
                delta = _parse_relative_cc(event.value)
                mapper.handle_brightness_knob(delta)
            
            elif event.control_id == config.night_mode_knob_cc:
                delta = _parse_relative_cc(event.value)
                mapper.handle_night_mode_knob(delta)
            
            elif event.control_id == config.hdr_button_note:
                mapper.handle_hdr_button()
            
            # ... etc for other controls
    
    except KeyboardInterrupt:
        print("\nSaving state and exiting...")
        mapper.save_state()
        sys.exit(0)

def _parse_relative_cc(value: int) -> int:
    """Convert relative CC value to signed delta"""
    return value - 64 if value > 64 else -(64 - value)


#this block is a guard that keeps us from using modules in other plaes without realizing that there are dependencies referred to in other contexts.
if __name__ == '__main__':
    main()