import cv2
import numpy as np

class sprite_detector:

    def __init__(self):
        self.left = 0
        self.top = 0
        self.right = 0
        self.bottom = 0
        self.isIReady = False

    def analyze(self, image, frame_number: int):
        '''
        Analyzes the image to detect sprites. If the game area projection is not yet found,
        it will try to find it. Otherwise, it will crop the image to the game area and detect sprites in it.
        
        Args:
            image (MatLike): current frame of the game to be analyzed
            frame_number (int): number of the current frame within the video
        '''

        if self.isIReady:
            image = image[self.top:self.bottom, self.left:self.right]
            image = self.normalize(image)
            self.detect(image, frame_number)
            return
        else:
            self.find_game_area_projection(image, frame_number)
            if not self.isIReady: return
            image = image[self.top:self.bottom, self.left:self.right]
            cv2.imwrite("cropped.png", image) # Save the cropped image for debugging
            return

    def find_game_area_projection(self, image: np.ndarray, frame_number: int, threshold: int = 20):
        '''
        Attempts to find the borders of the game area projection in the given image by analyzing the mean pixel values of rows and columns.
        If the borders are found, it will set the isIReady flag to True and store the coordinates of the borders for later use.
        
        Args:
            image (MatLike): current frame of the game to be analyzed
            frame_number (int): number of the current frame within the video
            threshold (int): light value threshold to determine the borders of the game area projection
        '''

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        col_mean = np.mean(gray, axis=0)
        row_mean = np.mean(gray, axis=1)

        cols = np.where(col_mean > threshold)[0]
        rows = np.where(row_mean > threshold)[0]

        if len(cols) == 0 or len(rows) == 0:
            return
        
        cropped_gray = gray[rows[0]:rows[-1], cols[0]:cols[-1]]
        cropped_gray = cv2.resize(cropped_gray, (256, 224))
        
        title_screen = cv2.imread("./ressources/title_screen.png", cv2.IMREAD_GRAYSCALE)
        if title_screen is None:
            print("Error: Could not load title screen image")
            return
        
        result = cv2.matchTemplate(cropped_gray, title_screen, cv2.TM_CCOEFF_NORMED)
        location = np.where(result >= 0.8)
        if len(location[0]) == 0:
            print(f"nothing frame {frame_number} with accuracy = {result.max()}")
            return

        print (f"Found title screen at frame {frame_number} with accuracy = {result[location[0][0], location[1][0]]}")
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
   
    def detect(self, image, frame_number: int):
        """
        Detect sprites in an image using template matching.
        
        Args:
            image (MatLike): Normalized image in which to detect sprites (grayscale, 256x224)
            frame_number (int): number of the current frame within the video
        """
       
        # Load the template (goomba1.png)
        template_path = "./ressources/goomba1.png"
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"Error: Could not load template from {template_path}")
            return
        
        # Perform template matching
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        
        # Find locations where the match is above the threshold (0.8)
        threshold = 0.8
        locations = np.where(result >= threshold)
        
        # Print results
        if len(locations[0]) == 0:
            return
        else:
            print(f"Found {len(locations[0])} sprite(s) at frame {frame_number} with accuracy >= {threshold}")
            for i, (y, x) in enumerate(zip(locations[0], locations[1])):
                accuracy = result[y, x]
                print(f"  Sprite {i+1}: Position ({x}, {y}), Accuracy: {accuracy:.4f}")