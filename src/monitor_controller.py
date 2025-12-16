"""Hardware abstraction for DDC/CI monitor control"""

class MonitorController:
    """Represents the physical monitor and its capabilities"""
    
    def __init__(self, monitor_name: str, vcp_codes: dict):
        self.monitor_name = monitor_name
        self.vcp_codes = vcp_codes  # Loaded from vcp_codes.json
        self._validate_ddc_connection()
    
    def set_brightness(self, value: int) -> bool:
        """Set brightness (0-100)"""
        pass
    
    def set_blue_gain(self, value: int) -> bool:
        """Set blue channel gain (0-100)"""
        pass
    
    def toggle_hdr(self) -> bool:
        """Toggle HDR mode"""
        pass
    
    def cycle_local_dimming(self) -> str:
        """Cycle through local dimming modes, return current mode"""
        pass
    
    def get_current_state(self) -> dict:
        """Query current monitor settings"""
        pass