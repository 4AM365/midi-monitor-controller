# src/midi_handler.py
"""MIDI input/output handler for X-Touch Mini"""

import mido
from typing import Optional
from dataclasses import dataclass

@dataclass
class MIDIEvent:
    """Represents a processed MIDI event"""
    control_type: str  # 'knob', 'button'
    control_id: int    # CC number or note number
    value: int         # Raw MIDI value
    delta: Optional[int] = None  # For knobs: scaled delta

class MIDIHandler:
    """
    Handles MIDI I/O with X-Touch Mini.
    
    Args:
        device_name: MIDI device name
        knob_sensitivity: Scaling factor for knob deltas
    """
    
    def __init__(self, device_name: str, knob_sensitivity: float):
        # No defaults - force caller to provide values from Config
        self.device_name = device_name
        self.knob_sensitivity = knob_sensitivity
        self.inport: Optional[mido.ports.BaseInput] = None
        self.outport: Optional[mido.ports.BaseOutput] = None
        
        # Track previous knob values for delta calculation (absolute mode)
        self.knob_previous_values = {}
    
    # ... rest of the class stays the same ...
        
    def connect(self):
        """Open MIDI ports for input and output"""
        # Find X-Touch input port
        input_ports = mido.get_input_names()
        inport_name = None
        
        for port in input_ports:
            if self.device_name.upper() in port.upper():
                inport_name = port
                break
        
        if not inport_name:
            raise RuntimeError(f"X-Touch Mini not found. Available ports: {input_ports}")
        
        # Find X-Touch output port (for LED feedback)
        output_ports = mido.get_output_names()
        outport_name = None
        
        for port in output_ports:
            if self.device_name.upper() in port.upper():
                outport_name = port
                break
        
        # Open ports
        self.inport = mido.open_input(inport_name)
        if outport_name:
            self.outport = mido.open_output(outport_name)
        
        print(f"✓ Connected to {inport_name}")
        if self.outport:
            print(f"✓ LED output available on {outport_name}")
    
    def disconnect(self):
        """Close MIDI ports"""
        if self.inport:
            self.inport.close()
        if self.outport:
            self.outport.close()
    
    def calculate_absolute_delta(self, control_id: int, current_value: int) -> int:
        """Calculate delta from absolute encoder position."""
    
        # Check if this is the first reading for this knob
        if control_id not in self.knob_previous_values:
            # First reading - store it and return 0 delta
            self.knob_previous_values[control_id] = current_value
            print(f"[DEBUG] First reading for knob {control_id}: value={current_value}")
            return 0
        
        # Get previous value
        previous = self.knob_previous_values[control_id]
        
        # Calculate raw delta
        raw_delta = current_value - previous
        
        print(f"[DEBUG] Knob {control_id}: prev={previous}, curr={current_value}, raw_delta={raw_delta}")
            
        # Handle wrap-around
        if raw_delta > 64:
            raw_delta = raw_delta - 128
            print(f"[DEBUG] Wrap backward: raw_delta now {raw_delta}")
        elif raw_delta < -64:
            raw_delta = raw_delta + 128
            print(f"[DEBUG] Wrap forward: raw_delta now {raw_delta}")
        
        # Store current as previous for next time
        self.knob_previous_values[control_id] = current_value
        
        # Invert
        inverted_delta = -raw_delta
        
        # Scale
        scaled_delta = int(inverted_delta * self.knob_sensitivity)
        
        print(f"[DEBUG] inverted={inverted_delta}, scaled={scaled_delta}")
        
        return scaled_delta
    
    def read_event(self) -> Optional[MIDIEvent]:
        """
        Read next MIDI event (blocking).
        
        Returns:
            MIDIEvent or None if message should be ignored
        """
        if not self.inport:
            raise RuntimeError("MIDI not connected. Call connect() first.")
        
        msg = self.inport.receive()
        
        if msg.type == 'control_change':
            # Knob - use absolute delta calculation
            delta = self.calculate_absolute_delta(msg.control, msg.value)
            
            return MIDIEvent(
                control_type='knob',
                control_id=msg.control,
                value=msg.value,
                delta=delta
            )
        
        elif msg.type == 'note_on':
            # Button press
            if msg.velocity > 0:
                return MIDIEvent(
                    control_type='button',
                    control_id=msg.note,
                    value=msg.velocity
                )
            else:
                # Velocity 0 = button release (some controllers do this)
                return None
        
        elif msg.type == 'note_off':
            # Button release - ignore for now
            return None
        
        else:
            # Ignore other message types (pitchwheel, etc.)
            return None
        
#old led ring method    
    # def set_led_ring(self, knob_id: int, position: int):
    #     """
    #     Set LED ring position around a knob.
        
    #     Args:
    #         knob_id: Knob CC number (e.g., 1 for your knob 1)
    #         position: LED position (0-11, where 11 is full ring)
    #     """
    #     if not self.outport:
    #         return  # No output port available
        
    #     # X-Touch LED ring responds to CC messages
    #     position = max(0, min(11, position))  # Clamp 0-11
        
    #     msg = mido.Message('control_change', 
    #                       control=knob_id, 
    #                       value=position,
    #                       channel=0)
    #     self.outport.send(msg)

    # src/midi_handler.py - update for Pan mode

    def set_led_ring(self, knob_id: int, position: int):
        """
        Set LED ring position around a knob.
        
        Args:
            knob_id: Knob CC number
            position: Position 0-11 (visual segments)
        """
        if not self.outport:
            return
        
        position = max(0, min(11, position))
        
        # Pan mode: 0=full left, 64=center (off), 127=full right
        # We want: 0=no LEDs, 11=full ring
        # Map 0-11 to 64-127 (center to full right)
        led_value = 64 + int((position / 11) * 63)
        
        msg = mido.Message('control_change', 
                        control=knob_id, 
                        value=led_value,
                        channel=0)
        self.outport.send(msg)
    
    def set_button_led(self, button_id: int, state: bool):
        """
        Set button LED on/off.
        
        Args:
            button_id: Button note number
            state: True=on, False=off
        """
        if not self.outport:
            return
        
        velocity = 127 if state else 0
        msg = mido.Message('note_on',
                          note=button_id,
                          velocity=velocity,
                          channel=0)
        self.outport.send(msg)
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, *args):
        self.disconnect()