import os


from scipy import signal
import subprocess
import librosa
import numpy as np
import matplotlib.pyplot as plt


def find_audio_patterns(main_audio_path, template_path, threshold_ratio=0.6, min_dist_seconds=1.0):
    # 1. Load the audio files
    print("Loading audio files...")
    y_main, sr = librosa.load(main_audio_path, sr=22050)
    y_template, _ = librosa.load(template_path, sr=22050)

    # 2. Normalize the signals (Volume matching)
    y_main = y_main / np.max(np.abs(y_main))
    y_template = y_template / np.max(np.abs(y_template))

    # 3. Compute Cross-Correlation
    print("Computing correlation...")
    correlation = signal.correlate(y_main, y_template, mode='valid', method='fft')

    # Normalize correlation to 0-1 range for consistent thresholding
    correlation = correlation / np.max(np.abs(correlation))

    # Convert minimum distance from seconds to samples
    distance_samples = int(min_dist_seconds * sr)

    # 4. Find ALL peaks that satisfy our criteria
    peaks, properties = signal.find_peaks(
        correlation,
        height=threshold_ratio,
        distance=distance_samples
    )

    # 5. Compile results and Print
    matches = []
    print(f"Found {len(peaks)} matches:")

    for i, peak_index in enumerate(peaks):
        match_time = peak_index / sr
        score = properties["peak_heights"][i]

        matches.append({
            "time": round(match_time, 2),
            "score": round(score, 3),
            "index": peak_index
        })
        print(f" - Time: {match_time:.2f}s | Confidence: {score:.2f}")

    # 6. Plotting (X-axis in Seconds & Save to File)
    # Create a time axis that matches the length of the correlation array
    time_axis = np.arange(len(correlation)) / sr

    plt.figure(figsize=(14, 6))

    # Plot the correlation curve against time (seconds)
    plt.plot(time_axis, correlation, label="Correlation Confidence", alpha=0.8)

    # Mark the found peaks on the plot
    # We use the peak indices to find the correct time and height
    plt.plot(time_axis[peaks], correlation[peaks], "x", color="red", label="Matches", markersize=10, markeredgewidth=2)

    plt.title(f"Audio Matches Found: {len(matches)} occurrences")
    plt.xlabel("Time (Seconds)")  # <--- Changed from Index to Seconds
    plt.ylabel("Normalized Correlation (0.0 - 1.0)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Construct the full path: e.g., "matches/audio_plot.png"
    output_dir="ressources/sound_matches"
    save_path = os.path.join(output_dir, "audio_matches.png")
    plt.savefig(save_path, dpi=300)
    print(f"\nPlot saved to: {save_path}")

    # If you are running this in a notebook/IDE that supports it, this will still show the plot
    plt.show()

    return matches


def convert_file(input_file, output_file="", audio_stream=0, can_overwrite=False):
    if output_file == "" or os.path.splitext(input_file)[1] == "":
        output_file = os.path.splitext(input_file)[0] + ".wav"

    overwrite='-y' if can_overwrite else '-n'

    command = [
        "ffmpeg",
        overwrite,
        "-i", input_file,
        "-map", f"a:{audio_stream}",
        "-ac", "2",
        output_file
    ]

    subprocess.run(command, check=True)

# convert_file("mario_gameplay.mp4")

results = find_audio_patterns(
    'ressources/audios/Super Mario Bros.wav',
    'ressources/sounds/mario_death.wav',
    threshold_ratio=0.6,
    min_dist_seconds=1
)
print(results)
