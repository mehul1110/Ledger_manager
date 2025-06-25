#!/usr/bin/env python3
"""
Script to create an ICO file from an image for use as application icon.
Usage: python create_icon.py <input_image> [output_icon.ico]
"""

import sys
from PIL import Image
import os

def create_icon(input_path, output_path=None):
    """Convert an image to ICO format with multiple sizes."""
    if output_path is None:
        output_path = "frontend/app_icon.ico"
    
    try:
        # Open the image
        img = Image.open(input_path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create different sizes for the icon
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icon_images = []
        
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icon_images.append(resized)
        
        # Save as ICO
        icon_images[0].save(output_path, format='ICO', sizes=[(img.width, img.height) for img in icon_images])
        print(f"Icon created successfully: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error creating icon: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_icon.py <input_image> [output_icon.ico]")
        print("Example: python create_icon.py my_logo.png")
        sys.exit(1)
    
    input_image = sys.argv[1]
    output_icon = sys.argv[2] if len(sys.argv) > 2 else "frontend/app_icon.ico"
    
    if not os.path.exists(input_image):
        print(f"Error: Input image '{input_image}' not found!")
        sys.exit(1)
    
    success = create_icon(input_image, output_icon)
    sys.exit(0 if success else 1)
