# src/config.py
"""Configuration for monitor controller"""

from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
from typing import Optional

@dataclass
class Config:
    """Application configuration"""
    
    # Monitor settings
    monitor_name: str = "BenQ EX321UX"
    monitor_index: int = 0
    
    # MIDI device
    midi_device: str = "X-TOUCH MINI"
    knob_sensitivity: float = 1.0  # For absolute encoders
    
    # X-Touch control mappings (DEPRECATED - use controls dict instead)
    knob_brightness: int = 1
    knob_night_mode: int = 2
    button_local_dimming: int = 8
    button_hdr: int = 9
    button_crosshair: int = 10
    
    # Behavior
    always_start_calibrated: bool = True
    
    # Dynamic control mappings (NEW - put after fields with defaults)
    controls: dict = field(default_factory=dict)
    
    def save(self, path: Optional[str] = None):
        """Save configuration to JSON file"""
        if path is None:
            path = Path.home() / ".monitor_controller_config.json"
        else:
            path = Path(path).expanduser()
        
        # Convert to dict
        config_dict = asdict(self)
        
        # Save to JSON
        with open(path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        print(f"✓ Configuration saved to {path}")
    
    @classmethod
    def load(cls, path: Optional[str] = None):
        """Load configuration from JSON, or return defaults if not found"""
        if path is None:
            path = Path.home() / ".monitor_controller_config.json"
        else:
            path = Path(path).expanduser()
        
        if path.exists():
            with open(path, 'r') as f:
                data = json.load(f)
            
            print(f"✓ Configuration loaded from {path}")
            return cls(**data)
        else:
            # No config file - return defaults
            print("ℹ️  No configuration file found, using defaults")
            return cls()
    
    @staticmethod
    def exists(path: Optional[str] = None) -> bool:
        """Check if configuration file exists"""
        if path is None:
            path = Path.home() / ".monitor_controller_config.json"
        else:
            path = Path(path).expanduser()
        
        return path.exists()