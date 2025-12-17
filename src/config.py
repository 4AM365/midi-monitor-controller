# src/config.py
"""Configuration for monitor controller"""

from dataclasses import dataclass

@dataclass
class Config:
    """Application configuration"""
    
    # Monitor settings
    monitor_name: str = "BenQ EX321UX"
    monitor_index: int = 0
    
    # MIDI device
    midi_device: str = "X-TOUCH MINI"
    knob_sensitivity: float = 1.0  # For absolute encoders
    
    # X-Touch control mappings
    # KNOBS (CC numbers)
    knob_brightness: int = 1
    knob_night_mode: int = 2
    
    # BUTTONS (Note numbers)
    button_local_dimming: int = 8
    button_hdr: int = 9
    button_crosshair: int = 10  # For future use
    
    # Behavior
    always_start_calibrated: bool = True
    
    @classmethod
    def load(cls):
        """Load configuration (for now just return defaults)"""
        return cls()