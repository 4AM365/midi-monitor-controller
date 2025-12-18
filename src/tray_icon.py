# src/tray_icon.py
"""System tray icon for Monitor Controller"""

import pystray
from PIL import Image, ImageDraw
import threading

class TrayIcon:
    """System tray icon with menu"""
    
    def __init__(self, on_exit_callback=None):
        self.on_exit_callback = on_exit_callback
        self.icon = None
        self.running = False
    
    def create_icon_image(self):
        """Create a simple icon image (circle with 'M')"""
        # Create 64x64 image
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='black')
        draw = ImageDraw.Draw(image)
        
        # Draw blue circle
        draw.ellipse([8, 8, 56, 56], fill='#0078D4', outline='white', width=2)
        
        # Draw 'M' in center (simple representation)
        draw.text((20, 18), 'M', fill='white', font=None)
        
        return image
    
    def start(self):
        """Start the tray icon in background thread"""
        self.running = True
        thread = threading.Thread(target=self._run_icon, daemon=True)
        thread.start()
    
    def _run_icon(self):
        """Run the tray icon (blocking)"""
        # Create menu (simple version - no dynamic status)
        menu = pystray.Menu(
            pystray.MenuItem("Monitor Controller", None, enabled=False),  # Title
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Status: Running", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self._on_exit)
        )
        
        # Create icon
        self.icon = pystray.Icon(
            "monitor_controller",
            self.create_icon_image(),
            "Monitor Controller - Running",
            menu
        )
        
        # Run (blocking)
        self.icon.run()
    
    def _on_exit(self, icon, item):
        """Handle exit menu item"""
        self.running = False
        self.icon.stop()
        
        if self.on_exit_callback:
            self.on_exit_callback()
    
    def stop(self):
        """Stop the tray icon"""
        if self.icon:
            self.icon.stop()