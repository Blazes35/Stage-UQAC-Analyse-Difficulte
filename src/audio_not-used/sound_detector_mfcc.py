import os
import cv2
import librosa
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal


def find_audio_patterns_mfcc(main_audio_path, template_path, threshold=0.45, min_dist_seconds=1.0):
    # 1. Load the audio files
    print("Loading audio files...")
    main_audio_dir = "ressources/audios"
    save_main_audio_path = os.path.join(main_audio_dir, main_audio_path)
    y_main, sr = librosa.load(save_main_audio_path, sr=22050)

    template_dir = "ressources/sounds"
    save_template_path = os.path.join(template_dir, template_path)
    y_template, _ = librosa.load(save_template_path, sr=22050)

    # 2. Extract MFCC Features (The "Acoustic Fingerprint")
    print("Generating MFCC fingerprints...")
    hop_length = 256
    n_mfcc = 20  # Standard number of coefficients for sound recognition

    mfcc_main = librosa.feature.mfcc(y=y_main, sr=sr, n_mfcc=n_mfcc, hop_length=hop_length).astype(np.float32)
    mfcc_template = librosa.feature.mfcc(y=y_template, sr=sr, n_mfcc=n_mfcc, hop_length=hop_length).astype(np.float32)

    # 3. The Volume-Invariance Trick
    # We drop the 0th coefficient (index 0) from both matrices because it represents overall energy/volume.
    # This ensures a loud explosion doesn't trigger a false positive over a quieter death sound.
    mfcc_main = mfcc_main[1:, :]
    mfcc_template = mfcc_template[1:, :]

    # 4. 2D Template Matching
    print("Performing fingerprint matching...")
    result = cv2.matchTemplate(mfcc_main, mfcc_template, cv2.TM_CCOEFF_NORMED)
    correlation = result[0]
    correlation[correlation < 0] = 0

    # 5. Find Peaks
    frames_per_second = sr / hop_length
    distance_frames = int(min_dist_seconds * frames_per_second)

    peaks, properties = signal.find_peaks(
        correlation,
        height=threshold,
        distance=distance_frames
    )

    # 6. Compile Results
    matches = []
    print(f"\nFound {len(peaks)} matches:")

    for i, peak_index in enumerate(peaks):
        match_time = peak_index / frames_per_second
        score = properties["peak_heights"][i]
        matches.append({"time": round(match_time, 2), "score": round(score, 3)})
        print(f" - Time: {match_time:.2f}s | Confidence: {score:.2f}")

    # 7. Plotting
    time_axis = np.arange(len(correlation)) / frames_per_second

    plt.figure(figsize=(14, 6))
    plt.plot(time_axis, correlation, label="MFCC Match Confidence", alpha=0.8)

    if len(peaks) > 0:
        plt.plot(time_axis[peaks], correlation[peaks], "x", color="red", label="Matches", markersize=10,
                 markeredgewidth=2)

    plt.axhline(y=threshold, color='green', linestyle='--', alpha=0.5, label='Threshold')
    plt.title(f"Audio Matches Found: {len(matches)} occurrences")
    plt.xlabel("Time (Seconds)")
    plt.ylabel("Match Coefficient (0 to 1)")
    plt.ylim(0, 1.05)
    plt.legend()
    plt.grid(True, alpha=0.3)

    output_dir = "ressources/sound_matches"
    os.makedirs(output_dir, exist_ok=True)
    main_audio_base_file = os.path.splitext(main_audio_path)[0]
    template_audio_base_file = os.path.splitext(template_path)[0]
    save_path = os.path.join(output_dir, main_audio_base_file + "-" + template_audio_base_file + ".png")
    plt.savefig(save_path, dpi=300)
    print(f"\nPlot saved to: {save_path}")

    plt.show()

    return matches

results = find_audio_patterns_mfcc(
    'LongVideo.wav',
    'mario_death.wav',
    threshold=0.70,
    min_dist_seconds=1.0
)
