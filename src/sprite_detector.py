import cv2
import numpy as np
import csv
from typing import cast
import template_loader as tl

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

    def __init__(self, video_id: int):
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
        self.video_id = video_id

        self.title_screen = tl.load_title_screen_template()
        self.mario_dead_template = tl.load_dead_template()
        self.mario_templates = tl.load_mario_templates()
        self.level_templates = tl.load_levels_templates()
        self.current_level = "1-1"

        with open("./data/deaths.csv", "w", newline='') as death_file:
            fieldnames = ["number", "type", "frame", "level", "video_id"]
            writer = csv.DictWriter(death_file, fieldnames=fieldnames)
            writer.writeheader()
        with open("./data/levels.csv", "w", newline='') as level_file:
            fieldnames = ["frame", "level", "video_id"]
            writer = csv.DictWriter(level_file, fieldnames=fieldnames)
            writer.writeheader()

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
        if normalized.mean() < 20:
            self._detect_level(normalized, frame_number)

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
            f"Found title screen at timestamp {frame_to_timestamp(frame_number)} "
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
        if self.last_death_frame != -1 and frame_number - self.last_death_frame < 300:
            return
        
        result = cv2.matchTemplate(
            image,
            self.mario_dead_template,
            cv2.TM_CCOEFF_NORMED
        )

        max_value = result.max()
        locations = np.where(result == max_value)
        count = locations[0].size

        if count > 0 and max_value > 0.75:
            self._write_death(frame_number, "enemy")
            return
            

        best_score = 0
        y_value = 0
        x_value = 0
        for template in self.mario_templates:
            result = cv2.matchTemplate(
                image,
                template,
                cv2.TM_CCOEFF_NORMED
            )
            if result.max() > best_score:
                best_score = result.max()
                y_value = np.where(result == best_score)[0][0]
                x_value = np.where(result == best_score)[1][0]


        #if frame_number % 100 == 0:
        #    print(f"Best match score for Mario templates at frame {frame_number}: {best_score:.4f}, y: {y_value}")
        if best_score > 0.8 and y_value > 205 and x_value < 150:
            print(f"pitfall death with score {best_score:.4f}")
            self._write_death(frame_number, "pitfall")

    def _write_death(self, frame_number: int, death_type: str):
        """
        Writes a death event to the CSV file.

        Args:
            frame_number (int): Index of the frame where the death was detected.
            death_type (str): Type of death (e.g., "enemy", "fall", etc.).
        """
        self.last_death_frame = frame_number
        self.death_count += 1

        with open("./data/deaths.csv", "a", newline='') as death_file:
            fieldnames = ["number", "type", "frame", "level", "video_id"]
            writer = csv.DictWriter(death_file, fieldnames=fieldnames)
            writer.writerow({
                "number": self.death_count,
                "type": death_type,
                "frame": frame_number,
                "level": self.current_level,
                "video_id": self.video_id
            })
        print(f"Death detected at time {frame_to_timestamp(frame_number)}, type: {death_type}, total deaths: {self.death_count}")
        
    def _detect_level(self, image, frame_number: int):
        """
        Detects the current level in a normalized grayscale frame using
        template matching.

        All matches above MATCH_THRESHOLD are reported with their
        coordinates and correlation score.

        Args:
            image (np.ndarray): Grayscale image (256x224).
            frame_number (int): Index of the current frame.
        """
        for template in self.level_templates:
            result = cv2.matchTemplate(
                image,
                template.image,
                cv2.TM_CCOEFF_NORMED
            )

            max_value = np.max(result)
            if max_value < 0.95:
                continue

            if not self.current_level == template.name:
                self.current_level = template.name
                with open("./data/levels.csv", "a", newline='') as level_file:
                    fieldnames = ["frame", "level", "video_id"]
                    writer = csv.DictWriter(level_file, fieldnames=fieldnames)
                    writer.writerow({
                        "frame": frame_number,
                        "level": self.current_level,
                        "video_id": self.video_id
                    })
                print(f"Level changed to {self.current_level} at timestamp {frame_to_timestamp(frame_number)}")
            break

def frame_to_timestamp(frame_number: int, fps: float = 60) -> str:
    """
    Converts a frame number to a timestamp string in the format "MM:SS".

    Args:
        frame_number (int): The index of the frame.
        fps (float): Frames per second of the video.

    Returns:
        str: Timestamp in "MM:SS" format.
    """
    total_seconds = frame_number / fps
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"