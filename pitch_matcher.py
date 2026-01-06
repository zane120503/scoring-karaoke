"""
So khớp Pitch và tính điểm sử dụng DTW (Dynamic Time Warping)
"""
import numpy as np
from typing import Tuple, Optional
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import warnings
warnings.filterwarnings('ignore')


class PitchMatcher:
    """Lớp so khớp pitch và tính điểm"""
    
    def __init__(self, tolerance_cents: float = 75.0, difficulty_mode: str = 'normal'):
        """
        Args:
            tolerance_cents: Độ lệch cho phép tính bằng cents (75 cents mặc định - dễ hơn)
            difficulty_mode: 'easy', 'normal', 'hard' - điều chỉnh độ khó chấm điểm
        """
        self.tolerance_cents = tolerance_cents
        self.difficulty_mode = difficulty_mode
    
    def interpolate_pitch(self, time: np.ndarray, frequency: np.ndarray, 
                         target_times: np.ndarray) -> np.ndarray:
        """
        Nội suy pitch để có cùng resolution thời gian
        
        Args:
            time: Mảng thời gian gốc
            frequency: Mảng tần số gốc
            target_times: Mảng thời gian đích
        
        Returns:
            Mảng tần số đã nội suy
        """
        if len(time) == 0 or len(frequency) == 0:
            return np.zeros_like(target_times)
        
        # Loại bỏ các giá trị NaN hoặc Inf
        mask = np.isfinite(frequency) & (frequency > 0)
        if np.sum(mask) == 0:
            return np.zeros_like(target_times)
        
        time_clean = time[mask]
        freq_clean = frequency[mask]
        
        # Nội suy tuyến tính
        interpolated = np.interp(target_times, time_clean, freq_clean, 
                                 left=freq_clean[0] if len(freq_clean) > 0 else 0,
                                 right=freq_clean[-1] if len(freq_clean) > 0 else 0)
        
        return interpolated
    
    def align_time_series(self, time1: np.ndarray, freq1: np.ndarray,
                         time2: np.ndarray, freq2: np.ndarray,
                         sample_rate: float = 10.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Căn chỉnh hai chuỗi pitch về cùng resolution thời gian
        
        Args:
            time1: Thời gian của pitch 1
            freq1: Tần số của pitch 1
            time2: Thời gian của pitch 2
            freq2: Tần số của pitch 2
            sample_rate: Số điểm mẫu mỗi giây (Hz)
        
        Returns:
            (aligned_time, aligned_freq1, aligned_freq2)
        """
        # Tìm khoảng thời gian chung
        start_time = max(time1[0] if len(time1) > 0 else 0, 
                        time2[0] if len(time2) > 0 else 0)
        end_time = min(time1[-1] if len(time1) > 0 else 0, 
                      time2[-1] if len(time2) > 0 else 0)
        
        if end_time <= start_time:
            # Không có overlap, tạo timeline từ cả hai
            start_time = min(time1[0] if len(time1) > 0 else 0, 
                           time2[0] if len(time2) > 0 else 0)
            end_time = max(time1[-1] if len(time1) > 0 else 0, 
                         time2[-1] if len(time2) > 0 else 0)
        
        # Tạo timeline mới với resolution cố định
        dt = 1.0 / sample_rate
        aligned_time = np.arange(start_time, end_time + dt, dt)
        
        # Nội suy cả hai chuỗi về timeline mới
        aligned_freq1 = self.interpolate_pitch(time1, freq1, aligned_time)
        aligned_freq2 = self.interpolate_pitch(time2, freq2, aligned_time)
        
        return aligned_time, aligned_freq1, aligned_freq2
    
    def hz_to_cents(self, hz: np.ndarray, reference_hz: float = 440.0) -> np.ndarray:
        """Chuyển đổi Hz sang Cents"""
        with np.errstate(divide='ignore', invalid='ignore'):
            cents = 1200 * np.log2(hz / reference_hz)
            cents = np.nan_to_num(cents, nan=0.0, posinf=0.0, neginf=0.0)
        return cents
    
    def calculate_dtw_distance(self, pitch1: np.ndarray, pitch2: np.ndarray) -> Tuple[float, list]:
        """
        Tính khoảng cách DTW giữa hai chuỗi pitch
        
        Args:
            pitch1: Chuỗi pitch 1 (đã chuyển sang cents)
            pitch2: Chuỗi pitch 2 (đã chuyển sang cents)
        
        Returns:
            (distance, path): Khoảng cách DTW và đường đi
        """
        # Loại bỏ các giá trị không hợp lệ
        mask1 = np.isfinite(pitch1) & (pitch1 != 0)
        mask2 = np.isfinite(pitch2) & (pitch2 != 0)
        
        if np.sum(mask1) == 0 or np.sum(mask2) == 0:
            return float('inf'), []
        
        pitch1_clean = pitch1[mask1]
        pitch2_clean = pitch2[mask2]
        
        # Reshape cho fastdtw (cần 2D array)
        pitch1_2d = pitch1_clean.reshape(-1, 1)
        pitch2_2d = pitch2_clean.reshape(-1, 1)
        
        # Tính DTW
        distance, path = fastdtw(pitch1_2d, pitch2_2d, dist=euclidean)
        
        return distance, path
    
    def calculate_accuracy(self, pitch_user: np.ndarray, pitch_reference: np.ndarray) -> float:
        """
        Tính độ chính xác pitch với điểm trung gian (graded scoring)
        
        Args:
            pitch_user: Pitch người hát (cents)
            pitch_reference: Pitch chuẩn (cents)
        
        Returns:
            Độ chính xác (0-1) với điểm trung gian
        """
        if len(pitch_user) == 0 or len(pitch_reference) == 0:
            return 0.0
        
        # Căn chỉnh về cùng độ dài
        min_len = min(len(pitch_user), len(pitch_reference))
        pitch_user_aligned = pitch_user[:min_len]
        pitch_reference_aligned = pitch_reference[:min_len]
        
        # Loại bỏ các điểm không có pitch (0 hoặc NaN)
        mask = (pitch_user_aligned != 0) & (pitch_reference_aligned != 0) & \
               np.isfinite(pitch_user_aligned) & np.isfinite(pitch_reference_aligned)
        
        if np.sum(mask) == 0:
            return 0.0
        
        pitch_user_valid = pitch_user_aligned[mask]
        pitch_reference_valid = pitch_reference_aligned[mask]
        
        # Tính độ lệch
        deviation = np.abs(pitch_user_valid - pitch_reference_valid)
        
        # Tính điểm với hệ thống điểm trung gian (graded scoring) - CẢI THIỆN ĐỂ DỄ HƠN
        # Điểm giảm dần theo độ lệch thay vì chỉ đúng/sai
        # Mở rộng phạm vi để cho điểm cao hơn
        tolerance_strict = self.tolerance_cents * 0.6   # 60% tolerance = điểm cao (tăng từ 50%)
        tolerance_normal = self.tolerance_cents * 1.2    # 120% tolerance = điểm trung bình (tăng từ 100%)
        tolerance_loose = self.tolerance_cents * 3.0     # 300% tolerance = điểm thấp nhưng vẫn có điểm (tăng từ 200%)
        tolerance_very_loose = self.tolerance_cents * 5.0  # 500% tolerance = vẫn có điểm nhỏ
        
        # Tính điểm cho từng điểm pitch
        scores = np.zeros_like(deviation)
        
        # Điểm cao (1.0) nếu trong tolerance_strict
        scores[deviation <= tolerance_strict] = 1.0
        
        # Điểm trung bình cao (0.7-0.99) nếu trong tolerance_normal nhưng ngoài tolerance_strict
        mask_normal = (deviation > tolerance_strict) & (deviation <= tolerance_normal)
        if np.any(mask_normal):
            # Điểm giảm tuyến tính từ 0.99 xuống 0.7 (tăng từ 0.5)
            scores[mask_normal] = 0.99 - 0.29 * (deviation[mask_normal] - tolerance_strict) / (tolerance_normal - tolerance_strict)
        
        # Điểm trung bình (0.4-0.69) nếu trong tolerance_loose nhưng ngoài tolerance_normal
        mask_loose = (deviation > tolerance_normal) & (deviation <= tolerance_loose)
        if np.any(mask_loose):
            # Điểm giảm tuyến tính từ 0.69 xuống 0.4 (tăng từ 0.49)
            scores[mask_loose] = 0.69 - 0.29 * (deviation[mask_loose] - tolerance_normal) / (tolerance_loose - tolerance_normal)
        
        # Điểm thấp (0.1-0.39) nếu trong tolerance_very_loose nhưng ngoài tolerance_loose
        mask_very_loose = (deviation > tolerance_loose) & (deviation <= tolerance_very_loose)
        if np.any(mask_very_loose):
            # Điểm giảm tuyến tính từ 0.39 xuống 0.1
            scores[mask_very_loose] = 0.39 - 0.29 * (deviation[mask_very_loose] - tolerance_loose) / (tolerance_very_loose - tolerance_loose)
        
        # Điểm 0 nếu ngoài tolerance_very_loose (nhưng không bị trừ điểm)
        
        # Tính accuracy trung bình
        accuracy = np.mean(scores)
        return accuracy
    
    def calculate_score(self, time_user: np.ndarray, freq_user: np.ndarray,
                       time_reference: np.ndarray, freq_reference: np.ndarray,
                       sample_rate: float = 10.0) -> dict:
        """
        Tính điểm số tổng hợp
        
        Args:
            time_user: Thời gian pitch người hát
            freq_user: Tần số pitch người hát (Hz)
            time_reference: Thời gian pitch chuẩn
            freq_reference: Tần số pitch chuẩn (Hz)
            sample_rate: Resolution thời gian (Hz)
        
        Returns:
            Dictionary chứa các điểm số và metrics
        """
        # Căn chỉnh về cùng timeline
        aligned_time, aligned_freq_user, aligned_freq_reference = \
            self.align_time_series(time_user, freq_user, 
                                 time_reference, freq_reference, 
                                 sample_rate)
        
        # Chuyển sang Cents
        cents_user = self.hz_to_cents(aligned_freq_user)
        cents_reference = self.hz_to_cents(aligned_freq_reference)
        
        # Tính accuracy
        accuracy = self.calculate_accuracy(cents_user, cents_reference)
        
        # Tính DTW distance
        dtw_distance, dtw_path = self.calculate_dtw_distance(cents_user, cents_reference)
        
        # Normalize DTW distance thành điểm (0-100)
        # Cải thiện công thức để dễ đạt điểm cao hơn
        # Điều chỉnh max_distance dựa trên difficulty mode
        if self.difficulty_mode == 'easy':
            # Chế độ dễ: tăng max_distance lên 5x để dễ đạt điểm cao hơn
            multiplier = 5.0
        elif self.difficulty_mode == 'normal':
            # Chế độ vừa: tăng max_distance lên 3.5x
            multiplier = 3.5
        else:  # hard
            # Chế độ khó: tăng lên 2.5x (vẫn dễ hơn trước)
            multiplier = 2.5
        
        max_expected_distance = len(aligned_time) * self.tolerance_cents * multiplier
        
        if max_expected_distance > 0:
            # Công thức cải thiện: sử dụng căn bậc 3 để làm mềm đường cong điểm hơn nữa
            # Điều này giúp điểm giảm chậm hơn nhiều khi có sai lệch
            normalized_distance = min(1.0, dtw_distance / max_expected_distance)
            # Sử dụng căn bậc 3 thay vì căn bậc 2 để dễ hơn
            dtw_score = 100 * (1.0 - np.power(normalized_distance, 1.0/3.0))
        else:
            dtw_score = 0.0
        
        # Tính độ lệch trung bình (Mean Absolute Error)
        mask = (cents_user != 0) & (cents_reference != 0) & \
               np.isfinite(cents_user) & np.isfinite(cents_reference)
        if np.sum(mask) > 0:
            mae_cents = np.mean(np.abs(cents_user[mask] - cents_reference[mask]))
        else:
            mae_cents = float('inf')
        
        # Điểm tổng hợp (weighted average)
        # Điều chỉnh tỷ lệ dựa trên difficulty mode - ƯU TIÊN ACCURACY HƠN
        if self.difficulty_mode == 'easy':
            # Chế độ dễ: ưu tiên accuracy rất nhiều (80% accuracy, 20% DTW)
            accuracy_weight = 80
            dtw_weight = 20
        elif self.difficulty_mode == 'normal':
            # Chế độ vừa: ưu tiên accuracy (75% accuracy, 25% DTW)
            accuracy_weight = 75
            dtw_weight = 25
        else:  # hard
            # Chế độ khó: cân bằng hơn (70% accuracy, 30% DTW)
            accuracy_weight = 70
            dtw_weight = 30
        
        # accuracy là 0-1, dtw_score là 0-100
        final_score = accuracy * accuracy_weight + (dtw_score / 100) * dtw_weight
        
        # Đảm bảo điểm không vượt quá 100
        final_score = min(100.0, final_score)
        
        # Bonus: Nếu accuracy > 0.5, thêm điểm bonus nhỏ để khuyến khích
        if accuracy > 0.5:
            bonus = (accuracy - 0.5) * 5  # Tối đa 2.5 điểm bonus
            final_score = min(100.0, final_score + bonus)
        
        return {
            'final_score': round(final_score, 2),
            'accuracy': round(accuracy * 100, 2),
            'dtw_score': round(dtw_score, 2),
            'dtw_distance': round(dtw_distance, 2),
            'mae_cents': round(mae_cents, 2),
            'duration': round(aligned_time[-1] - aligned_time[0], 2) if len(aligned_time) > 0 else 0.0
        }

