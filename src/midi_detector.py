# src/midi_detector.py
"""MIDI control detection for automatic mapping"""

import mido
import time
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass

@dataclass
class DetectedControl:
    """Represents a detected MIDI control"""
    control_type: str  # 'knob' or 'button'
    control_id: int    # CC number or note number
    message_type: str  # 'control_change' or 'note_on'
    name: str          # Human-readable description

class MIDIDetector:
    """Detects MIDI controls for automatic mapping"""
    
    def __init__(self, device_name: str):
        """
        Args:
            device_name: MIDI device name to monitor
        """
        self.device_name = device_name
        self.inport = None
    
    def connect(self):
        """Open MIDI input port"""
        input_ports = mido.get_input_names()
        
        for port in input_ports:
            if self.device_name in port:
                self.inport = mido.open_input(port)
                print(f"✓ Detector connected to {port}")
                return
        
        raise RuntimeError(f"Device '{self.device_name}' not found")
    
    def disconnect(self):
        """Close MIDI port"""
        if self.inport:
            self.inport.close()
    
    def listen_for_knob(self, timeout: int = 10) -> Optional[DetectedControl]:
        """
        Listen for any knob/encoder turn.
        
        Args:
            timeout: Seconds to wait for input
        
        Returns:
            DetectedControl if knob detected, None if timeout
        """
        if not self.inport:
            raise RuntimeError("Not connected. Call connect() first.")
        
        # CLEAR BUFFER - use iter_pending() to drain old messages
        print("Clearing buffer...")
        for _ in self.inport.iter_pending():
            pass  # Discard all pending messages
        
        time.sleep(0.05)  # Wait for messages to settle
        
        # Drain again
        for _ in self.inport.iter_pending():
            pass
        
        print(f"Listening for knob turn... ({timeout}s timeout)")
        print("(Turn a knob NOW)")
        
        time.sleep(0.2)  # Give user time to stop touching previous knob
        
        start_time = time.time()
        seen_controls = {}  # Track which controls sent messages
        
        while time.time() - start_time < timeout:
            # Check for messages (non-blocking)
            msg = self.inport.poll()  # Returns None if no message
            
            if msg and msg.type == 'control_change':
                # Track how many times this CC was seen
                cc_id = msg.control
                seen_controls[cc_id] = seen_controls.get(cc_id, 0) + 1
                
                print(f"  Saw CC {cc_id} (count: {seen_controls[cc_id]})")
                
                # If we've seen multiple messages from same CC, it's a knob
                if seen_controls[cc_id] >= 2:
                    print(f"✓ Detected knob: CC {cc_id}")
                    return DetectedControl(
                        control_type='knob',
                        control_id=cc_id,
                        message_type='control_change',
                        name=f"Knob/Encoder CC{cc_id}"
                    )
            
            time.sleep(0.05)  # 50ms delay
        
        print("✗ Timeout - no knob detected")
        return None

    def listen_for_button(self, timeout: int = 10) -> Optional[DetectedControl]:
        """
        Listen for any button press.
        
        Args:
            timeout: Seconds to wait for input
        
        Returns:
            DetectedControl if button detected, None if timeout
        """
        if not self.inport:
            raise RuntimeError("Not connected. Call connect() first.")
        
        # CLEAR BUFFER
        print("Clearing buffer...")
        for _ in self.inport.iter_pending():
            pass
        
        time.sleep(0.05)
        
        for _ in self.inport.iter_pending():
            pass
        
        print(f"Listening for button press... ({timeout}s timeout)")
        print("(Press a button NOW)")
        
        time.sleep(0.05)
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            msg = self.inport.poll()
            
            if msg:
                print(f"  Saw message: {msg}")
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    note_id = msg.note
                    print(f"✓ Detected button: Note {note_id}")
                    return DetectedControl(
                        control_type='button',
                        control_id=note_id,
                        message_type='note_on',
                        name=f"Button Note{note_id}"
                    )
            
            time.sleep(0.05)
        
        print("✗ Timeout - no button detected")
        return None  

    def get_all_controls(self, duration: int = 5) -> Dict[str, List[int]]:
        """
        Monitor all MIDI activity for a duration and return what was detected.
        
        Useful for manual selection dropdowns.
        
        Args:
            duration: Seconds to monitor
        
        Returns:
            Dict with 'knobs' and 'buttons' lists of control IDs
        """
        if not self.inport:
            raise RuntimeError("Not connected. Call connect() first.")
        
        print(f"Monitoring all MIDI activity for {duration}s...")
        print("Move all knobs and press all buttons you want to use!")
        
        knobs = set()
        buttons = set()
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            msg = self.inport.poll()
            
            if msg:
                if msg.type == 'control_change':
                    knobs.add(msg.control)
                    print(f"  Found knob: CC {msg.control}")
                
                elif msg.type == 'note_on' and msg.velocity > 0:
                    buttons.add(msg.note)
                    print(f"  Found button: Note {msg.note}")
            
            time.sleep(0.01)
        
        result = {
            'knobs': sorted(list(knobs)),
            'buttons': sorted(list(buttons))
        }
        
        print(f"\n✓ Found {len(result['knobs'])} knobs, {len(result['buttons'])} buttons")
        return result
    
    def test_control(self, control: DetectedControl, duration: int = 3) -> bool:
        """
        Test if a control is responding.
        
        Args:
            control: The control to test
            duration: How long to listen
        
        Returns:
            True if control sent messages
        """
        if not self.inport:
            raise RuntimeError("Not connected. Call connect() first.")
        
        print(f"Testing {control.name}... ({duration}s)")
        
        start_time = time.time()
        detected = False
        
        while time.time() - start_time < duration:
            msg = self.inport.poll()
            
            if msg:
                if (msg.type == control.message_type and 
                    (msg.type == 'control_change' and msg.control == control.control_id or
                     msg.type == 'note_on' and msg.note == control.control_id)):
                    detected = True
                    print(f"✓ {control.name} is responding!")
                    break
            
            time.sleep(0.01)
        
        if not detected:
            print(f"✗ {control.name} not responding")
        
        return detected
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, *args):
        self.disconnect()


# # Test script
# if __name__ == '__main__':
#     print("MIDI Detector Test")
#     print("=" * 50)
    
#     # Keep window open if running as exe or double-clicked
#     input("Press Enter to start detection...")
    
#     detector = MIDIDetector("X-TOUCH MINI")
    
#     try:
#         detector.connect()
        
#         # Test: Detect a knob
#         print("\n=== Detect Brightness Knob ===")
#         print("Turn the knob you want for brightness...")
#         brightness_knob = detector.listen_for_knob(timeout=10)
        
#         if brightness_knob:
#             print(f"\n✓ Saved: {brightness_knob}")
#         else:
#             print("\n✗ No knob detected")
        
#         # Keep window open to see results
#         input("\nPress Enter to exit...")
        
#     except Exception as e:
#         print(f"Error: {e}")
#         import traceback
#         traceback.print_exc()
#         input("\nPress Enter to exit...")
#     finally:
#         detector.disconnect()
#         print("\nDone!")