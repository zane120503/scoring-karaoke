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
    
    def __init__(self, method: str = 'crepe', model_capacity: str = 'tiny', normalize_audio: bool = True):
        """
        Args:
            method: 'crepe' hoặc 'basic_pitch'
            model_capacity: Chỉ dùng cho CREPE - 'tiny', 'small', 'medium', 'large', 'full'
                          (mặc định 'tiny' - nhanh nhất cho karaoke real-time)
            normalize_audio: Có normalize audio trước khi extract pitch không (mặc định True)
                           - True: Normalize để đảm bảo công bằng khi so sánh
                           - False: Giữ nguyên volume gốc
        """
        self.method = method
        self.model_capacity = model_capacity
        self.normalize_audio = normalize_audio
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
            
            # Kiểm tra phiên bản TensorFlow
            tf_version = tf.__version__
            major, minor = map(int, tf_version.split('.')[:2])
            if major > 2 or (major == 2 and minor >= 15):
                print("⚠️ Cảnh báo: Basic Pitch có thể không tương thích với TensorFlow >= 2.15")
                print(f"   Phiên bản TensorFlow hiện tại: {tf_version}")
                print("   Khuyến nghị: Sử dụng CREPE thay thế hoặc downgrade TensorFlow < 2.15.1")
            
            self._basic_pitch_model = {
                'predict': predict,
                'model_path': ICASSP_2022_MODEL_PATH
            }
            return True
        except ImportError:
            print("⚠️ Basic Pitch chưa được cài đặt. Chạy: pip install basic-pitch")
            return False
        except Exception as e:
            print(f"⚠️ Lỗi khi load Basic Pitch: {str(e)}")
            print("   Khuyến nghị: Sử dụng CREPE thay thế (pip install crepe)")
            return False
    
    def extract_pitch_crepe(self, audio_path: str, step_size: int = 50, use_viterbi: bool = False, confidence_threshold: float = 0.4) -> Tuple[np.ndarray, np.ndarray]:
        """
        Trích xuất pitch sử dụng CREPE
        
        Args:
            audio_path: Đường dẫn file audio
            step_size: Độ phân giải tính bằng milliseconds (50ms mặc định cho tốc độ cao, 10ms = 100Hz cho độ chính xác cao)
            use_viterbi: Sử dụng Viterbi smoothing (False để tăng tốc, True cho độ chính xác cao hơn)
            confidence_threshold: Ngưỡng confidence (0.4 mặc định, thấp hơn = giữ lại nhiều điểm hơn)
        
        Returns:
            (time, frequency): Mảng thời gian và mảng tần số (Hz)
        """
        if self._crepe_model is None:
            if not self._load_crepe():
                raise ImportError("Không thể load CREPE model")
        
        # Load audio - chỉ load với độ dài cần thiết nếu audio quá dài
        audio, sr = librosa.load(audio_path, sr=16000)
        
        # Normalize audio để đảm bảo công bằng khi so sánh (nếu được bật)
        # Điều này giúp giảm ảnh hưởng của sự khác biệt về âm lượng
        if self.normalize_audio and len(audio) > 0:
            max_amp = np.max(np.abs(audio))
            if max_amp > 0:
                # Normalize về [-1, 1] range, nhưng giữ nguyên tỷ lệ
                # Sử dụng peak normalization thay vì RMS để tránh làm mất dynamic range
                audio = audio / max_amp * 0.95  # 0.95 để tránh clipping
        
        # CREPE yêu cầu sample rate 16kHz
        # Tắt viterbi để tăng tốc (giảm một chút độ chính xác nhưng nhanh hơn đáng kể)
        time, frequency, confidence, activation = self._crepe_model.predict(
            audio, 
            sr, 
            viterbi=use_viterbi,  # Tắt viterbi để tăng tốc
            model_capacity=self.model_capacity,
            step_size=step_size
        )
        
        # Lọc các pitch không đáng tin cậy với threshold thấp hơn để giữ lại nhiều điểm hơn
        mask = confidence > confidence_threshold
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
        
        try:
            # Basic Pitch trả về MIDI notes, cần convert sang Hz
            model_output, midi_data, note_events = self._basic_pitch_model['predict'](
                audio_path,
                self._basic_pitch_model['model_path']
            )
        except AttributeError as e:
            if "'_UserObject' object has no attribute 'add_slot'" in str(e):
                error_msg = (
                    "❌ Lỗi tương thích TensorFlow với Basic Pitch!\n\n"
                    "Nguyên nhân: Xung đột phiên bản TensorFlow.\n\n"
                    "Giải pháp:\n"
                    "1. Sử dụng CREPE thay thế (khuyến nghị):\n"
                    "   - CREPE hoạt động tốt với TensorFlow mới nhất\n"
                    "   - Chỉ cần: pip install crepe\n\n"
                    "2. Nếu bắt buộc dùng Basic Pitch:\n"
                    "   - Downgrade TensorFlow: pip install 'tensorflow<2.15.1'\n"
                    "   - Hoặc dùng Python 3.10/3.11 thay vì 3.12+\n"
                    "   - Lưu ý: Có thể gây xung đột với các package khác\n"
                )
                raise RuntimeError(error_msg) from e
            else:
                raise
        except Exception as e:
            error_msg = f"Lỗi khi chạy Basic Pitch: {str(e)}\n\n"
            error_msg += "Gợi ý: Thử sử dụng CREPE thay thế (nhanh hơn và ổn định hơn)"
            raise RuntimeError(error_msg) from e
        
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
                    - normalize_audio: Override normalize setting (optional)
        
        Returns:
            (time, frequency): Mảng thời gian và mảng tần số (Hz)
        """
        # Cho phép override normalize_audio trong kwargs
        original_normalize = self.normalize_audio
        if 'normalize_audio' in kwargs:
            self.normalize_audio = kwargs.pop('normalize_audio')
        
        try:
            if self.method == 'crepe':
                step_size = kwargs.get('step_size', 50)  # Mặc định 50ms cho tốc độ cao
                use_viterbi = kwargs.get('use_viterbi', False)  # Tắt viterbi để tăng tốc
                confidence_threshold = kwargs.get('confidence_threshold', 0.4)  # Threshold thấp hơn
                return self.extract_pitch_crepe(audio_path, step_size, use_viterbi, confidence_threshold)
            elif self.method == 'basic_pitch':
                return self.extract_pitch_basic_pitch(audio_path)
            else:
                raise ValueError(f"Method không hợp lệ: {self.method}. Chọn 'crepe' hoặc 'basic_pitch'")
        finally:
            # Khôi phục lại setting gốc
            self.normalize_audio = original_normalize
    
    def extract_pitch_from_midi(self, midi_path: str, 
                                track_filter: Optional[str] = None,
                                pitch_range: Optional[Tuple[float, float]] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Trích xuất pitch từ file MIDI (cho reference)
        
        Args:
            midi_path: Đường dẫn file MIDI
            track_filter: Lọc track theo tên (ví dụ: 'vocal', 'voice', 'melody'). 
                         Nếu None, lấy tất cả track.
                         Có thể dùng 'auto' để tự động tìm track vocal.
            pitch_range: Lọc theo khoảng pitch (Hz). Ví dụ: (80, 2000) cho vocal.
                        Nếu None, không lọc theo pitch.
        
        Returns:
            (time, frequency): Mảng thời gian và mảng tần số (Hz)
        """
        try:
            from mido import MidiFile
            import mido
        except ImportError:
            raise ImportError("Cần cài đặt mido: pip install mido")
        
        midi = MidiFile(midi_path)
        times = []
        frequencies = []
        
        # Từ khóa để nhận diện track vocal
        vocal_keywords = ['vocal', 'voice', 'sing', 'melody', 'lead', 'solo', 'vox']
        
        # Hàm lấy tên track từ messages
        def get_track_name(track):
            for msg in track:
                if msg.type == 'track_name':
                    return msg.name.lower()
            return ''
        
        # Nếu track_filter = 'auto', tự động tìm track vocal
        auto_track_filter = None
        if track_filter == 'auto':
            for track in midi.tracks:
                track_name = get_track_name(track)
                for keyword in vocal_keywords:
                    if keyword in track_name:
                        auto_track_filter = track_name
                        break
                if auto_track_filter:
                    break
        
        # Tempo mặc định (120 BPM = 500000 microseconds per beat)
        tempo = 500000
        
        for track_idx, track in enumerate(midi.tracks):
            # Lọc track theo tên nếu có yêu cầu
            if track_filter == 'auto':
                # Nếu tìm thấy track vocal, chỉ lấy track đó
                if auto_track_filter:
                    track_name = get_track_name(track)
                    if auto_track_filter not in track_name:
                        continue
                # Nếu không tìm thấy track vocal (auto_track_filter = None)
                # thì lấy tất cả track (fallback - tránh mất note)
                # Điều này hữu ích khi file MIDI chỉ có giọng hát nhưng không có tên track
            elif track_filter:
                # Lọc theo tên track cụ thể
                track_name = get_track_name(track)
                if track_filter.lower() not in track_name:
                    continue
            # Nếu track_filter = None, lấy tất cả track
            
            current_time = 0.0
            for msg in track:
                # Cập nhật tempo nếu có
                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                
                # Chuyển đổi ticks sang seconds
                # ticks_per_beat từ MIDI file, tempo từ message
                if midi.ticks_per_beat > 0:
                    current_time += mido.tick2second(msg.time, midi.ticks_per_beat, tempo)
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    # Convert MIDI note to Hz
                    midi_note = msg.note
                    freq = 440 * (2 ** ((midi_note - 69) / 12))
                    
                    # Lọc theo pitch range nếu có
                    if pitch_range:
                        if freq < pitch_range[0] or freq > pitch_range[1]:
                            continue
                    
                    times.append(current_time)
                    frequencies.append(freq)
        
        # Sắp xếp theo thời gian
        if len(times) > 0:
            sorted_indices = np.argsort(times)
            times = np.array(times)[sorted_indices]
            frequencies = np.array(frequencies)[sorted_indices]
        else:
            times = np.array([])
            frequencies = np.array([])
        
        return times, frequencies


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

