import cv2
import os
import re
import numpy as np
from dataclasses import dataclass, field
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

@dataclass
class CompoundTemplates:
    templates : List[np.ndarray] = field(default_factory=list)
    action_name : str = ""
    cooldown : int = 60
    threshold : float = 0.8
    last_seen : int = -10000

other_data = {
    "goomba stomped": {
        "cooldown": 50,
        "threshold": 0.9
    },
    "goomba killed": {
        "cooldown": 60,
        "threshold": 0.9
    },
    "koopa killed": {
        "cooldown": 60,
        "threshold": 0.95
    },
    "jump": {
        "cooldown": 60,
        "threshold": 0.85
    },
    "mushroom": {
        "cooldown": 900,
        "threshold": 0.95
    },
    "fire flower": {
        "cooldown": 900,
        "threshold": 0.9
    },
    "star": {
        "cooldown": 3000,
        "threshold": 0.9
    },
    "coinblock hit": {
        "cooldown": 40,
        "threshold": 0.78
    }
}

def load_other_templates() -> List[CompoundTemplates]:
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
                name = os.path.splitext(filename)[0]
                name = re.sub(r"(\d+)$", "", name).replace("_", " ")
                cooldown = other_data.get(name, {}).get("cooldown", 60)
                threshold = other_data.get(name, {}).get("threshold", 0.5)
                already_exists = False
                for template in templates:
                    if template.action_name == name:
                        template.templates.append(image)
                        already_exists = True
                        break
                if not already_exists:
                    templates.append(CompoundTemplates(
                        templates=[image],
                        action_name=name,
                        cooldown=cooldown,
                        threshold=threshold
                    ))
    print(f"Loaded {len(templates)} compound templates from {directory}")
    return templates