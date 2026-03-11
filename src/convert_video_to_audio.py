import os
import subprocess


def convert_file(input_file, output_file="", audio_stream=0, can_overwrite=False):
    if output_file == "" or os.path.splitext(input_file)[1] == "":
        output_file = os.path.splitext(input_file)[0] + ".wav"

    overwrite='-y' if can_overwrite else '-n'

    input_dir = "ressources/videos"
    save_input_path = os.path.join(input_dir, input_file)
    output_dir = "ressources/audios"
    save_output_path = os.path.join(output_dir, output_file)

    command = [
        "ffmpeg",
        overwrite,
        "-i", save_input_path,
        "-map", f"a:{audio_stream}",
        "-ac", "2",
        save_output_path
    ]

    subprocess.run(command, check=True)
