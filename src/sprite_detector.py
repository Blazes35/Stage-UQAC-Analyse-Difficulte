import cv2
import numpy as np
import csv
import template_loader as tl
from dataclasses import dataclass

@dataclass
class Event:
    event: str
    frame: int
    time_stamp: str
    level: str
    video_id: int

class SpriteDetector:
    """
    Detects sprites in video frames using template matching.

    The detector first identifies the projected game area inside the full frame.
    Once the projection is found, subsequent frames are cropped, normalized to
    the original game resolution (256x234), and analyzed for sprite presence.
    """

    NORMALIZED_WIDTH = 256 # Largeur originale de la projection du jeu Super Mario Bros
    NORMALIZED_HEIGHT = 234 # Hauteur originale de la projection du jeu Super Mario Bros
    MENU_MATCH_THRESHOLD = 0.5 # Degré de similarité minimum pour détecter le menu principal
    PROJECTION_THRESHOLD = 50 # Seuil de luminosité pour détecter les bords de la projection du jeu

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
        self.video_id = video_id
        self.events = []

        self.title_screen = tl.load_title_screen_template()
        self.mario_dead_template = tl.load_dead_template()
        self.mario_templates = tl.load_mario_templates()
        self.level_templates = tl.load_levels_templates()
        self.other_templates = tl.load_other_templates()
        self.current_level = "Game Over"

    def analyze(self, image: np.ndarray, frame_number: int):
        """
        Analyzes a single video frame.

        If the game projection area has not yet been identified, the method
        attempts to detect it. Once detected, frames are cropped to the
        projection bounds, normalized to 256x234 grayscale, and scanned
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
        if normalized.mean() < 20:
            self._detect_level(normalized, frame_number)

        if self.current_level == "Game Over":
            return

        self._detect_death(normalized, frame_number)
        self._detect_other_sprites(normalized, frame_number)

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
        if max_value < self.MENU_MATCH_THRESHOLD:
            return

        print(
            f"Found title screen at timestamp {_frame_to_timestamp(frame_number)} "
            f"with accuracy = {max_value:.4f}"
        )

        self.left, self.top = cols[0], rows[0]
        self.right, self.bottom = cols[-1], rows[-1]
        self.is_ready = True

    def _normalize(self, image: np.ndarray) -> np.ndarray:
        """
        Converts an image to grayscale and rescales it to the original
        Super Mario Bros resolution (256x234).

        Args:
            image (np.ndarray): Cropped RGB/BGR game area.

        Returns:
            np.ndarray: Grayscale image resized to 256x234.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.resize(
            gray,
            (self.NORMALIZED_WIDTH, self.NORMALIZED_HEIGHT)
        )

    def _detect_death(self, image, frame_number: int):
        """
        Detects mario death within a frame by first looking for the dead sprite, then checking for a
        pitfall death by tracking the position of Mario's head.

        Args:
            image (np.ndarray): Grayscale image (256x234).
            frame_number (int): Index of the current frame.
        """
        if self.last_death_frame != -1 and frame_number - self.last_death_frame < 300:
            return
        
          
        result = cv2.matchTemplate(
            image,
            self.mario_dead_template,
            cv2.TM_CCOEFF_NORMED,
        )

        max_value = result.max()
        locations = np.where(result == max_value)
        count = locations[0].size

        if count > 0 and max_value > 0.8:
            print(f"Enemy death with score {max_value:.4f}")
            self._write_death(frame_number, "enemy")
            return
            

        best_score = 0
        y_value = 0
        x_value = 0
        for template in self.mario_templates:
            result = cv2.matchTemplate(
                image,
                template,
                cv2.TM_CCOEFF_NORMED,
            )
            if result.max() > best_score:
                best_score = result.max()
                y_value = np.where(result == best_score)[0][0]
                x_value = np.where(result == best_score)[1][0]
                if best_score > 0.95:
                    break

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

        with open("./data/deaths.csv", "a", newline='') as death_file:
            fieldnames = ["type", "frame", "level", "video_id"]
            writer = csv.DictWriter(death_file, fieldnames=fieldnames)
            writer.writerow({
                "type": death_type,
                "frame": frame_number,
                "level": self.current_level,
                "video_id": self.video_id
            })
        print(f"Death detected at time {_frame_to_timestamp(frame_number)}, type: {death_type}")
        
    def _detect_level(self, image, frame_number: int):
        """
        Detects the current level in a normalized grayscale frame using
        template matching.

        If a match above the threshold is found and the detected level differs
        from the current level, the new level is recorded in the levels CSV file.

        Args:
            image (np.ndarray): Grayscale image (256x234).
            frame_number (int): Index of the current frame.
        """
        for template in self.level_templates:
            result = cv2.matchTemplate(
                image,
                template.image,
                cv2.TM_CCOEFF_NORMED
            )

            max_value = np.max(result)
            if max_value < 0.9:
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
                print(f"Level changed to {self.current_level} at timestamp {_frame_to_timestamp(frame_number)}")
            break

    def _detect_other_sprites(self, image, frame_number: int):
        """
        Detects other sprites in a normalized grayscale frame using
        template matching.

        All matches above their respective thresholds are added to the events list, which is periodically
        flushed to the CSV file to minimize I/O overhead.

        Args:
            image (np.ndarray): Grayscale image (256x234).
            frame_number (int): Index of the current frame.
        """
        for compound_template in self.other_templates:
            if frame_number - compound_template.last_seen < compound_template.cooldown:
                continue

            for template in compound_template.templates:
                
                result = cv2.matchTemplate(
                    image,
                    template,
                    cv2.TM_CCOEFF_NORMED
                )

                max_value = np.max(result)
                if max_value < compound_template.threshold:
                    continue

                print(f"Detected {compound_template.action_name} with score {max_value:.4f}")
                self.events.append(Event(
                    event=compound_template.action_name,
                    frame=frame_number,
                    time_stamp=_frame_to_timestamp(frame_number),
                    level=self.current_level,
                    video_id=self.video_id
                ))
                compound_template.last_seen = frame_number
                break

    def _write_all_events(self):
        """
        Writes all detected events to the CSV file.

        Should be called periodically (e.g., every 1000 frames) to flush accumulated events
        """
        print(f"Writing {len(self.events)} events to CSV file...")
        with open("./data/events.csv", "a", newline='') as event_file:
            fieldnames = ["event", "frame", "level", "video_id"]
            writer = csv.DictWriter(event_file, fieldnames=fieldnames)
            for event in self.events:
                if event.level == "Game Over":
                    continue
                writer.writerow({
                    "event": event.event,
                    "frame": event.frame,
                    "level": event.level,
                    "video_id": event.video_id
                })
            self.events = []

def _frame_to_timestamp(frame_number: int, fps: float = 60) -> str:
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