import os
import cv2
import librosa
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal


def find_audio_patterns_hpss_cqt(main_audio_path, template_path, threshold=0.55, min_dist_seconds=3.0):
    print("Loading audio files...")
    y_main, sr = librosa.load(os.path.join("ressources/audios", main_audio_path), sr=22050)
    y_template, _ = librosa.load(os.path.join("ressources/sounds", template_path), sr=22050)

    # Pre-normalize
    y_main = y_main / np.max(np.abs(y_main))
    y_template = y_template / np.max(np.abs(y_template))

    # 1. Harmonic-Percussive Source Separation (The Magic Bullet)
    print("Separating harmonic tones from percussive noise (filtering out fireballs)...")
    # margin > 1.0 forces the algorithm to be stricter about what it considers a "tone"
    y_main_harmonic, _ = librosa.effects.hpss(y_main, margin=1.2)
    y_template_harmonic, _ = librosa.effects.hpss(y_template, margin=1.2)

    # 2. Constant-Q Transform (Pitch/Melody Tracking)
    print("Generating CQT Musical Spectrograms...")
    hop_length = 256

    # Generate the CQT (84 bins = 7 octaves of musical notes)
    C_main = librosa.cqt(y=y_main_harmonic, sr=sr, hop_length=hop_length, n_bins=84)
    C_template = librosa.cqt(y=y_template_harmonic, sr=sr, hop_length=hop_length, n_bins=84)

    # Convert to Decibels with a fixed reference
    C_main_db = librosa.amplitude_to_db(np.abs(C_main), ref=1.0).astype(np.float32)
    C_template_db = librosa.amplitude_to_db(np.abs(C_template), ref=1.0).astype(np.float32)

    # 3. 2D Template Matching
    print("Performing precise melody matching...")
    result = cv2.matchTemplate(C_main_db, C_template_db, cv2.TM_CCOEFF_NORMED)
    correlation = result[0]
    correlation[correlation < 0] = 0

    # 4. Find Peaks (with increased distance to prevent double-counting)
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
        match_time = peak_index / frames_per_second
        score = properties["peak_heights"][i]
        matches.append({"time": round(match_time, 2), "score": round(score, 3)})
        print(f" - Time: {match_time:.2f}s | Confidence: {score:.2f}")

    # 6. Plotting
    time_axis = np.arange(len(correlation)) / frames_per_second

    plt.figure(figsize=(14, 6))
    plt.plot(time_axis, correlation, label="Melody Match Confidence", alpha=0.8)

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

results = find_audio_patterns_hpss_cqt(
    'LongVideo.wav',
    'mario_death.wav',
    threshold=0.40,
    min_dist_seconds=1.0
)
