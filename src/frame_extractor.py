import cv2
import os, shutil
from sprite_detector import SpriteDetector

def extract_all_frames(video_path : str, folder_for_frames : str = "./ressources/frames", save_frames : bool = False):
    """
    Extract all frames with the names "frame[n].jpg" with n the number of the frame in the folder specified

    :param video_path: path of the video to extract all the frames
    :type video_path: str
    :param folder_for_frames: Path of the folder which will contain all the frames
    :type folder_for_frames: str
    :param save_frames: If True, save the frames in the folder specified
    :type save_frames: bool
    """

    if not os.path.isfile(video_path) :
        print("The file" + video_path + " was not found")
        return
    print("Extracting '" + video_path +"' frames...")

    detector = SpriteDetector(1)

    if save_frames and not os.path.exists(folder_for_frames):
        os.makedirs(folder_for_frames)
        print("Created folder '" + folder_for_frames + "'.")

    capture = cv2.VideoCapture(video_path)
    i = 0

    while(capture.isOpened):
        i += 1
        if i % 600 == 0:
            print("Analyzed " + str(i) + " frames...")
            detector.write_all_events()

        #capture.read()
        has_more_frames, frame = capture.read()
        if has_more_frames == False:
            break

        detector.analyze(frame, i)
        
        if save_frames:
            frame_name = folder_for_frames + "/frame"+str(i)+".jpg"
            cv2.imwrite(frame_name, frame)
    print ("Total of frames extracted : " + str(i-1))

def delete_all_files_in_folder(folder : str):
    """
    Deletes all files in the folder specified
    (can be used to clear frames in a folder)

    :param folder: name of the folder from which to remove files
    :type folder: str
    """
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
