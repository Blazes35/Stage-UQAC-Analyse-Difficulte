import cv2
import os
import numpy as np
from dataclasses import dataclass
from typing import List

@dataclass
class ImageTemplate:
    name: str
    image: np.ndarray

def load_levels_templates() -> List[ImageTemplate]:
    """Load all sprite template images from resources/sprite_templates/levels directory."""
    templates = []
    directory = "./ressources/sprite_templates/levels"
    
    if not os.path.exists(directory):
        return templates
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        if os.path.isfile(filepath):
            image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
            if image is not None:
                name = os.path.splitext(filename)[0]
                templates.append(ImageTemplate(name=name, image=image))
    
    return templates