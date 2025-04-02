import os
import numpy as np
import librosa
import json
import traceback
import argparse
from mastering import Config, process_audio, lr_to_ms, rms, calculate_improved_rms, calculate_lufs

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CUSTOM_DIR = os.path.join(SCRIPT_DIR, "custom")
FFMPEG = "ffmpeg"  # Path to ffmpeg executable

def extract_features(audio_path, config, duration=None):
    print(f"Extracting features from: {audio_path}")
    y, sr = librosa.load(audio_path, sr=config.sample_rate, duration=duration, mono=False)  # Load full audio
    
    print("Processing audio...")
    try:
        processed_audio = process_audio(y, y, 4, config)
    except Exception as e:
        print(f"Error in process_audio: {str(e)}")
        print(traceback.format_exc())
        return None
    
    # Oversample the processed audio
    oversampled_audio = librosa.resample(y=processed_audio, orig_sr=sr, target_sr=sr * config.oversampling_factor)
    oversampled_sr = sr * config.oversampling_factor
    
    print("Converting to mid-side...")
    mid, side = lr_to_ms(oversampled_audio)
    
    print("Calculating initial RMS...")
    initial_rms = rms(oversampled_audio)
    
    print("Calculating RMS values...")
    rms_mid = rms(mid)
    rms_side = rms(side)
    
    print("Calculating RMS after matching...")
    rms_after_matching = calculate_improved_rms(oversampled_audio, oversampled_sr, config)
    
    print("Calculating stereo width...")
    stereo_width_mid, stereo_width_side = analyze_stereo_width(mid, side)
    
    print("Calculating frequency spectrum...")
    n_fft = config.fft_size
    mid_spectrum = np.abs(librosa.stft(mid, n_fft=n_fft))
    side_spectrum = np.abs(librosa.stft(side, n_fft=n_fft))
    
    # Simplify spectrum
    simplified_spectrum_mid = simplify_spectrum(mid_spectrum)
    simplified_spectrum_side = simplify_spectrum(side_spectrum)
    
    print("Calculating level correction...")
    level_correction_mid, level_correction_side = calculate_level_correction(mid, side)
    
    print("Calculating LUFS...")
    lufs = calculate_lufs(oversampled_audio, oversampled_sr)
    
    # Calculate additional spectral features
    spectral_centroid = librosa.feature.spectral_centroid(y=oversampled_audio).mean()
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=oversampled_audio).mean()
    
    print("Feature extraction complete.")
    return {
        "initial_rms": initial_rms,
        "rms_mid": rms_mid,
        "rms_side": rms_side,
        "rms_after_matching": rms_after_matching,
        "stereo_width_mid": stereo_width_mid,
        "stereo_width_side": stereo_width_side,
        "simplified_spectrum_mid": simplified_spectrum_mid.tolist(),
        "simplified_spectrum_side": simplified_spectrum_side.tolist(),
        "level_correction_mid": level_correction_mid,
        "level_correction_side": level_correction_side,
        "lufs": lufs,
        "spectral_centroid": spectral_centroid,
        "spectral_bandwidth": spectral_bandwidth,
        "waveform": y,
        "sample_rate": sr
    }

def analyze_stereo_width(mid, side):
    mid_rms = np.sqrt(np.mean(np.square(mid)))
    side_rms = np.sqrt(np.mean(np.square(side)))
    total_rms = mid_rms + side_rms
    return mid_rms / total_rms, side_rms / total_rms

def calculate_level_correction(mid, side):
    # Calculate a simplified level correction factor
    mid_correction = np.mean(np.abs(mid))
    side_correction = np.mean(np.abs(side))
    return mid_correction, side_correction

def simplify_spectrum(spectrum, n_bands=10):
    return librosa.feature.melspectrogram(S=spectrum, n_mels=n_bands).mean(axis=1)

def create_genre_profile(audio_path, genre, config):
    features = extract_features(audio_path, config)
    
    if features is None:
        print(f"Failed to extract features for {genre}")
        return

    profile = {
        "version": "1.0",
        "genre": genre,
        "initial_rms": float(features["initial_rms"]),
        "rms_mid": float(features["rms_mid"]),
        "rms_side": float(features["rms_side"]),
        "rms_after_matching": float(features["rms_after_matching"]),
        "stereo_width_mid": float(features["stereo_width_mid"]),
        "stereo_width_side": float(features["stereo_width_side"]),
        "simplified_spectrum_mid": features["simplified_spectrum_mid"],
        "simplified_spectrum_side": features["simplified_spectrum_side"],
        "level_correction_mid": float(features["level_correction_mid"]),
        "level_correction_side": float(features["level_correction_side"]),
        "lufs": float(features["lufs"]),
        "spectral_centroid": float(features["spectral_centroid"]),
        "spectral_bandwidth": float(features["spectral_bandwidth"])
    }

    os.makedirs(os.path.join(CUSTOM_DIR, genre), exist_ok=True)
    output_file = os.path.join(CUSTOM_DIR, genre, f"{genre}.json")

    with open(output_file, 'w') as f:
        json.dump(profile, f, indent=2)

    # Save the waveform as a WAV file
    waveform_file = os.path.join(CUSTOM_DIR, genre, f"{genre}.mp3")
    command = f"{FFMPEG} -i \"{audio_path}\" -loglevel error -ac 2 -b:a 320k -y \"{waveform_file}\""
    try:
        import subprocess
        ffmpeg_version_output = subprocess.check_output(["ffmpeg", "-version"], text=True)
        first_line = ffmpeg_version_output.splitlines()[0]
        print(f"FFmpeg installed: {first_line}")
        subprocess.run(command, shell=True, check=True)
    except FileNotFoundError:
        import soundfile as sf
        print("FFmpeg is not installed. Use soundfile to save the waveform.")
        sf.write(waveform_file, features["waveform"].T, features["sample_rate"], format='mp3')

    print(f"Created profile for {genre}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate custom profiles for audio mastering")
    parser.add_argument("audio_file", help="Path to the audio file to extract features from")
    parser.add_argument("-n", "--name", default="CustomProfile", help="Name of the genre profile to create")
    args = parser.parse_args()
    config = Config()

    create_genre_profile(args.audio_file, args.name, config)