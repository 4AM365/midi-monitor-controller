# src/setup_wizard.py
"""Setup wizard GUI for first-time configuration"""

import tkinter as tk
from tkinter import ttk, messagebox
import mido
from monitorcontrol import get_monitors
from midi_detector import MIDIDetector, DetectedControl
from config import Config
import threading

class SetupWizard:
    """Interactive setup wizard for Monitor Controller"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Monitor Controller - Setup Wizard")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Data to collect
        self.midi_device = None
        self.monitor_index = None
        self.controls = {}
        self.detector = None
        
        # Current step
        self.current_step = 0
        self.steps = [
            self.step_welcome,
            self.step_select_midi,
            self.step_select_monitor,
            self.step_detect_brightness,
            self.step_detect_night_mode,
            self.step_detect_local_dimming,
            self.step_detect_hdr,
            self.step_confirm
        ]
        
        # Main container
        self.container = tk.Frame(self.root, padx=20, pady=20)
        self.container.pack(fill="both", expand=True)
        
        # Navigation buttons
        self.nav_frame = tk.Frame(self.root)
        self.nav_frame.pack(side="bottom", fill="x", padx=20, pady=10)
        
        self.back_btn = ttk.Button(self.nav_frame, text="← Back", command=self.go_back)
        self.back_btn.pack(side="left")
        
        self.next_btn = ttk.Button(self.nav_frame, text="Next →", command=self.go_next)
        self.next_btn.pack(side="right")
        
        self.cancel_btn = ttk.Button(self.nav_frame, text="Cancel", command=self.cancel)
        self.cancel_btn.pack(side="right", padx=(0, 10))
        
        # Start wizard
        self.show_step()
    
    def clear_container(self):
        """Clear all widgets from container"""
        for widget in self.container.winfo_children():
            widget.destroy()
    
    def show_step(self):
        """Display current step"""
        self.clear_container()
        
        # Update navigation buttons
        self.back_btn.config(state="normal" if self.current_step > 0 else "disabled")
        
        # Show current step
        self.steps[self.current_step]()
    
    def go_next(self):
        """Go to next step"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.show_step()
    
    def go_back(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self.show_step()
    
    def cancel(self):
        """Cancel setup"""
        if messagebox.askyesno("Cancel Setup", "Are you sure? Configuration will not be saved."):
            if self.detector:
                self.detector.disconnect()
            self.root.quit()
    
    # ==================== STEPS ====================
    
    def step_welcome(self):
        """Step 1: Welcome"""
        tk.Label(
            self.container,
            text="Welcome to Monitor Controller Setup!",
            font=("Arial", 16, "bold")
        ).pack(pady=20)
        
        tk.Label(
            self.container,
            text="This wizard will help you configure your MIDI controller\n"
                 "to control your monitor's brightness, night mode, and more.",
            justify="center"
        ).pack(pady=10)
        
        tk.Label(
            self.container,
            text="You will need:",
            font=("Arial", 10, "bold")
        ).pack(pady=(20, 5))
        
        requirements = [
            "• A MIDI controller (keyboard, pad, knobs, etc.)",
            "• A monitor that supports DDC/CI",
            "• Both devices connected to your computer"
        ]
        
        for req in requirements:
            tk.Label(self.container, text=req, justify="left").pack(anchor="w", padx=50)
        
        tk.Label(
            self.container,
            text="\nClick 'Next' to begin!",
            font=("Arial", 10, "italic")
        ).pack(pady=20)
    
    def step_select_midi(self):
        """Step 2: Select MIDI device"""
        tk.Label(
            self.container,
            text="Select MIDI Controller",
            font=("Arial", 14, "bold")
        ).pack(pady=20)
        
        tk.Label(
            self.container,
            text="Choose your MIDI device from the list:"
        ).pack(pady=10)
        
        # Get MIDI devices
        input_ports = mido.get_input_names()
        
        if not input_ports:
            tk.Label(
                self.container,
                text="⚠️ No MIDI devices found!",
                foreground="red",
                font=("Arial", 12)
            ).pack(pady=20)
            self.next_btn.config(state="disabled")
            return
        
        self.next_btn.config(state="normal")
        
        # Radio buttons for selection
        self.midi_var = tk.StringVar(value=input_ports[0])
        
        for port in input_ports:
            ttk.Radiobutton(
                self.container,
                text=port,
                variable=self.midi_var,
                value=port
            ).pack(anchor="w", padx=50, pady=5)
        
        # Save selection for next step
        self.midi_device = self.midi_var.get()
        self.midi_var.trace('w', lambda *args: setattr(self, 'midi_device', self.midi_var.get()))
    
    def step_select_monitor(self):
        """Step 3: Select monitor"""
        tk.Label(
            self.container,
            text="Select Monitor",
            font=("Arial", 14, "bold")
        ).pack(pady=20)
        
        tk.Label(
            self.container,
            text="Choose which monitor to control:"
        ).pack(pady=10)
        
        # Get monitors
        monitors = get_monitors()
        
        if not monitors:
            tk.Label(
                self.container,
                text="⚠️ No DDC-capable monitors found!",
                foreground="red",
                font=("Arial", 12)
            ).pack(pady=20)
            self.next_btn.config(state="disabled")
            return
        
        self.next_btn.config(state="normal")
        
        # Radio buttons
        self.monitor_var = tk.IntVar(value=0)
        
        for i in range(len(monitors)):
            ttk.Radiobutton(
                self.container,
                text=f"Monitor {i}",
                variable=self.monitor_var,
                value=i
            ).pack(anchor="w", padx=50, pady=5)
        
        self.monitor_index = self.monitor_var.get()
        self.monitor_var.trace('w', lambda *args: setattr(self, 'monitor_index', self.monitor_var.get()))
    
    def step_detect_brightness(self):
        """Step 4: Detect brightness knob"""
        self._detect_control_step(
            title="Brightness Control",
            instruction="Turn the knob you want to use for BRIGHTNESS",
            control_name="brightness",
            control_type="knob"
        )
    
    def step_detect_night_mode(self):
        """Step 5: Detect night mode knob"""
        self._detect_control_step(
            title="Night Mode Control",
            instruction="Turn the knob you want to use for NIGHT MODE",
            control_name="night_mode",
            control_type="knob"
        )
    
    def step_detect_local_dimming(self):
        """Step 6: Detect local dimming button"""
        self._detect_control_step(
            title="Local Dimming Button",
            instruction="Press the button you want to use for LOCAL DIMMING",
            control_name="local_dimming",
            control_type="button"
        )
    
    def step_detect_hdr(self):
        """Step 7: Detect HDR button (optional)"""
        self._detect_control_step(
            title="HDR Toggle Button (Optional)",
            instruction="Press the button for HDR toggle, or click Skip",
            control_name="hdr_toggle",
            control_type="button",
            optional=True
        )
    
    def _detect_control_step(self, title, instruction, control_name, control_type, optional=False):
        """Generic control detection step"""
        tk.Label(
            self.container,
            text=title,
            font=("Arial", 14, "bold")
        ).pack(pady=20)
        
        tk.Label(
            self.container,
            text=instruction,
            font=("Arial", 11)
        ).pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(
            self.container,
            text="Listening... (10s timeout)",
            font=("Arial", 10),
            foreground="blue"
        )
        self.status_label.pack(pady=20)
        
        # Progress indicator
        self.progress = ttk.Progressbar(
            self.container,
            mode='indeterminate',
            length=300
        )
        self.progress.pack(pady=10)
        self.progress.start(10)
        
        # Retry button (hidden initially)
        self.retry_btn = ttk.Button(
            self.container,
            text="Try Again",
            command=lambda: self._start_detection(control_name, control_type)
        )
        
        if optional:
            ttk.Button(
                self.container,
                text="Skip",
                command=self.go_next
            ).pack(pady=5)
        
        # Disable next until detected
        if not optional:
            self.next_btn.config(state="disabled")
        
        # Auto-start detection
        self.root.after(500, lambda: self._start_detection(control_name, control_type))
    
    def _start_detection(self, control_name, control_type):
        """Start detection in background thread"""
        self.retry_btn.pack_forget()
        self.status_label.config(text=f"Listening... (10s timeout)", foreground="blue")
        self.progress.start(10)
        
        def detect():
            try:
                if not self.detector:
                    self.detector = MIDIDetector(self.midi_device)
                    self.detector.connect()
                
                if control_type == "knob":
                    detected = self.detector.listen_for_knob(timeout=10)
                else:
                    detected = self.detector.listen_for_button(timeout=10)
                
                self.root.after(0, lambda: self._detection_complete(control_name, detected))
                
            except Exception as e:
                # Capture e immediately in the lambda
                error_msg = str(e)  # Convert to string NOW
                self.root.after(0, lambda: self._detection_error(error_msg))  # Use error_msg, not e
        
        thread = threading.Thread(target=detect, daemon=True)
        thread.start()
    
    def _detection_complete(self, control_name, detected):
        """Handle detection completion"""
        self.progress.stop()
        
        if detected:
            self.controls[control_name] = {
                "type": detected.control_type,
                "control_id": detected.control_id,
                "cc_type": detected.message_type
            }
            self.status_label.config(
                text=f"✓ Detected: {detected.name}",
                foreground="green"
            )
            self.next_btn.config(state="normal")
        else:
            self.status_label.config(
                text="✗ Timeout - No control detected",
                foreground="red"
            )
            self.retry_btn.pack(pady=10)
    
    def _detection_error(self, error_msg):
        """Handle detection error"""
        self.progress.stop()
        self.status_label.config(
            text=f"✗ Error: {error_msg}",
            foreground="red"
        )
        self.retry_btn.pack(pady=10)
    
    def step_confirm(self):
        """Step 8: Confirm and save"""
        tk.Label(
            self.container,
            text="Setup Complete!",
            font=("Arial", 14, "bold")
        ).pack(pady=20)
        
        tk.Label(
            self.container,
            text="Review your configuration:"
        ).pack(pady=10)
        
        config_text = f"""MIDI Device: {self.midi_device}
Monitor: Monitor {self.monitor_index}

Controls:
"""
        for name, ctrl in self.controls.items():
            config_text += f"  • {name}: {ctrl['type'].title()} {ctrl['control_id']}\n"
        
        tk.Label(
            self.container,
            text=config_text,
            justify="left",
            font=("Courier", 9),
            bg="white",
            relief="sunken",
            padx=10,
            pady=10
        ).pack(pady=10)
        
        self.next_btn.config(text="Finish & Save", command=self.finish)
    
    def finish(self):
        """Save configuration and exit"""
        config = Config(
            midi_device=self.midi_device,
            monitor_index=self.monitor_index,
            knob_brightness=self.controls.get('brightness', {}).get('control_id', 1),
            knob_night_mode=self.controls.get('night_mode', {}).get('control_id', 2),
            button_local_dimming=self.controls.get('local_dimming', {}).get('control_id', 8),
            button_hdr=self.controls.get('hdr_toggle', {}).get('control_id', 9),
            controls=self.controls
        )
        
        config.save()
        
        messagebox.showinfo(
            "Setup Complete",
            "Configuration saved successfully!\n\nMonitor Controller is ready to use."
        )
        
        if self.detector:
            self.detector.disconnect()
        
        self.root.destroy()
    
    def run(self):
        """Run the wizard"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        self.root.mainloop()

# Test
if __name__ == '__main__':
    wizard = SetupWizard()
    wizard.run()