"""
Trích xuất Pitch Contour từ audio sử dụng CREPE hoặc Basic Pitch
"""
import numpy as np
import librosa
from typing import Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class PitchExtractor:
    """Lớp trích xuất pitch từ audio"""
    
    def __init__(self, method: str = 'crepe', model_capacity: str = 'full'):
        """
        Args:
            method: 'crepe' hoặc 'basic_pitch'
            model_capacity: Chỉ dùng cho CREPE - 'tiny', 'small', 'medium', 'large', 'full'
        """
        self.method = method
        self.model_capacity = model_capacity
        self._crepe_model = None
        self._basic_pitch_model = None
        
    def _load_crepe(self):
        """Load CREPE model"""
        try:
            import crepe
            self._crepe_model = crepe
            return True
        except ImportError:
            print("⚠️ CREPE chưa được cài đặt. Chạy: pip install crepe")
            return False
    
    def _load_basic_pitch(self):
        """Load Basic Pitch model"""
        try:
            from basic_pitch import ICASSP_2022_MODEL_PATH
            from basic_pitch.inference import predict
            import tensorflow as tf
            self._basic_pitch_model = {
                'predict': predict,
                'model_path': ICASSP_2022_MODEL_PATH
            }
            return True
        except ImportError:
            print("⚠️ Basic Pitch chưa được cài đặt. Chạy: pip install basic-pitch")
            return False
    
    def extract_pitch_crepe(self, audio_path: str, step_size: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """
        Trích xuất pitch sử dụng CREPE
        
        Args:
            audio_path: Đường dẫn file audio
            step_size: Độ phân giải tính bằng milliseconds (10ms = 100Hz)
        
        Returns:
            (time, frequency): Mảng thời gian và mảng tần số (Hz)
        """
        if self._crepe_model is None:
            if not self._load_crepe():
                raise ImportError("Không thể load CREPE model")
        
        # Load audio
        audio, sr = librosa.load(audio_path, sr=16000)
        
        # CREPE yêu cầu sample rate 16kHz
        time, frequency, confidence, activation = self._crepe_model.predict(
            audio, 
            sr, 
            viterbi=True,
            model_capacity=self.model_capacity,
            step_size=step_size
        )
        
        # Lọc các pitch không đáng tin cậy (confidence < 0.5)
        mask = confidence > 0.5
        time_filtered = time[mask]
        frequency_filtered = frequency[mask]
        
        # Loại bỏ các giá trị 0 (không phát hiện được pitch)
        mask_nonzero = frequency_filtered > 0
        time_filtered = time_filtered[mask_nonzero]
        frequency_filtered = frequency_filtered[mask_nonzero]
        
        return time_filtered, frequency_filtered
    
    def extract_pitch_basic_pitch(self, audio_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Trích xuất pitch sử dụng Basic Pitch
        
        Args:
            audio_path: Đường dẫn file audio
        
        Returns:
            (time, frequency): Mảng thời gian và mảng tần số (Hz)
        """
        if self._basic_pitch_model is None:
            if not self._load_basic_pitch():
                raise ImportError("Không thể load Basic Pitch model")
        
        # Basic Pitch trả về MIDI notes, cần convert sang Hz
        model_output, midi_data, note_events = self._basic_pitch_model['predict'](
            audio_path,
            self._basic_pitch_model['model_path']
        )
        
        # Chuyển đổi MIDI notes sang frequency (Hz)
        # MIDI note 69 = A4 = 440 Hz
        times = []
        frequencies = []
        
        for note in note_events:
            # Lấy thời gian bắt đầu và kết thúc
            start_time = note['start_time']
            end_time = note['end_time']
            midi_note = note['pitch']
            
            # Convert MIDI to Hz: f = 440 * 2^((midi - 69) / 12)
            freq = 440 * (2 ** ((midi_note - 69) / 12))
            
            # Tạo các điểm thời gian với resolution 10ms
            duration = end_time - start_time
            num_points = int(duration * 100)  # 100 points per second (10ms resolution)
            if num_points > 0:
                time_points = np.linspace(start_time, end_time, num_points)
                freq_points = np.full(num_points, freq)
                times.extend(time_points)
                frequencies.extend(freq_points)
        
        if len(times) == 0:
            return np.array([]), np.array([])
        
        return np.array(times), np.array(frequencies)
    
    def extract_pitch(self, audio_path: str, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """
        Trích xuất pitch từ audio
        
        Args:
            audio_path: Đường dẫn file audio
            **kwargs: Các tham số bổ sung cho từng method
        
        Returns:
            (time, frequency): Mảng thời gian và mảng tần số (Hz)
        """
        if self.method == 'crepe':
            step_size = kwargs.get('step_size', 10)
            return self.extract_pitch_crepe(audio_path, step_size)
        elif self.method == 'basic_pitch':
            return self.extract_pitch_basic_pitch(audio_path)
        else:
            raise ValueError(f"Method không hợp lệ: {self.method}. Chọn 'crepe' hoặc 'basic_pitch'")
    
    def extract_pitch_from_midi(self, midi_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Trích xuất pitch từ file MIDI (cho reference)
        
        Args:
            midi_path: Đường dẫn file MIDI
        
        Returns:
            (time, frequency): Mảng thời gian và mảng tần số (Hz)
        """
        try:
            from mido import MidiFile
        except ImportError:
            raise ImportError("Cần cài đặt mido: pip install mido")
        
        midi = MidiFile(midi_path)
        times = []
        frequencies = []
        current_time = 0
        
        for track in midi.tracks:
            current_time = 0
            for msg in track:
                current_time += msg.time
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    # Convert MIDI note to Hz
                    midi_note = msg.note
                    freq = 440 * (2 ** ((midi_note - 69) / 12))
                    times.append(current_time)
                    frequencies.append(freq)
        
        return np.array(times), np.array(frequencies)


def hz_to_cents(hz: np.ndarray, reference_hz: float = 440.0) -> np.ndarray:
    """
    Chuyển đổi Hz sang Cents (đơn vị đo cao độ tương đối)
    
    Args:
        hz: Mảng tần số (Hz)
        reference_hz: Tần số tham chiếu (mặc định A4 = 440Hz)
    
    Returns:
        Mảng giá trị Cents
    """
    return 1200 * np.log2(hz / reference_hz)


def cents_to_hz(cents: np.ndarray, reference_hz: float = 440.0) -> np.ndarray:
    """
    Chuyển đổi Cents sang Hz
    
    Args:
        cents: Mảng giá trị Cents
        reference_hz: Tần số tham chiếu (mặc định A4 = 440Hz)
    
    Returns:
        Mảng tần số (Hz)
    """
    return reference_hz * (2 ** (cents / 1200))

