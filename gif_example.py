#!/usr/bin/env python3
"""
Example of adding an animated GIF to Tkinter using PIL (Pillow)
"""

import tkinter as tk
from PIL import Image, ImageTk
import os

class AnimatedGIF:
    def __init__(self, parent, gif_path, width=None, height=None):
        self.parent = parent
        self.gif_path = gif_path
        
        # Load the GIF
        self.gif = Image.open(gif_path)
        self.frames = []
        
        # Extract all frames from the GIF
        try:
            while True:
                frame = self.gif.copy()
                if width and height:
                    frame = frame.resize((width, height), Image.Resampling.LANCZOS)
                self.frames.append(ImageTk.PhotoImage(frame))
                self.gif.seek(len(self.frames))  # Go to next frame
        except EOFError:
            pass  # End of frames
        
        # Create label to display the GIF
        self.label = tk.Label(parent)
        self.current_frame = 0
        self.is_playing = True
        
        # Start animation
        self.animate()
    
    def animate(self):
        if self.is_playing and self.frames:
            # Display current frame
            self.label.config(image=self.frames[self.current_frame])
            
            # Move to next frame
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            
            # Schedule next frame (adjust delay as needed - 100ms = 10 FPS)
            self.parent.after(100, self.animate)
    
    def play(self):
        self.is_playing = True
        self.animate()
    
    def pause(self):
        self.is_playing = False
    
    def pack(self, **kwargs):
        self.label.pack(**kwargs)
    
    def grid(self, **kwargs):
        self.label.grid(**kwargs)
    
    def place(self, **kwargs):
        self.label.place(**kwargs)

# Example usage
def test_animated_gif():
    root = tk.Tk()
    root.title("Animated GIF Example")
    root.geometry("600x400")
    
    # Add a title
    title = tk.Label(root, text="BAHI-KHATA with Animated GIF", 
                     font=('Arial', 16, 'bold'))
    title.pack(pady=10)
    
    # Check if GIF file exists (you'll need to add your own GIF)
    gif_path = "loading.gif"  # Replace with your GIF path
    
    if os.path.exists(gif_path):
        # Add animated GIF
        animated_gif = AnimatedGIF(root, gif_path, width=200, height=150)
        animated_gif.pack(pady=20)
        
        # Control buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        
        play_btn = tk.Button(button_frame, text="Play", 
                            command=animated_gif.play)
        play_btn.pack(side='left', padx=5)
        
        pause_btn = tk.Button(button_frame, text="Pause", 
                             command=animated_gif.pause)
        pause_btn.pack(side='left', padx=5)
    else:
        # Show message if GIF not found
        message = tk.Label(root, text=f"GIF file '{gif_path}' not found.\n"
                                     "Please add a GIF file to test this feature.",
                          fg='red', font=('Arial', 12))
        message.pack(pady=50)
    
    root.mainloop()

if __name__ == "__main__":
    test_animated_gif()
