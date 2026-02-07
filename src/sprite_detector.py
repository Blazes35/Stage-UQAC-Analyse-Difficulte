import cv2
import numpy as np

class sprite_detector:
   
    def detect(self, image_path):
        """
        Detect sprites in an image using template matching.
        
        Args:
            image_path (str): Path to the PNG image file
        """
        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not load image from {image_path}")
            return
        
        # Convert to grayscale (black and white)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Load the template (goomba1.png)
        template_path = "./ressources/goomba2.png"
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"Error: Could not load template from {template_path}")
            return
        
        # Perform template matching
        result = cv2.matchTemplate(gray_image, template, cv2.TM_CCOEFF_NORMED)
        
        # Find locations where the match is above the threshold (0.7)
        threshold = 0.55
        locations = np.where(result >= threshold)
        
        # Print results
        if len(locations[0]) == 0:
            print(f"No sprites detected with accuracy >= {threshold}")
        else:
            print(f"Found {len(locations[0])} sprite(s) with accuracy >= {threshold}")
            for i, (y, x) in enumerate(zip(locations[0], locations[1])):
                accuracy = result[y, x]
                print(f"  Sprite {i+1}: Position ({x}, {y}), Accuracy: {accuracy:.4f}")