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

def load_dead_template() -> np.ndarray:
    """Load the Mario dead sprite template."""
    path = "./ressources/sprite_templates/mario/mario_dead.png"
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise RuntimeError("Could not load Mario dead template")
    return image

def load_title_screen_template() -> np.ndarray:
    """Load the title screen sprite template."""
    path = "./ressources/sprite_templates/title_screen.png"
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise RuntimeError("Could not load title screen template")
    return image

def load_mario_templates() -> List[np.ndarray]:
    """Load all Mario sprite templates from resources/sprite_templates/mario directory."""
    templates = []
    directory = "./ressources/sprite_templates/mario"
    sprites = ["head_small.png", "head_big.png", "head_fire.png", "jump_big.png", "jump_fire.png"]
    
    for sprite in sprites:
        path = os.path.join(directory, sprite)
        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if image is not None:
            templates.append(image)
        else:
            raise RuntimeError(f"Could not load Mario template: {sprite}")
    
    return templates

def load_blinking_templates() -> List[np.ndarray]:
    """Load all blinking sprite templates from resources/sprite_templates/blinking directory."""
    templates = []
    directory = "./ressources/sprite_templates/blinking"
    
    if not os.path.exists(directory):
        return templates
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        if os.path.isfile(filepath):
            image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
            if image is not None:
                templates.append(image)
    
    return templates

def load_other_templates() -> List[ImageTemplate]:
    """Load other sprite templates from resources/sprite_templates/other directory."""
    templates = []
    directory = "./ressources/sprite_templates/other"
    
    if not os.path.exists(directory):
        return templates
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        if os.path.isfile(filepath):
            image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
            if image is not None:
                name = os.path.splitext(filename)[0].replace("_", " ").replace("1", "").replace("2", "").replace("3", "")
                templates.append(ImageTemplate(name=name, image=image))
    
    return templates