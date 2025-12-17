# src/virtual_knob.py
"""Virtual knob that maintains position and handles limits"""

class VirtualKnob:
    """
    Represents a virtual knob position with min/max limits.
    
    Args:
        name: Descriptive name for logging
        initial: Starting position
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive, hard stop)
    """
    
    def __init__(self, name: str, initial: int, min_val: int, max_val: int):
        self.name = name
        self.position = initial
        self.min = min_val
        self.max = max_val
    
    def adjust(self, delta: int) -> tuple[int, bool]:
        """
        Adjust position by delta, with clamping.
        
        Args:
            delta: Change amount (positive or negative)
        
        Returns:
            (new_position, hit_limit)
            - new_position: The updated position
            - hit_limit: True if we hit min or max boundary
        """
        old_position = self.position
        
        # Apply delta with clamping
        self.position = max(self.min, min(self.max, self.position + delta))
        
        # Check if we hit a limit
        hit_limit = (self.position != old_position + delta) and (delta != 0)
        
        return self.position, hit_limit
    
    def set(self, value: int) -> int:
        """
        Set position directly (useful for initialization).
        
        Args:
            value: Target position
        
        Returns:
            Clamped position
        """
        self.position = max(self.min, min(self.max, value))
        return self.position
    
    def __repr__(self):
        return f"VirtualKnob({self.name}, {self.position}/{self.max})"