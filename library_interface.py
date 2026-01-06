
import json
import os
from pathlib import Path
from pitch_extractor import PitchExtractor
from pitch_matcher import PitchMatcher

def score_karaoke_and_get_json(user_audio_path: str, 
                               reference_path: str, 
                               method: str = 'crepe', 
                               tolerance_cents: float = 200.0,
                               difficulty_mode: str = 'easy') -> str:
    """
    Encapsulates the entire karaoke scoring pipeline and returns the results as a JSON string.
    This function is intended to be called from a C-compatible interface (e.g., C++ embedding Python).
    
    Args:
        user_audio_path (str): Path to the user's audio file (WAV, MP3, FLAC, etc.)
        reference_path (str): Path to the reference audio file (WAV, MP3, FLAC, or MIDI).
        method (str): Pitch extraction method ('crepe' or 'basic_pitch'). Default: 'crepe'
        tolerance_cents (float): Tolerance in cents for pitch matching. Default: 200.0 (easy mode)
        difficulty_mode (str): Difficulty mode ('easy', 'normal', 'hard'). Default: 'easy'
    
    Returns:
        str: JSON string containing the scoring results or error message.
             Success format: {"final_score": ..., "accuracy": ..., ...}
             Error format: {"error": "...", "final_score": 0, "accuracy": 0, "dtw_score": 0}
    """
    results = {}
    try:
        # 1. Validate file paths
        if not os.path.exists(user_audio_path):
            raise FileNotFoundError(f"User audio file not found: {user_audio_path}")
        if not os.path.exists(reference_path):
            raise FileNotFoundError(f"Reference file not found: {reference_path}")
        
        # 2. Initialize PitchExtractor
        extractor = PitchExtractor(method=method, model_capacity='tiny')
        
        # 3. Extract pitch from user's audio
        time_user, freq_user = extractor.extract_pitch(user_audio_path)
        if len(time_user) == 0 or len(freq_user) == 0:
            raise ValueError(f"No pitch detected in user audio: {user_audio_path}")
        
        # 4. Extract pitch from reference (audio or MIDI)
        ref_ext = Path(reference_path).suffix.lower()
        if ref_ext in ['.mid', '.midi']:
            # MIDI reference
            time_ref, freq_ref = extractor.extract_pitch_from_midi(reference_path, track_filter='auto')
        else:
            # Audio reference
            time_ref, freq_ref = extractor.extract_pitch(reference_path)
        
        if len(time_ref) == 0 or len(freq_ref) == 0:
            raise ValueError(f"No pitch detected in reference: {reference_path}")
        
        # 5. Match pitches and calculate score
        matcher = PitchMatcher(tolerance_cents=tolerance_cents, difficulty_mode=difficulty_mode)
        results = matcher.calculate_score(time_user, freq_user, time_ref, freq_ref)
        
        # 6. Ensure no error field in success case
        if 'error' in results:
            del results['error']

    except Exception as e:
        # Return consistent error format
        results = {
            'error': str(e),
            'final_score': 0.0,
            'accuracy': 0.0,
            'dtw_score': 0.0,
            'dtw_distance': 0.0,
            'mae_cents': 0.0,
            'duration': 0.0
        }

    return json.dumps(results, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    # Example usage for testing the function directly
    # Create dummy audio files for testing if they don't exist
    # In a real scenario, you would use actual audio files.
    
    # NOTE: This part is for demonstration and requires dummy files.
    # You should replace 'path/to/user_audio.wav' and 'path/to/reference.mid'
    # with actual file paths to test properly.
    
    user_file = 'example_user.wav'
    ref_file_midi = 'example_ref.mid'
    
    # This is a placeholder for a real test.
    # To run this, you need valid audio and midi files.
    # For now, we will just call the function with non-existent files
    # to demonstrate the error handling.
    
    print("--- Testing with non-existent files (expecting error) ---")
    json_output_error = score_karaoke_and_get_json('non_existent_user.wav', 'non_existent_ref.mid')
    print(json_output_error)
    
    # To test successfully, you would need to:
    # 1. Have valid .wav and .mid files in your project directory.
    # 2. Uncomment the lines below and replace the file names.
    
    # print("\n--- Testing with actual files (replace with your files) ---")
    # json_output_success = score_karaoke_and_get_json('path/to/your/user.wav', 'path/to/your/reference.mid')
    # print(json_output_success)

# --- Python Module Interface ---
# This module can be imported and used from C++ via Python C API
# The C++ code will embed Python interpreter and call these functions directly

# Export the main function for C++ to use
__all__ = ['score_karaoke_and_get_json']

