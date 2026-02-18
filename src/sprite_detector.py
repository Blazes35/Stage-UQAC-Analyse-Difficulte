import cv2
import numpy as np
from typing import cast

class SpriteDetector:
    """
    Detects sprites in video frames using template matching.

    The detector first identifies the projected game area inside the full frame.
    Once the projection is found, subsequent frames are cropped, normalized to
    the original NES resolution (256x224), and analyzed for sprite presence.
    """

    NORMALIZED_WIDTH = 256
    NORMALIZED_HEIGHT = 224
    MATCH_THRESHOLD = 0.5
    PROJECTION_THRESHOLD = 50

    TITLE_SCREEN_PATH = "./ressources/title_screen.png"
    GOOMBA_TEMPLATE_PATH = "./ressources/goomba1.png"

    def __init__(self):
        """
        Initializes the detector and preloads required templates.

        Template loading is performed once to avoid repeated disk I/O
        during high-frequency frame analysis.
        """
        self.left = 0
        self.top = 0
        self.right = 0
        self.bottom = 0
        self.is_ready = False
        self.last_death_frame = -1
        self.death_count = 0

        title_screen = cv2.imread(
            self.TITLE_SCREEN_PATH,
            cv2.IMREAD_GRAYSCALE
        )
        if title_screen is None:
            raise RuntimeError("Could not load title screen template")
        self.title_screen = cast(np.ndarray, title_screen)

        goomba_template = cv2.imread(
            self.GOOMBA_TEMPLATE_PATH,
            cv2.IMREAD_GRAYSCALE
        )
        if goomba_template is None:
            raise RuntimeError("Could not load goomba template")
        self.goomba_template = cast(np.ndarray, goomba_template)

        mario_dead_template = cv2.imread(
            "./ressources/mario_dead.png",
            cv2.IMREAD_GRAYSCALE
        )
        if mario_dead_template is None:
            raise RuntimeError("Could not load mario dead template")
        self.mario_dead_template = cast(np.ndarray, mario_dead_template)

    def analyze(self, image: np.ndarray, frame_number: int):
        """
        Analyzes a single video frame.

        If the game projection area has not yet been identified, the method
        attempts to detect it. Once detected, frames are cropped to the
        projection bounds, normalized to 256x224 grayscale, and scanned
        for sprite matches.

        Args:
            image (np.ndarray): Full RGB/BGR frame from the video.
            frame_number (int): Index of the current frame.
        """
        if not self.is_ready:
            self._find_game_area_projection(image, frame_number)
            return

        cropped = image[self.top:self.bottom, self.left:self.right]
        normalized = self._normalize(cropped)
        self._detect(normalized, frame_number)

    def _find_game_area_projection(self, image: np.ndarray, frame_number: int):
        """
        Attempts to detect the game projection area inside the frame.

        The method computes row and column mean intensities in grayscale
        space to identify non-black regions. If a valid area is found,
        it is resized to the canonical resolution and matched against
        the stored title screen template. When a sufficiently strong
        match is detected, projection bounds are stored for subsequent
        frame processing.

        Args:
            image (np.ndarray): Full RGB/BGR frame.
            frame_number (int): Index of the current frame.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        col_mean = gray.mean(axis=0)
        row_mean = gray.mean(axis=1)

        cols = np.flatnonzero(col_mean > self.PROJECTION_THRESHOLD)
        rows = np.flatnonzero(row_mean > self.PROJECTION_THRESHOLD)

        if cols.size == 0 or rows.size == 0:
            return
        #else:
            #print(
            #    f"Found non-black area at frame {frame_number} "
            #    f"with bounds x: [{cols[0]}, {cols[-1]}], "
            #    f"y: [{rows[0]}, {rows[-1]}]"
            #)

        cropped = gray[rows[0]:rows[-1], cols[0]:cols[-1]]
        resized = cv2.resize(
            cropped,
            (self.NORMALIZED_WIDTH, self.NORMALIZED_HEIGHT)
        )

        result = cv2.matchTemplate(
            resized,
            self.title_screen,
            cv2.TM_CCOEFF_NORMED
        )

        max_value = result.max()
        if max_value < self.MATCH_THRESHOLD:
            return

        print(
            f"Found title screen at frame {frame_number} "
            f"with accuracy = {max_value:.4f}"
        )

        self.left, self.top = cols[0], rows[0]
        self.right, self.bottom = cols[-1], rows[-1]
        self.is_ready = True

    def _normalize(self, image: np.ndarray) -> np.ndarray:
        """
        Converts an image to grayscale and rescales it to the original
        Super Mario Bros resolution (256x224).

        Args:
            image (np.ndarray): Cropped RGB/BGR game area.

        Returns:
            np.ndarray: Grayscale image resized to 256x224.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.resize(
            gray,
            (self.NORMALIZED_WIDTH, self.NORMALIZED_HEIGHT)
        )

    def _detect(self, image, frame_number: int):
        """
        Detects sprites in a normalized grayscale frame using
        template matching.

        All matches above MATCH_THRESHOLD are reported with their
        coordinates and correlation score.

        Args:
            image (np.ndarray): Grayscale image (256x224).
            frame_number (int): Index of the current frame.
        """
        
        result = cv2.matchTemplate(
            image,
            self.mario_dead_template,
            cv2.TM_CCOEFF_NORMED
        )

        locations = np.where(result >= 0.8)
        count = locations[0].size

        if count == 0:
            return

        if self.last_death_frame != -1 and frame_number - self.last_death_frame < 300:
            return
        
        self.last_death_frame = frame_number
        self.death_count += 1

        print(f"Death detected at frame {frame_number}, death count: {self.death_count}")
        #for i, (y, x) in enumerate(zip(*locations)):
        #    print(
        #        f"  Sprite {i + 1}: Position ({x}, {y}), "
        #        f"Accuracy: {result[y, x]:.4f}"
        #    )