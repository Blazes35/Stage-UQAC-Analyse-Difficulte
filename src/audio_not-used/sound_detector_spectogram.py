import os
import cv2
import librosa
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

from trim_template import optimize_template


def find_audio_patterns_spectrogram(main_audio_path, template_path, threshold=0.55, min_dist_seconds=1.0):
    # 1. Load the audio files
    print("Loading audio files...")
    main_audio_dir = "ressources/audios"
    save_main_audio_path = os.path.join(main_audio_dir, main_audio_path)
    y_main, sr = librosa.load(save_main_audio_path, sr=22050)

    main_audio_dir = "ressources/sounds"
    save_template_path = os.path.join(main_audio_dir, template_path)
    y_template, _ = librosa.load(save_template_path, sr=22050)

    # 2. Convert to Spectrograms (Frequency Domain)
    print("Generating spectrograms...")
    # hop_length controls time resolution. 512 is standard (approx 23ms per frame at 22050Hz)
    hop_length = 512

    # Compute STFT, get magnitude, and convert to decibels (log scale) to highlight patterns
    S_main = librosa.amplitude_to_db(np.abs(librosa.stft(y_main, hop_length=hop_length)), ref=np.max)
    S_template = librosa.amplitude_to_db(np.abs(librosa.stft(y_template, hop_length=hop_length)), ref=np.max)

    # OpenCV matchTemplate requires float32 data types
    S_main = S_main.astype(np.float32)
    S_template = S_template.astype(np.float32)

    # 3. 2D Template Matching using OpenCV
    print("Performing spectrogram template matching...")
    # TM_CCOEFF_NORMED automatically handles normalization, returning scores between -1.0 and +1.0
    # It slides the template matrix across the main audio matrix.
    result = cv2.matchTemplate(S_main, S_template, cv2.TM_CCOEFF_NORMED)

    # Since the frequency bins (Y-axis) are identical, it only slides on the time axis (X-axis).
    # Result is essentially a 1D array, so we extract it.
    correlation = result[0]

    # Zero out negative correlations to clean up the data
    correlation[correlation < 0] = 0

    # 4. Find Peaks
    # We must convert min_dist_seconds to spectrogram "frames" instead of raw audio samples
    frames_per_second = sr / hop_length
    distance_frames = int(min_dist_seconds * frames_per_second)

    peaks, properties = signal.find_peaks(
        correlation,
        height=threshold,
        distance=distance_frames
    )

    # 5. Compile Results
    matches = []
    print(f"\nFound {len(peaks)} matches:")

    for i, peak_index in enumerate(peaks):
        # Convert frame index back to seconds
        match_time = peak_index / frames_per_second
        score = properties["peak_heights"][i]

        matches.append({
            "time": round(match_time, 2),
            "score": round(score, 3)
        })
        print(f" - Time: {match_time:.2f}s | Confidence: {score:.2f}")

    # 6. Plotting
    # Create an X-axis based on spectrogram frames converted to seconds
    time_axis = np.arange(len(correlation)) / frames_per_second

    plt.figure(figsize=(14, 6))
    plt.plot(time_axis, correlation, label="Template Match Confidence", alpha=0.8)

    if len(peaks) > 0:
        plt.plot(time_axis[peaks], correlation[peaks], "x", color="red", label="Matches", markersize=10,
                 markeredgewidth=2)

    # Add a visual threshold line
    plt.axhline(y=threshold, color='green', linestyle='--', alpha=0.5, label='Threshold')

    plt.title(f"Spectrogram Matches Found: {len(matches)} occurrences")
    plt.xlabel("Time (Seconds)")
    plt.ylabel("Match Coefficient (0 to 1)")
    plt.ylim(0, 1.05)
    plt.legend()
    plt.grid(True, alpha=0.3)

    output_dir = "ressources/sound_matches"
    os.makedirs(output_dir, exist_ok=True)
    main_audio_base_file = os.path.splitext(main_audio_path)[0]
    template_audio_base_file = os.path.splitext(template_path)[0]
    save_path = os.path.join(output_dir, main_audio_base_file+"-"+template_audio_base_file+".png")
    plt.savefig(save_path, dpi=300)
    print(f"\nPlot saved to: {save_path}")

    plt.show()

    return matches


# Note: The threshold usually needs to be tweaked for spectrograms.
# 0.5 to 0.65 is usually a very strong match for TM_CCOEFF_NORMED.
results = find_audio_patterns_spectrogram(
    'Super Mario Bros.wav',
    'mario_death.wav',
    threshold=0.55,
    min_dist_seconds=1.0
)

# Run it on your Mario death sound
optimize_template("mario_death.wav", "mario_death_trimmed.wav", top_db=30)