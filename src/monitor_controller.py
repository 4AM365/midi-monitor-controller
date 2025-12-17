from monitorcontrol import get_monitors
from typing import Optional

class MonitorController:


    def get_local_dimming(self) -> Optional[bool]:
        """
        Get current local dimming state.
        
        Returns:
            True if on, False if off, None if failed
        """
        if not self.monitor:
            raise RuntimeError("Not connected. Call connect() first.")
        
        try:
            with self.monitor:
                current, _ = self.monitor.vcp.get_vcp_feature(self._vcp_codes['local_dimming'])
            return bool(current)  # 1 = True (on), 0 = False (off)
        except Exception as e:
            print(f"✗ Failed to get local dimming: {e}")
            return None
    
    def __init__(self, monitor_index: int = 0):
        """
        Args:
            monitor_index: Which monitor to control (0 = first/primary)
        """
        self.monitor_index = monitor_index
        self.monitor = None
        self._vcp_codes = {
            'brightness': 0x10,
            'contrast': 0x12,
            'red_gain': 0x16,
            'green_gain': 0x18,
            'blue_gain': 0x1A,
            'sharpness': 0x87,
            'local_dimming': 0xEA,
        }
    
    def connect(self):
        """Initialize connection to monitor"""
        monitors = get_monitors()
        
        if not monitors:
            raise RuntimeError("No DDC-capable monitors found")
        
        if self.monitor_index >= len(monitors):
            raise RuntimeError(f"Monitor index {self.monitor_index} not found. Only {len(monitors)} monitor(s) detected.")
        
        self.monitor = monitors[self.monitor_index]
        print(f"✓ Connected to monitor {self.monitor_index}")
    
    def disconnect(self):
        """Clean up monitor connection"""
        # monitorcontrol handles cleanup automatically
        self.monitor = None
    
    def set_brightness(self, value: int) -> bool:
        """Set monitor brightness with auto-reconnect on failure."""
        if not self.monitor:
            raise RuntimeError("Not connected. Call connect() first.")
        
        try:
            value = max(0, min(100, value))
            with self.monitor:
                self.monitor.vcp.set_vcp_feature(self._vcp_codes['brightness'], value)
            return True
        except Exception as e:
            # DDC failed - try reconnecting
            print(f"⚠️  DDC error, attempting reconnect: {e}")
            try:
                self.reconnect()
                # Retry the command
                with self.monitor:
                    self.monitor.vcp.set_vcp_feature(self._vcp_codes['brightness'], value)
                print("✓ Reconnected successfully")
                return True
            except Exception as e2:
                print(f"✗ Reconnect failed: {e2}")
                return False

    def reconnect(self):
        """Reconnect to monitor (after sleep/wake)"""
        self.disconnect()
        self.connect()
    
    def get_brightness(self) -> Optional[int]:
        """
        Get current brightness.
        
        Returns:
            Brightness level (0-100) or None if failed
        """
        if not self.monitor:
            raise RuntimeError("Not connected. Call connect() first.")
        
        try:
            with self.monitor:
                current, _ = self.monitor.vcp.get_vcp_feature(self._vcp_codes['brightness'])
            return current
        except Exception as e:
            print(f"✗ Failed to get brightness: {e}")
            return None

    def set_night_mode(self, intensity: int) -> bool:
        """
        Set night mode warm color shift.
        
        Args:
            intensity: Night mode intensity (0-100)
        
        Returns:
            True if successful
        """
        if not self.monitor:
            raise RuntimeError("Not connected. Call connect() first.")
        
        try:
            # Calculate RGB values
            red = 100
            green = 60 + int((intensity / 100) * 40)   # 60-100
            blue = 20 + int((intensity / 100) * 80)    # 20-100
            
            with self.monitor:
                self.monitor.vcp.set_vcp_feature(self._vcp_codes['red_gain'], red)
                self.monitor.vcp.set_vcp_feature(self._vcp_codes['green_gain'], green)
                self.monitor.vcp.set_vcp_feature(self._vcp_codes['blue_gain'], blue)
            
            return True
        except Exception as e:
            print(f"✗ Failed to set night mode: {e}")
            return False

    def get_night_mode(self) -> Optional[int]:
        """
        Get current night mode intensity (inferred from blue gain).
        
        Returns:
            Approximate intensity (0-100) or None if failed
        """
        # For simplicity, just read blue gain as proxy
        return self.get_blue_gain()
    
    
    def set_blue_gain(self, value: int) -> bool:
        """
        Set blue channel gain (for night mode).
        
        Args:
            value: Blue gain (0-100)
                  100 = normal/calibrated
                  0 = maximum warmth (no blue)
        
        Returns:
            True if successful
        """
        if not self.monitor:
            raise RuntimeError("Not connected. Call connect() first.")
        
        try:
            value = max(0, min(100, value))
            with self.monitor:
                self.monitor.vcp.set_vcp_feature(self._vcp_codes['blue_gain'], value)
            return True
        except Exception as e:
            print(f"✗ Failed to set blue gain: {e}")
            return False
    
    def get_blue_gain(self) -> Optional[int]:
        """Get current blue gain"""
        if not self.monitor:
            raise RuntimeError("Not connected. Call connect() first.")
        
        try:
            with self.monitor:
                current, _ = self.monitor.vcp.get_vcp_feature(self._vcp_codes['blue_gain'])
            return current
        except Exception as e:
            print(f"✗ Failed to get blue gain: {e}")
            return None
    
    def set_local_dimming(self, enabled: bool) -> bool:
        """
        Toggle local dimming.
        
        Args:
            enabled: True=on, False=off
        
        Returns:
            True if successful
        """
        if not self.monitor:
            raise RuntimeError("Not connected. Call connect() first.")
        
        try:
            value = 1 if enabled else 0
            with self.monitor:
                self.monitor.vcp.set_vcp_feature(self._vcp_codes['local_dimming'], value)
            return True
        except Exception as e:
            print(f"✗ Failed to set local dimming: {e}")
            return False
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, *args):
        self.disconnect()