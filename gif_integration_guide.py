#!/usr/bin/env python3
"""
Integration example for adding animated GIF to BAHI-KHATA app
"""

import tkinter as tk
from PIL import Image, ImageTk
import os

class AnimatedBackground:
    """Class to handle animated GIF backgrounds or decorative elements"""
    
    def __init__(self, parent, gif_path, x=0, y=0, width=None, height=None, alpha=0.3):
        self.parent = parent
        self.gif_path = gif_path
        self.x = x
        self.y = y
        self.alpha = alpha  # Transparency level (0.0 = transparent, 1.0 = opaque)
        
        try:
            # Load and process GIF
            self.gif = Image.open(gif_path)
            self.frames = []
            
            # Extract frames
            while True:
                try:
                    frame = self.gif.copy()
                    if width and height:
                        frame = frame.resize((width, height), Image.Resampling.LANCZOS)
                    
                    # Apply transparency if needed
                    if alpha < 1.0:
                        frame = frame.convert("RGBA")
                        # Apply alpha to all pixels
                        data = frame.getdata()
                        new_data = []
                        for item in data:
                            if len(item) == 4:  # RGBA
                                new_data.append((item[0], item[1], item[2], int(item[3] * alpha)))
                            else:  # RGB
                                new_data.append(item + (int(255 * alpha),))
                        frame.putdata(new_data)
                    
                    self.frames.append(ImageTk.PhotoImage(frame))
                    self.gif.seek(len(self.frames))
                except EOFError:
                    break
            
            # Create label for animation
            self.label = tk.Label(parent, bg=parent['bg'] if hasattr(parent, '__getitem__') else 'white')
            self.current_frame = 0
            self.is_playing = True
            
            # Position the GIF
            self.label.place(x=x, y=y)
            
            # Start animation
            self.animate()
            
        except Exception as e:
            print(f"Error loading GIF: {e}")
            self.frames = []
            self.label = None
    
    def animate(self):
        if self.is_playing and self.frames and self.label:
            try:
                self.label.config(image=self.frames[self.current_frame])
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.parent.after(150, self.animate)  # Adjust speed here
            except tk.TclError:
                # Widget was destroyed
                pass
    
    def hide(self):
        if self.label:
            self.label.place_forget()
    
    def show(self):
        if self.label:
            self.label.place(x=self.x, y=self.y)

# Function to add to your app.py
def add_animated_elements_to_app(app_instance):
    """
    Add animated GIF elements to your BAHI-KHATA app
    Call this function in your app's __init__ or main window setup
    """
    
    # Example 1: Loading animation (bottom right corner)
    loading_gif_path = "assets/loading.gif"
    if os.path.exists(loading_gif_path):
        app_instance.loading_animation = AnimatedBackground(
            app_instance.root, 
            loading_gif_path, 
            x=app_instance.root.winfo_width() - 120, 
            y=app_instance.root.winfo_height() - 120,
            width=100, 
            height=100,
            alpha=0.7
        )
    
    # Example 2: Decorative animation (top right corner)
    decoration_gif_path = "assets/coins.gif"  # Money/coins animation
    if os.path.exists(decoration_gif_path):
        app_instance.decoration_animation = AnimatedBackground(
            app_instance.root, 
            decoration_gif_path, 
            x=app_instance.root.winfo_width() - 200, 
            y=50,
            width=150, 
            height=100,
            alpha=0.5
        )
    
    # Example 3: Welcome screen animation (center)
    welcome_gif_path = "assets/welcome.gif"
    if os.path.exists(welcome_gif_path):
        app_instance.welcome_animation = AnimatedBackground(
            app_instance.root, 
            welcome_gif_path, 
            x=app_instance.root.winfo_width() // 2 - 100, 
            y=app_instance.root.winfo_height() // 2 - 100,
            width=200, 
            height=200,
            alpha=0.8
        )

# Example integration with your existing app
def integrate_with_existing_app():
    """
    Example of how to modify your existing app.py to include animated GIFs
    """
    
    # Add this to your BookkeepingApp class __init__ method:
    """
    # After setting up your main window, add:
    self.setup_animated_elements()
    """
    
    # Add this method to your BookkeepingApp class:
    """
    def setup_animated_elements(self):
        # Create assets directory if it doesn't exist
        if not os.path.exists('assets'):
            os.makedirs('assets')
        
        # Add loading animation for when processing transactions
        loading_path = 'assets/loading.gif'
        if os.path.exists(loading_path):
            self.loading_gif = AnimatedBackground(
                self.root, loading_path, 
                x=self.root.winfo_width() - 150, 
                y=self.root.winfo_height() - 150,
                width=120, height=120, alpha=0.6
            )
            self.loading_gif.hide()  # Hide initially
        
        # Add decorative elements
        decoration_path = 'assets/money.gif'
        if os.path.exists(decoration_path):
            self.decoration_gif = AnimatedBackground(
                self.root, decoration_path,
                x=50, y=50,
                width=100, height=100, alpha=0.4
            )
    
    def show_loading(self):
        if hasattr(self, 'loading_gif'):
            self.loading_gif.show()
    
    def hide_loading(self):
        if hasattr(self, 'loading_gif'):
            self.loading_gif.hide()
    """

if __name__ == "__main__":
    print("This is an integration example.")
    print("To use animated GIFs in your BAHI-KHATA app:")
    print("1. Install Pillow: pip install Pillow")
    print("2. Add GIF files to an 'assets' directory")
    print("3. Use the AnimatedBackground class in your app")
    print("4. Call the integration functions in your app setup")
