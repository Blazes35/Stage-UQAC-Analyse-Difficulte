import os

import librosa
import soundfile as sf


def optimize_template(input_filename, output_filename, top_db=30):
    """
    Loads an audio file, trims the silence from the start and end,
    and saves the optimized version.
    """
    input_path = os.path.join("ressources/sounds", input_filename)
    output_path = os.path.join("ressources/sounds", output_filename)

    print(f"Loading '{input_filename}' for trimming...")
    # Load the audio
    y, sr = librosa.load(input_path, sr=22050)

    # Trim the silence
    # top_db=30 means anything that is 30 decibels quieter than the loudest
    # part of the file is considered "silence" and gets chopped off the edges.
    y_trimmed, index = librosa.effects.trim(y, top_db=30)

    # Calculate durations for reporting
    duration_original = librosa.get_duration(y=y, sr=sr)
    duration_trimmed = librosa.get_duration(y=y_trimmed, sr=sr)
    time_saved = duration_original - duration_trimmed

    print(f" - Original duration: {duration_original:.3f} seconds")
    print(f" - Trimmed duration:  {duration_trimmed:.3f} seconds")
    print(f" - Removed {time_saved:.3f} seconds of dead air.")

    # Save the optimized file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sf.write(output_path, y_trimmed, sr)
    print(f"\nSuccess! Optimized template saved to: '{output_path}'")
