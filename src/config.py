"""User configuration"""

from dataclasses import dataclass

@dataclass
class Config:
    """Application configuration"""
    
    # Monitor settings
    monitor_name: str = "BenQ EX321UX"
    
    # MIDI device
    midi_device: str = "X-TOUCH MINI"
    
    # Control mappings (CC numbers from X-Touch Editor)
    brightness_knob_cc: int = 1
    night_mode_knob_cc: int = 2
    hdr_button_note: int = 0
    local_dimming_button_note: int = 1
    crosshair_button_note: int = 2
    
    # Behavior
    always_start_calibrated: bool = True  # Night mode knob resets to 100 on startup
    notify_on_limit: bool = True
    
    @classmethod
    def load(cls, path: str = "config.json"):
        """Load from JSON"""
        pass