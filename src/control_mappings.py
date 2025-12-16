"""State management and control logic"""

from dataclasses import dataclass
from typing import Callable

@dataclass
class KnobState:
    """Virtual knob position with constraints"""
    position: int
    min_val: int
    max_val: int
    name: str
    
    def adjust(self, delta: int) -> tuple[int, bool]:
        """
        Adjust position by delta, return (new_position, hit_limit)
        """
        old = self.position
        self.position = max(self.min_val, min(self.max_val, self.position + delta))
        hit_limit = (self.position == self.max_val or self.position == self.min_val) and old != self.position
        return self.position, hit_limit

class ControlMapper:
    """Maps MIDI events to monitor actions with state"""
    
    def __init__(self, monitor: MonitorController, midi: MIDIHandler):
        self.monitor = monitor
        self.midi = midi
        
        # Virtual knob states
        self.brightness = KnobState(75, 0, 100, "Brightness")
        self.night_mode = KnobState(100, 0, 100, "Night Mode")  # 100 = calibrated
        
        # Button toggle states
        self.hdr_enabled = False
        self.crosshair_enabled = False
    
    def handle_brightness_knob(self, delta: int):
        """Handle brightness knob adjustment"""
        new_val, hit_limit = self.brightness.adjust(delta)
        self.monitor.set_brightness(new_val)
        self.midi.set_led_ring(1, self._scale_to_led(new_val))
        if hit_limit:
            self._notify_limit("Brightness")
    
    def handle_night_mode_knob(self, delta: int):
        """Handle night mode knob adjustment"""
        new_val, hit_limit = self.night_mode.adjust(delta)
        self.monitor.set_blue_gain(new_val)
        self.midi.set_led_ring(2, self._scale_to_led(new_val))
        if hit_limit and new_val == 100:
            self._notify_calibrated()
    
    def handle_hdr_button(self):
        """Toggle HDR mode"""
        self.hdr_enabled = not self.hdr_enabled
        success = self.monitor.toggle_hdr()
        self.midi.set_button_led(1, self.hdr_enabled if success else not self.hdr_enabled)
    
    def save_state(self):
        """Persist knob positions to disk"""
        pass
    
    def load_state(self):
        """Restore knob positions from disk"""
        pass