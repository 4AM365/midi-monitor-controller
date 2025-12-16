"""MIDI I/O for X-Touch Mini"""

from enum import Enum
from dataclasses import dataclass

class ControlType(Enum):
    KNOB = "knob"
    BUTTON = "button"

@dataclass
class MIDIEvent:
    """Semantic MIDI event"""
    control_type: ControlType
    control_id: int
    value: int  # For knobs: relative delta; for buttons: 0/1

class MIDIHandler:
    """Manages X-Touch Mini communication"""
    
    def __init__(self, device_name: str = "X-TOUCH MINI"):
        self.inport = None
        self.outport = None
        self._connect(device_name)
    
    def read_event(self) -> MIDIEvent:
        """Blocking read of next MIDI event"""
        pass
    
    def set_led_ring(self, knob_id: int, value: int):
        """Set LED ring position (0-11)"""
        pass
    
    def set_button_led(self, button_id: int, state: bool):
        """Set button LED on/off"""
        pass