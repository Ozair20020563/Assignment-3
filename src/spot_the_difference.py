"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    SPOT THE DIFFERENCE GAME - ASSIGNMENT 3                     ║
║                                    HITI 37                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                              GROUP MEMBERS                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  1. Ozair Khalid           ID: 401294      GitHub: Ozair20020563              ║
║  2. Md Naimur Islam        ID: S397051     GitHub: Durjoy09                   ║
║  3. Jiaxuan Mai            ID: S397307     GitHub: Chloe-03011                ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Date: May 2026                                                                 ║
║                           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import random
import os
from dataclasses import dataclass
from typing import List, Tuple
from abc import ABC, abstractmethod

# ... rest of your code continues

@dataclass
class DifferenceRegion:
    x: int
    y: int
    width: int
    height: int
    difference_type: str
    found: bool = False
    
    def contains_point(self, click_x: int, click_y: int, tolerance: int = 10) -> bool:
        return (self.x - tolerance <= click_x <= self.x + self.width + tolerance and
                self.y - tolerance <= click_y <= self.y + self.height + tolerance)

class ImageAlteration(ABC):
    @abstractmethod
    def apply(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> np.ndarray:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass

class ColorShiftAlteration(ImageAlteration):
    def apply(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> np.ndarray:
        x, y, w, h = region
        roi = image[y:y+h, x:x+w].copy()
        
        # Convert to HSV for color manipulation
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV).astype(np.int16)
        
        # Random hue shift between -20 and +20 degrees (reduced to prevent overflow)
        hue_shift = random.randint(-20, 20)
        hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180
        
        # Clip values to valid range and convert back
        hsv = np.clip(hsv, 0, 255).astype(np.uint8)
        roi_altered = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        image[y:y+h, x:x+w] = roi_altered
        return image
    
    def get_name(self) -> str:
        return "Color Shift"

class BlurAlteration(ImageAlteration):
    def apply(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> np.ndarray:
        x, y, w, h = region
        roi = image[y:y+h, x:x+w]
        
        # Use smaller kernel sizes for better compatibility
        kernel_size = random.choice([3, 5])
        roi_altered = cv2.GaussianBlur(roi, (kernel_size, kernel_size), 0)
        image[y:y+h, x:x+w] = roi_altered
        return image
    
    def get_name(self) -> str:
        return "Blur"

class PixelateAlteration(ImageAlteration):
    def apply(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> np.ndarray:
        x, y, w, h = region
        roi = image[y:y+h, x:x+w]
        
        # Ensure dimensions are valid
        pixel_size = random.choice([4, 6, 8])
        small_w = max(1, w // pixel_size)
        small_h = max(1, h // pixel_size)
        
        small = cv2.resize(roi, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
        roi_altered = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        image[y:y+h, x:x+w] = roi_altered
        return image
    
    def get_name(self) -> str:
        return "Pixelate"

class ContrastAlteration(ImageAlteration):
    """New alteration type - safer than color shift for all images"""
    def apply(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> np.ndarray:
        x, y, w, h = region
        roi = image[y:y+h, x:x+w].astype(np.float32)
        
        # Adjust contrast safely
        alpha = random.uniform(0.7, 1.3)  # Contrast
        roi_altered = np.clip(roi * alpha, 0, 255).astype(np.uint8)
        image[y:y+h, x:x+w] = roi_altered
        return image
    
    def get_name(self) -> str:
        return "Contrast Change"

class SpotTheDifferenceGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Spot the Difference Game")
        self.root.geometry("1400x800")
        self.root.configure(bg='#2c3e50')
        
        self.original_image = None
        self.modified_image = None
        self.original_display = None
        self.modified_display = None
        self.difference_regions = []
        self.mistakes = 0
        self.max_mistakes = 3
        self.total_found = 0
        self.current_image_path = None
        self.game_active = True
        self.display_width = 500
        self.display_height = 400
        
        # Updated alteration types - more stable
        self.alteration_types = [
            BlurAlteration(),
            PixelateAlteration(),
            ContrastAlteration()
        ]
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = tk.Label(main_frame, text="SPOT THE DIFFERENCE", 
                               font=('Arial', 24, 'bold'), 
                               bg='#2c3e50', fg='#ecf0f1')
        title_label.pack(pady=10)
        
        control_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.load_btn = tk.Button(control_frame, text="Load Image", 
                                  command=self.load_image, font=('Arial', 12),
                                  bg='#3498db', fg='white', padx=20, pady=5)
        self.load_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.reveal_btn = tk.Button(control_frame, text="Reveal All", 
                                    command=self.reveal_differences, font=('Arial', 12),
                                    bg='#e67e22', fg='white', padx=20, pady=5,
                                    state=tk.DISABLED)
        self.reveal_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        score_frame = tk.Frame(control_frame, bg='#34495e')
        score_frame.pack(side=tk.RIGHT, padx=10)
        
        self.found_label = tk.Label(score_frame, text="Found: 0/5", 
                                    font=('Arial', 14, 'bold'),
                                    bg='#34495e', fg='#2ecc71')
        self.found_label.pack(side=tk.LEFT, padx=10)
        
        self.mistake_label = tk.Label(score_frame, text=f"Mistakes: 0/{self.max_mistakes}", 
                                      font=('Arial', 14, 'bold'),
                                      bg='#34495e', fg='#e74c3c')
        self.mistake_label.pack(side=tk.LEFT, padx=10)
        
        images_frame = tk.Frame(main_frame, bg='#2c3e50')
        images_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        original_panel = tk.Frame(images_frame, bg='#2c3e50')
        original_panel.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        
        tk.Label(original_panel, text="ORIGINAL IMAGE", font=('Arial', 14, 'bold'),
                bg='#2c3e50', fg='#3498db').pack()
        
        self.original_canvas = tk.Canvas(original_panel, width=self.display_width, 
                                         height=self.display_height, bg='#ecf0f1',
                                         highlightthickness=2, highlightbackground='#3498db')
        self.original_canvas.pack(pady=10)
        
        modified_panel = tk.Frame(images_frame, bg='#2c3e50')
        modified_panel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5)
        
        tk.Label(modified_panel, text="MODIFIED IMAGE (CLICK HERE)", font=('Arial', 14, 'bold'),
                bg='#2c3e50', fg='#e74c3c').pack()
        
        self.modified_canvas = tk.Canvas(modified_panel, width=self.display_width, 
                                         height=self.display_height, bg='#ecf0f1',
                                         highlightthickness=2, highlightbackground='#e74c3c')
        self.modified_canvas.pack(pady=10)
        
        self.modified_canvas.bind("<Button-1>", self.on_image_click)
        
        self.status_label = tk.Label(main_frame, text="Ready! Load an image to start.", 
                                     font=('Arial', 10), bg='#2c3e50', fg='#ecf0f1')
        self.status_label.pack(pady=5)
    
    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if not file_path:
            return
        
        try:
            # Load image
            self.original_image = cv2.imread(file_path)
            if self.original_image is None:
                raise ValueError("Could not load image")
            
            self.current_image_path = file_path
            
            # Create modified version
            self.create_modified_image()
            
            # Reset game state
            self.reset_game_state()
            
            # Display images
            self.display_images()
            
            # Enable buttons
            self.reveal_btn.config(state=tk.NORMAL)
            self.game_active = True
            
            self.status_label.config(text=f"Loaded: {os.path.basename(file_path)} - Find 5 differences!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            print(f"Detailed error: {e}")  # For debugging
    
    def create_modified_image(self):
        """Create a modified copy with 5 non-overlapping differences"""
        self.modified_image = self.original_image.copy()
        height, width = self.original_image.shape[:2]
        
        # Adjust region size based on image dimensions
        region_width = max(40, min(int(width * 0.1), 100))
        region_height = max(40, min(int(height * 0.1), 100))
        
        self.difference_regions = []
        attempts = 0
        max_attempts = 100
        
        while len(self.difference_regions) < 5 and attempts < max_attempts:
            # Ensure region fits within image
            x = random.randint(0, max(1, width - region_width))
            y = random.randint(0, max(1, height - region_height))
            
            # Check for overlap
            overlap = False
            for region in self.difference_regions:
                if (abs(x - region.x) < region_width and 
                    abs(y - region.y) < region_height):
                    overlap = True
                    break
            
            if not overlap:
                # Pick random alteration type
                alteration = random.choice(self.alteration_types)
                
                try:
                    # Apply alteration safely
                    self.modified_image = alteration.apply(self.modified_image, (x, y, region_width, region_height))
                    self.difference_regions.append(
                        DifferenceRegion(x, y, region_width, region_height, alteration.get_name())
                    )
                except Exception as e:
                    print(f"Alteration failed: {e}")
            
            attempts += 1
        
        # If we couldn't create 5 differences, add simple ones
        if len(self.difference_regions) < 5:
            self.add_simple_differences()
    
    def add_simple_differences(self):
        """Add simple brightness differences as fallback"""
        height, width = self.original_image.shape[:2]
        region_size = 50
        
        while len(self.difference_regions) < 5:
            x = random.randint(0, max(1, width - region_size))
            y = random.randint(0, max(1, height - region_size))
            
            overlap = False
            for region in self.difference_regions:
                if (abs(x - region.x) < region_size and 
                    abs(y - region.y) < region_size):
                    overlap = True
                    break
            
            if not overlap:
                # Simple brightness change
                roi = self.modified_image[y:y+region_size, x:x+region_size]
                brighter = np.clip(roi.astype(np.float32) * 1.2, 0, 255).astype(np.uint8)
                self.modified_image[y:y+region_size, x:x+region_size] = brighter
                self.difference_regions.append(
                    DifferenceRegion(x, y, region_size, region_size, "Brightness")
                )
    
    def reset_game_state(self):
        for region in self.difference_regions:
            region.found = False
        self.mistakes = 0
        self.total_found = 0
        self.game_active = True
        self.update_score_display()
        
        # Clear circles from canvases
        self.original_canvas.delete("circle")
        self.modified_canvas.delete("circle")
    
    def display_images(self):
        # Display original image
        self.original_display = self.resize_image(self.original_image, self.display_width, self.display_height)
        self.original_canvas.delete("all")
        self.original_canvas.create_image(self.display_width // 2, self.display_height // 2,
                                          anchor=tk.CENTER, image=self.original_display)
        
        # Display modified image
        self.modified_display = self.resize_image(self.modified_image, self.display_width, self.display_height)
        self.modified_canvas.delete("all")
        self.modified_canvas.create_image(self.display_width // 2, self.display_height // 2,
                                          anchor=tk.CENTER, image=self.modified_display)
    
    def resize_image(self, image, target_width, target_height):
        height, width = image.shape[:2]
        scale_w = target_width / width
        scale_h = target_height / height
        scale = min(scale_w, scale_h)
        
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        resized = cv2.resize(image, (new_width, new_height))
        rgb_image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        return ImageTk.PhotoImage(pil_image)
    
    def on_image_click(self, event):
        if not self.game_active or self.modified_image is None:
            return
        
        # Get click coordinates in image space
        img_height, img_width = self.modified_image.shape[:2]
        scale_w = self.display_width / img_width
        scale_h = self.display_height / img_height
        scale = min(scale_w, scale_h)
        
        displayed_width = int(img_width * scale)
        displayed_height = int(img_height * scale)
        
        offset_x = (self.display_width - displayed_width) // 2
        offset_y = (self.display_height - displayed_height) // 2
        
        img_x = int((event.x - offset_x) / scale)
        img_y = int((event.y - offset_y) / scale)
        
        # Check if click is within image bounds
        if img_x < 0 or img_y < 0 or img_x >= img_width or img_y >= img_height:
            return
        
        # Check each unfound difference
        found_region = None
        for region in self.difference_regions:
            if not region.found and region.contains_point(img_x, img_y):
                found_region = region
                break
        
        if found_region:
            # Correct guess
            found_region.found = True
            self.total_found += 1
            self.draw_circle_on_both(found_region, "red")
            self.update_score_display()
            self.status_label.config(text=f"Found! ({self.total_found}/5) - Type: {found_region.difference_type}")
            
            if self.total_found == 5:
                self.game_active = False
                messagebox.showinfo("Congratulations!", f"You found all 5 differences!\nMistakes: {self.mistakes}")
                self.status_label.config(text="Perfect! Load another image to continue!")
        else:
            # Wrong guess
            if self.mistakes < self.max_mistakes:
                self.mistakes += 1
                self.update_score_display()
                self.status_label.config(text=f"Wrong! Mistakes: {self.mistakes}/{self.max_mistakes}")
                
                if self.mistakes >= self.max_mistakes:
                    self.game_active = False
                    messagebox.showwarning("Game Over", f"You made 3 mistakes!\nFound {self.total_found}/5 differences.\nLoad a new image to try again.")
                    self.status_label.config(text="Game Over! Load a new image.")
    
    def draw_circle_on_both(self, region, color):
        img_height, img_width = self.original_image.shape[:2]
        scale_w = self.display_width / img_width
        scale_h = self.display_height / img_height
        scale = min(scale_w, scale_h)
        
        displayed_width = int(img_width * scale)
        displayed_height = int(img_height * scale)
        
        offset_x = (self.display_width - displayed_width) // 2
        offset_y = (self.display_height - displayed_height) // 2
        
        center_x = region.x + region.width // 2
        center_y = region.y + region.height // 2
        
        canvas_x = int(center_x * scale + offset_x)
        canvas_y = int(center_y * scale + offset_y)
        
        radius = max(20, int(min(region.width, region.height) * scale / 2))
        
        self.original_canvas.create_oval(canvas_x - radius, canvas_y - radius,
                                         canvas_x + radius, canvas_y + radius,
                                         outline=color, width=3, tags="circle")
        self.modified_canvas.create_oval(canvas_x - radius, canvas_y - radius,
                                         canvas_x + radius, canvas_y + radius,
                                         outline=color, width=3, tags="circle")
    
    def reveal_differences(self):
        if self.modified_image is None:
            return
        
        revealed_count = 0
        for region in self.difference_regions:
            if not region.found:
                self.draw_circle_on_both(region, "blue")
                revealed_count += 1
        
        if revealed_count > 0:
            self.game_active = False
            self.status_label.config(text=f"Revealed {revealed_count} differences! Load a new image.")
            self.reveal_btn.config(state=tk.DISABLED)
        else:
            self.status_label.config(text="All differences already found!")
    
    def update_score_display(self):
        self.found_label.config(text=f"Found: {self.total_found}/5")
        self.mistake_label.config(text=f"Mistakes: {self.mistakes}/{self.max_mistakes}")

if __name__ == "__main__":
    root = tk.Tk()
    game = SpotTheDifferenceGame(root)
    root.mainloop()