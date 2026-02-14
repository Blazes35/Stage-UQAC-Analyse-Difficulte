import cv2
import numpy as np

class sprite_detector:

    def __init__(self):
        self.left = 0
        self.top = 0
        self.right = 0
        self.bottom = 0
        self.isIReady = False

    def analyze(self, image_path: str):
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not load image from {image_path}")
            return None
        
        if self.isIReady:
            image = image[self.top:self.bottom, self.left:self.right]
            image = self.normalize(image)
            self.detect(image)
            return
        else:
            self.find_game_area_projection(image)
            image = image[self.top:self.bottom, self.left:self.right]
            # cv2.imwrite("cropped.png", image) # Save the cropped image for debugging
            image = self.normalize(image)
            self.detect(image)

    def find_game_area_projection(self, image: np.ndarray, threshold: int = 20):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        col_mean = np.mean(gray, axis=0)
        row_mean = np.mean(gray, axis=1)

        cols = np.where(col_mean > threshold)[0]
        rows = np.where(row_mean > threshold)[0]

        if len(cols) == 0 or len(rows) == 0:
            raise RuntimeError("Could not detect boundaries")

        self.left, self.top, self.right, self.bottom = cols[0], rows[0], cols[-1], rows[-1] 
        self.isIReady = True

    def normalize(self, image):
        """
        Normalize the image by converting it to grayscale downscaling it to 256*224 pixels like the original super mario bros game.
        
        Args:
            image (MatLinh): current frame of the game to be normalized
        """       
        # Convert to grayscale (black and white)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Resize to 256x224 pixels
        normalized_image = cv2.resize(gray_image, (256, 224))
        
        return normalized_image
   
    def detect(self, image):
        """
        Detect sprites in an image using template matching.
        
        Args:
            image (MatLike): Normalized image in which to detect sprites (grayscale, 256x224)
        """
       
        # Load the template (goomba1.png)
        template_path = "./ressources/goomba1.png"
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"Error: Could not load template from {template_path}")
            return
        
        # Perform template matching
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        
        # Find locations where the match is above the threshold (0.7)
        threshold = 0.8
        locations = np.where(result >= threshold)
        
        # Print results
        if len(locations[0]) == 0:
            print(f"No sprites detected with accuracy >= {threshold}")
        else:
            print(f"Found {len(locations[0])} sprite(s) with accuracy >= {threshold}")
            for i, (y, x) in enumerate(zip(locations[0], locations[1])):
                accuracy = result[y, x]
                print(f"  Sprite {i+1}: Position ({x}, {y}), Accuracy: {accuracy:.4f}")