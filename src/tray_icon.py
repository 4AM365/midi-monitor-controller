# src/tray_icon.py
"""System tray icon for Monitor Controller"""

import pystray
from PIL import Image, ImageDraw
import threading

class TrayIcon:
    """System tray icon with menu"""
    
    def __init__(self, on_exit_callback=None, on_setup_callback=None):
        self.on_exit_callback = on_exit_callback
        self.on_setup_callback = on_setup_callback  # NEW
        self.icon = None
        self.running = False
    
    def create_icon_image(self):
        """Create a simple icon image (circle with 'M')"""
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='black')
        draw = ImageDraw.Draw(image)
        
        # Draw blue circle
        draw.ellipse([8, 8, 56, 56], fill='#0078D4', outline='white', width=2)
        
        # Draw 'M' in center
        draw.text((20, 18), 'M', fill='white', font=None)
        
        return image
    
    def start(self):
        """Start the tray icon in background thread"""
        self.running = True
        thread = threading.Thread(target=self._run_icon, daemon=True)
        thread.start()
    
    def _run_icon(self):
        """Run the tray icon (blocking)"""
        # Create menu
        menu_items = [
            pystray.MenuItem("Monitor Controller", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Status: Running", None, enabled=False),
            pystray.Menu.SEPARATOR,
        ]
        
        # Add setup option if callback provided
        if self.on_setup_callback:
            menu_items.append(pystray.MenuItem("⚙️ Run Setup Wizard", self._on_setup))
            menu_items.append(pystray.Menu.SEPARATOR)
        
        menu_items.append(pystray.MenuItem("Exit", self._on_exit))
        
        menu = pystray.Menu(*menu_items)
        
        # Create icon
        self.icon = pystray.Icon(
            "monitor_controller",
            self.create_icon_image(),
            "Monitor Controller - Running",
            menu
        )
        
        # Run (blocking)
        self.icon.run()
    
    def _on_setup(self, icon, item):
        """Handle setup menu item"""
        if self.on_setup_callback:
            self.on_setup_callback()
    
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