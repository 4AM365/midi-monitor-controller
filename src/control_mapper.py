from virtual_knob import VirtualKnob
from midi_handler import MIDIHandler
from monitor_controller import MonitorController
from config import Config

class ControlMapper:
    """Maps MIDI controls to monitor actions"""    
    def __init__(self, midi: MIDIHandler, monitor: MonitorController, config: Config):
        self.midi = midi
        self.monitor = monitor
        self.config = config
        
        # Virtual knobs
        self.brightness = VirtualKnob("Brightness", 75, 0, 100)
        self.night_mode = VirtualKnob("Night Mode", 100, 0, 100)
        self.mappings = config.controls
        
        # Button states
        self.local_dimming_enabled = True
        self.hdr_enabled = False
        
        # Night mode discrete steps (5 levels)
        self.night_mode_steps = [0, 25, 50, 75, 100]
        self.current_night_mode_step = 100  # Start at calibrated

    def handle_event(self, event):
        # Dynamic routing based on config
        for function, mapping in self.mappings.items():
            if event.control_id == mapping['control_id']:
                self._handle_function(function, event)
    
    def initialize(self):
        """Sync virtual knobs with actual monitor state"""
        print("Initializing control mapper...")
        
        # Read current monitor settings
        current_brightness = self.monitor.get_brightness()
        if current_brightness is not None:
            self.brightness.set(current_brightness)
            print(f"  Brightness: {current_brightness}")
        
        # Reset night mode
        if self.config.always_start_calibrated:
            self.night_mode.set(100)
            self.monitor.set_night_mode(100)
            self.current_night_mode_step = 100
            print(f"Night mode: 100 (reset to calibrated)")
        else:
            current_blue = self.monitor.get_blue_gain()
            if current_blue is not None:
                self.night_mode.set(current_blue)
                self.current_night_mode_step = self._get_night_mode_step(current_blue)
                print(f"Night mode: {current_blue}")
        
        # Read local dimming state (NEW)
        current_dimming = self.monitor.get_local_dimming()
        if current_dimming is not None:
            self.local_dimming_enabled = current_dimming
            print(f"  Local dimming: {'ON' if current_dimming else 'OFF'}")
        else:
            # Couldn't read - default to ON and set it
            self.local_dimming_enabled = True
            self.monitor.set_local_dimming(True)
            print(f"Local dimming: ON (default)")
        
        # Update LED feedback
        self._update_leds()
        
        print("Initialized")
    
    def _get_night_mode_step(self, value: int) -> int:
        """Map continuous value (0-100) to nearest discrete step"""
        # Find closest step
        closest_step = min(self.night_mode_steps, key=lambda x: abs(x - value))
        return closest_step
    
    def handle_brightness_knob(self, delta: int):
        """Handle brightness knob adjustment"""
        new_val, hit_limit = self.brightness.adjust(delta)
        
        # Send to monitor
        self.monitor.set_brightness(new_val)
        
        # Update LED ring
        led_pos = int((new_val / 100) * 11)
        self.midi.set_led_ring(self.config.knob_brightness, led_pos)
    
    def handle_night_mode_knob(self, delta: int):
        """Handle night mode (warm color shift) knob adjustment"""
        # Update virtual knob position (smooth LED movement)
        new_val, hit_limit = self.night_mode.adjust(delta)
        
        # Determine which discrete step we're in
        new_step = self._get_night_mode_step(new_val)
        
        # Only send DDC command if we changed steps
        if new_step != self.current_night_mode_step:
            self.monitor.set_night_mode(new_step)
            self.current_night_mode_step = new_step
            
            # Print step change
            step_names = {
                100: "Calibrated (6500K)",
                75: "Slightly Warm (5500K)",
                50: "Warm (4500K)",
                25: "Very Warm (3500K)",
                0: "Candlelight (2700K)"
            }
            print(f"Night Mode: {step_names.get(new_step, new_step)}")
        
        # Update LED ring (always - shows smooth position between steps)
        led_pos = int((new_val / 100) * 11)
        self.midi.set_led_ring(self.config.knob_night_mode, led_pos)
        
        # Calibrated feedback at hard stop
        if hit_limit and new_val == 100:
            print("🔵 CALIBRATED - Hard stop reached")
    

    def handle_local_dimming_button(self):
        
        self.local_dimming_enabled = not self.local_dimming_enabled
        
        
        result = self.monitor.set_local_dimming(self.local_dimming_enabled)
        
        # Update button LED
        self.midi.set_button_led(self.config.button_local_dimming, self.local_dimming_enabled)
        
        status = "ON" if self.local_dimming_enabled else "OFF"
        print(f"Local Dimming: {status}")
    
    def handle_hdr_button(self):
        """Toggle HDR (placeholder)"""
        self.hdr_enabled = False
        
        # Update button LED
        self.midi.set_button_led(self.config.button_hdr, self.hdr_enabled)
        
        status = "ON" if self.hdr_enabled else "OFF"
        print(f"HDR Toggle: {status} (not yet implemented)")
    
    def handle_event(self, event):
        """Route MIDI event to appropriate handler"""
        if event.control_type == 'knob':
            if event.control_id == self.config.knob_brightness:
                self.handle_brightness_knob(event.delta)
            
            elif event.control_id == self.config.knob_night_mode:
                self.handle_night_mode_knob(event.delta)
            
            else:
                print(f"Unmapped knob: CC {event.control_id}")
        
        elif event.control_type == 'button':
            if event.control_id == self.config.button_local_dimming:
                self.handle_local_dimming_button()
            
            elif event.control_id == self.config.button_hdr:
                self.handle_hdr_button()
            
            else:
                print(f"Unmapped button: Note {event.control_id}")
    
    def _update_leds(self):
        """Update all LED indicators"""
        brightness_led = int((self.brightness.position / 100) * 11)
        self.midi.set_led_ring(self.config.knob_brightness, brightness_led)
        
        night_led = int((self.night_mode.position / 100) * 11)
        self.midi.set_led_ring(self.config.knob_night_mode, night_led)
        
        self.midi.set_button_led(self.config.button_local_dimming, self.local_dimming_enabled)
        self.midi.set_button_led(self.config.button_hdr, self.hdr_enabled)