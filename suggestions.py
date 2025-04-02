import json
import joblib
import numpy as np
import os

FOCUS_GENRES = ['Pop', 'EDM', 'Rock', 'Dance', 'Hiphop', 'Ambient', 'Chillout', 'Orchestral', 'Speech', 'Piano']
# Get the absolute path to the directory containing this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(SCRIPT_DIR, 'model')
PROFILES_DIR = os.path.join(SCRIPT_DIR, "profiles")
CUSTOM_DIR = os.path.join(SCRIPT_DIR, "custom")

def load_genre_model():
    model_path = os.path.join(MODEL_DIR, 'genre_model.joblib')
    feature_scaler_path = os.path.join(MODEL_DIR, 'genre_feature_scaler.joblib')
    target_scaler_path = os.path.join(MODEL_DIR, 'genre_target_scaler.joblib')
    
    print(f"Attempting to load model from: {model_path}")
    print(f"Attempting to load feature scaler from: {feature_scaler_path}")
    print(f"Attempting to load target scaler from: {target_scaler_path}")
    
    if not os.path.exists(model_path) or not os.path.exists(feature_scaler_path) or not os.path.exists(target_scaler_path):
        raise FileNotFoundError("Model or scalers not found")
    
    try:
        genre_model = joblib.load(model_path)
        feature_scaler = joblib.load(feature_scaler_path)
        target_scaler = joblib.load(target_scaler_path)
    except Exception as e:
        print(f"Error loading model or scalers: {e}")
        raise
    
    return genre_model, feature_scaler, target_scaler

def prepare_input_features(profile):
    numerical_features = [
        profile['initial_rms'],
        profile['rms_mid'],
        profile['rms_side'],
        profile['rms_after_matching'],
        profile['stereo_width_mid'],
        profile['stereo_width_side'],
        profile['lufs'],
        profile['spectral_centroid'],
        profile['spectral_bandwidth']
    ]
    print(f"Numerical features: {len(numerical_features)}")
    
    # Normalize numerical features
    max_val = max(numerical_features)
    min_val = min(numerical_features)
    normalized_features = [(x - min_val) / (max_val - min_val) for x in numerical_features]
    
    genre_encoding = [1 if profile['genre'] == g else 0 for g in FOCUS_GENRES]
    print(f"Genre encoding: {len(genre_encoding)}")
    
    spectrum_mid = profile['simplified_spectrum_mid']
    spectrum_side = profile['simplified_spectrum_side']
    print(f"Spectrum mid: {len(spectrum_mid)}")
    print(f"Spectrum side: {len(spectrum_side)}")
    
    features = normalized_features + genre_encoding + spectrum_mid + spectrum_side
    print(f"Total features: {len(features)}")
    
    return np.array(features).reshape(1, -1)

def get_suggestions_for_genre(genre):
    # Load the genre model and scalers
    genre_model, feature_scaler, target_scaler = load_genre_model()

    # Load the profile for the given genre
    profile_path = os.path.join(PROFILES_DIR, f"{genre}.json")
    if not os.path.exists(profile_path):
        profile_path = os.path.join(CUSTOM_DIR, genre, f"{genre}.json")
    assert os.path.exists(profile_path), f"Genre profile '{genre}.json' not found"

    with open(profile_path, 'r') as f:
        profile = json.load(f)
    
    # Prepare input features
    input_features = prepare_input_features(profile)
    
    # Scale the input features
    scaled_features = feature_scaler.transform(input_features)
    
    # Get suggestions from the model
    scaled_suggestions = genre_model.predict(scaled_features)
    
    # Inverse transform the suggestions
    suggestions = target_scaler.inverse_transform(scaled_suggestions.reshape(1, -1))[0]
    
    return {
        'rms_mid': suggestions[0],
        'rms_side': suggestions[1],
        'stereo_width': suggestions[2]
    }
