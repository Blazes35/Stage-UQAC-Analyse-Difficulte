import os
import csv 
from frame_extractor import extract_all_frames, delete_all_files_in_folder

def initiate_csv_files():
    """Initiate the csv files for deaths, levels, and events with the correct headers."""
    with open("./data/deaths.csv", "w", newline='') as death_file:
        fieldnames = ["number", "type", "frame", "level", "video_id"]
        writer = csv.DictWriter(death_file, fieldnames=fieldnames)
        writer.writeheader()
    with open("./data/levels.csv", "w", newline='') as level_file:
        fieldnames = ["frame", "level", "video_id"]
        writer = csv.DictWriter(level_file, fieldnames=fieldnames)
        writer.writeheader()
    with open("./data/events.csv", "w", newline='') as event_file:
        fieldnames = ["event", "frame", "time_stamp", "level", "video_id"]
        writer = csv.DictWriter(event_file, fieldnames=fieldnames)
        writer.writeheader()

if __name__ == "__main__":
    initiate_csv_files()
    # For every video in ressources/videos, extract all frames without saving them
    videos_folder = "./ressources/videos"
    video_id = 1
    for filename in os.listdir(videos_folder):
        video_path = os.path.join(videos_folder, filename)
        print("Processing video: " + video_path)
        if os.path.isfile(video_path) and video_path.endswith((".mp4")):  
            extract_all_frames(video_path, video_id=video_id, save_frames=False)
            video_id += 1