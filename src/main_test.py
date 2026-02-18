from sprite_detector import sprite_detector
from frame_extractor import extract_all_frames, delete_all_files_in_folder

if __name__ == "__main__":
    extract_all_frames("./ressources/Longplay NES - Super Mario Bros 100 4K 60FPS.mkv", save_frames=False)