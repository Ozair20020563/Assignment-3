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
        roi = image[y:y+h, x:x+w]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        hue_shift = random.randint(-30, 30)
        hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180
        roi_altered = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        image[y:y+h, x:x+w] = roi_altered
        return image
    
    def get_name(self) -> str:
        return "Color Shift"

class BlurAlteration(ImageAlteration):
    def apply(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> np.ndarray:
        x, y, w, h = region
        roi = image[y:y+h, x:x+w]
        kernel_size = random.choice([3, 5, 7])
        roi_altered = cv2.GaussianBlur(roi, (kernel_size, kernel_size), 0)
        image[y:y+h, x:x+w] = roi_altered
        return image
    
    def get_name(self) -> str:
        return "Blur"

class PixelateAlteration(ImageAlteration):
    def apply(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> np.ndarray:
        x, y, w, h = region
        roi = image[y:y+h, x:x+w]
        pixel_size = random.choice([4, 8, 12])
        small = cv2.resize(roi, (max(1, w // pixel_size), max(1, h // pixel_size)))
        roi_altered = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        image[y:y+h, x:x+w] = roi_altered
        return image
    
    def get_name(self) -> str:
        return "Pixelate"

class SpotTheDifferenceGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Spot the Difference Game")
        self.root.geometry("1400x800")
        self.root.configure(bg='#2c3e50')
        
        self.original_image = None
        self.modified_image = None
        self.difference_regions = []
        self.mistakes = 0
        self.max_mistakes = 3
        self.total_found = 0
        self.game_active = True
        self.display_width = 500
        self.display_height = 400
        
        self.alteration_types = [
            ColorShiftAlteration(),
            BlurAlteration(),
            PixelateAlteration()
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
            self.original_image = cv2.imread(file_path)
            if self.original_image is None:
                raise ValueError("Could not load image")
            
            self.create_modified_image()
            self.reset_game_state()
            self.display_images()
            self.reveal_btn.config(state=tk.NORMAL)
            self.status_label.config(text=f"Loaded: {os.path.basename(file_path)} - Find 5 differences!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def create_modified_image(self):
        self.modified_image = self.original_image.copy()
        height, width = self.original_image.shape[:2]
        
        region_width = max(30, int(width * random.uniform(0.08, 0.12)))
        region_height = max(30, int(height * random.uniform(0.08, 0.12)))
        
        self.difference_regions = []
        attempts = 0
        
        while len(self.difference_regions) < 5 and attempts < 50:
            x = random.randint(0, max(1, width - region_width))
            y = random.randint(0, max(1, height - region_height))
            
            overlap = False
            for region in self.difference_regions:
                if (abs(x - region.x) < region_width and 
                    abs(y - region.y) < region_height):
                    overlap = True
                    break
            
            if not overlap:
                alteration = random.choice(self.alteration_types)
                self.modified_image = alteration.apply(self.modified_image, (x, y, region_width, region_height))
                self.difference_regions.append(
                    DifferenceRegion(x, y, region_width, region_height, alteration.get_name())
                )
            
            attempts += 1
    
    def reset_game_state(self):
        for region in self.difference_regions:
            region.found = False
        self.mistakes = 0
        self.total_found = 0
        self.game_active = True
        self.update_score_display()
    
    def display_images(self):
        self.original_display = self.resize_image(self.original_image, self.display_width, self.display_height)
        self.original_canvas.delete("all")
        self.original_canvas.create_image(self.display_width // 2, self.display_height // 2,
                                          anchor=tk.CENTER, image=self.original_display)
        
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
        
        if img_x < 0 or img_y < 0 or img_x >= img_width or img_y >= img_height:
            return
        
        found_region = None
        for region in self.difference_regions:
            if not region.found and region.contains_point(img_x, img_y):
                found_region = region
                break
        
        if found_region:
            found_region.found = True
            self.total_found += 1
            self.draw_circle_on_both(found_region, "red")
            self.update_score_display()
            self.status_label.config(text=f"Found! ({self.total_found}/5) - Type: {found_region.difference_type}")
            
            if self.total_found == 5:
                self.game_active = False
                messagebox.showinfo("Congratulations!", f"You found all 5 differences!\nMistakes: {self.mistakes}")
        else:
            if self.mistakes < self.max_mistakes:
                self.mistakes += 1
                self.update_score_display()
                self.status_label.config(text=f"Wrong! Mistakes: {self.mistakes}/{self.max_mistakes}")
                
                if self.mistakes >= self.max_mistakes:
                    self.game_active = False
                    messagebox.showwarning("Game Over", f"3 mistakes! Found {self.total_found}/5 differences.")
    
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
                                         outline=color, width=3)
        self.modified_canvas.create_oval(canvas_x - radius, canvas_y - radius,
                                         canvas_x + radius, canvas_y + radius,
                                         outline=color, width=3)
    
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
            self.status_label.config(text=f"Revealed {revealed_count} differences!")
            self.reveal_btn.config(state=tk.DISABLED)
    
    def update_score_display(self):
        self.found_label.config(text=f"Found: {self.total_found}/5")
        self.mistake_label.config(text=f"Mistakes: {self.mistakes}/{self.max_mistakes}")

if __name__ == "__main__":
    root = tk.Tk()
    game = SpotTheDifferenceGame(root)
    root.mainloop()