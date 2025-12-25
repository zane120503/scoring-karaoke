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
    
    def __init__(self, tolerance_cents: float = 50.0):
        """
        Args:
            tolerance_cents: Độ lệch cho phép tính bằng cents (50 cents ≈ 1/4 tone)
        """
        self.tolerance_cents = tolerance_cents
    
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
        Tính độ chính xác pitch (tỷ lệ các nốt trong tolerance)
        
        Args:
            pitch_user: Pitch người hát (cents)
            pitch_reference: Pitch chuẩn (cents)
        
        Returns:
            Độ chính xác (0-1)
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
        
        # Đếm số điểm trong tolerance
        in_tolerance = np.sum(deviation <= self.tolerance_cents)
        
        accuracy = in_tolerance / len(deviation)
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
        # Sử dụng công thức: score = max(0, 100 - (distance / max_distance) * 100)
        # max_distance ước tính dựa trên độ dài chuỗi
        max_expected_distance = len(aligned_time) * self.tolerance_cents * 2
        if max_expected_distance > 0:
            dtw_score = max(0, 100 - (dtw_distance / max_expected_distance) * 100)
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
        # Accuracy: 60%, DTW Score: 40%
        # accuracy là 0-1, dtw_score là 0-100
        final_score = accuracy * 60 + (dtw_score / 100) * 40
        
        return {
            'final_score': round(final_score, 2),
            'accuracy': round(accuracy * 100, 2),
            'dtw_score': round(dtw_score, 2),
            'dtw_distance': round(dtw_distance, 2),
            'mae_cents': round(mae_cents, 2),
            'duration': round(aligned_time[-1] - aligned_time[0], 2) if len(aligned_time) > 0 else 0.0
        }

