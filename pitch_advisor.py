"""
Phân tích Pitch Contour và đưa ra lời khuyên cho người hát
"""
import numpy as np
from typing import Dict, List, Tuple
from pitch_matcher import PitchMatcher


class PitchAdvisor:
    """Lớp phân tích pitch và đưa ra lời khuyên"""
    
    def __init__(self, tolerance_cents: float = 200.0):
        """
        Args:
            tolerance_cents: Độ lệch cho phép tính bằng cents
        """
        self.tolerance_cents = tolerance_cents
    
    def analyze_pitch_contour(self, time_user: np.ndarray, freq_user: np.ndarray,
                              time_reference: np.ndarray, freq_reference: np.ndarray) -> Dict:
        """
        Phân tích pitch contour và đưa ra lời khuyên
        
        Args:
            time_user: Thời gian pitch người hát
            freq_user: Tần số pitch người hát (Hz)
            time_reference: Thời gian pitch chuẩn
            freq_reference: Tần số pitch chuẩn (Hz)
        
        Returns:
            Dictionary chứa các lời khuyên và phân tích
        """
        # Căn chỉnh về cùng timeline
        matcher = PitchMatcher(tolerance_cents=self.tolerance_cents)
        aligned_time, aligned_freq_user, aligned_freq_reference = \
            matcher.align_time_series(time_user, freq_user, time_reference, freq_reference)
        
        # Chuyển sang Cents
        cents_user = matcher.hz_to_cents(aligned_freq_user)
        cents_reference = matcher.hz_to_cents(aligned_freq_reference)
        
        # Loại bỏ các điểm không hợp lệ
        mask = (cents_user != 0) & (cents_reference != 0) & \
               np.isfinite(cents_user) & np.isfinite(cents_reference)
        
        if np.sum(mask) == 0:
            return {
                'advices': ['Không có đủ dữ liệu để phân tích.'],
                'issues': [],
                'strengths': []
            }
        
        cents_user_valid = cents_user[mask]
        cents_reference_valid = cents_reference[mask]
        time_valid = aligned_time[mask]
        
        # Phân tích các vấn đề
        advices = []
        issues = []
        strengths = []
        
        # 1. Phân tích độ lệch trung bình
        avg_deviation = np.mean(np.abs(cents_user_valid - cents_reference_valid))
        if avg_deviation < 50:
            strengths.append("Độ chính xác pitch rất tốt!")
        elif avg_deviation < 100:
            strengths.append("Độ chính xác pitch khá tốt.")
        elif avg_deviation > 200:
            issues.append("Độ lệch pitch trung bình khá lớn")
            advices.append(f"💡 Lời khuyên: Cố gắng hát đúng cao độ hơn. Độ lệch trung bình hiện tại: {avg_deviation:.1f} cents (≈{avg_deviation/100:.1f} semitone)")
        
        # 2. Phân tích xu hướng lệch (cao hơn hay thấp hơn)
        mean_diff = np.mean(cents_user_valid - cents_reference_valid)
        if mean_diff > 50:
            issues.append("Hát cao hơn reference")
            advices.append(f"💡 Lời khuyên: Bạn đang hát cao hơn khoảng {mean_diff:.1f} cents (≈{mean_diff/100:.1f} semitone). Hãy thử hạ giọng xuống một chút.")
        elif mean_diff < -50:
            issues.append("Hát thấp hơn reference")
            advices.append(f"💡 Lời khuyên: Bạn đang hát thấp hơn khoảng {abs(mean_diff):.1f} cents (≈{abs(mean_diff)/100:.1f} semitone). Hãy thử nâng giọng lên một chút.")
        
        # 3. Phân tích độ ổn định (variance)
        user_variance = np.var(cents_user_valid)
        ref_variance = np.var(cents_reference_valid)
        stability_ratio = user_variance / ref_variance if ref_variance > 0 else 1.0
        
        if stability_ratio > 2.0:
            issues.append("Pitch không ổn định")
            advices.append("💡 Lời khuyên: Giọng hát của bạn dao động nhiều. Hãy tập luyện để giữ pitch ổn định hơn, đặc biệt khi hát các nốt dài.")
        elif stability_ratio < 0.5:
            strengths.append("Pitch rất ổn định!")
        
        # 4. Phân tích các đoạn có vấn đề lớn
        deviation = np.abs(cents_user_valid - cents_reference_valid)
        large_error_mask = deviation > self.tolerance_cents * 2
        large_error_ratio = np.sum(large_error_mask) / len(deviation) if len(deviation) > 0 else 0
        
        if large_error_ratio > 0.3:
            issues.append(f"{large_error_ratio*100:.1f}% thời lượng có lệch lớn")
            advices.append(f"💡 Lời khuyên: Có {large_error_ratio*100:.1f}% thời lượng bài hát có lệch pitch lớn. Hãy tập luyện các đoạn này nhiều hơn.")
        
        # 5. Phân tích các đoạn tốt
        good_mask = deviation <= self.tolerance_cents * 0.5
        good_ratio = np.sum(good_mask) / len(deviation) if len(deviation) > 0 else 0
        
        if good_ratio > 0.5:
            strengths.append(f"{good_ratio*100:.1f}% thời lượng hát rất chính xác!")
        
        # 6. Phân tích khoảng pitch (range)
        user_range = np.max(cents_user_valid) - np.min(cents_user_valid)
        ref_range = np.max(cents_reference_valid) - np.min(cents_reference_valid)
        
        if user_range < ref_range * 0.7:
            issues.append("Khoảng pitch hẹp hơn reference")
            advices.append("💡 Lời khuyên: Bạn đang hát trong khoảng pitch hẹp hơn bài gốc. Hãy thử mở rộng vocal range của mình.")
        elif user_range > ref_range * 1.3:
            issues.append("Khoảng pitch rộng hơn reference")
            advices.append("💡 Lời khuyên: Bạn đang hát trong khoảng pitch rộng hơn bài gốc. Hãy tập trung vào các nốt chính của bài hát.")
        
        # 7. Phân tích timing (nếu có thể)
        # Tìm các peak trong cả hai contour
        if len(cents_user_valid) > 10 and len(cents_reference_valid) > 10:
            # Đơn giản hóa: so sánh các điểm quan trọng
            user_peaks = self._find_peaks(cents_user_valid)
            ref_peaks = self._find_peaks(cents_reference_valid)
            
            if len(user_peaks) > 0 and len(ref_peaks) > 0:
                # So sánh timing của peaks
                if len(user_peaks) < len(ref_peaks) * 0.7:
                    issues.append("Thiếu các điểm nhấn")
                    advices.append("💡 Lời khuyên: Bạn đang bỏ qua một số điểm nhấn quan trọng trong bài hát. Hãy chú ý đến các nốt cao và các điểm nhấn.")
        
        # Tổng hợp kết quả
        result = {
            'advices': advices if advices else ['🎉 Tuyệt vời! Bạn đang hát rất tốt!'],
            'issues': issues,
            'strengths': strengths,
            'metrics': {
                'avg_deviation_cents': round(avg_deviation, 2),
                'mean_diff_cents': round(mean_diff, 2),
                'stability_ratio': round(stability_ratio, 2),
                'large_error_ratio': round(large_error_ratio * 100, 2),
                'good_ratio': round(good_ratio * 100, 2),
                'user_range_cents': round(user_range, 2),
                'ref_range_cents': round(ref_range, 2)
            }
        }
        
        return result
    
    def _find_peaks(self, data: np.ndarray, min_height: float = None) -> List[int]:
        """Tìm các peak trong dữ liệu"""
        if len(data) < 3:
            return []
        
        peaks = []
        if min_height is None:
            min_height = np.std(data) * 0.5
        
        for i in range(1, len(data) - 1):
            if data[i] > data[i-1] and data[i] > data[i+1] and data[i] > min_height:
                peaks.append(i)
        
        return peaks
    
    def get_summary_advice(self, analysis_result: Dict) -> str:
        """
        Tạo tóm tắt lời khuyên ngắn gọn
        
        Args:
            analysis_result: Kết quả từ analyze_pitch_contour
        
        Returns:
            Chuỗi tóm tắt lời khuyên
        """
        summary_parts = []
        
        if analysis_result['strengths']:
            summary_parts.append("✅ Điểm mạnh:")
            for strength in analysis_result['strengths']:
                summary_parts.append(f"   • {strength}")
        
        if analysis_result['issues']:
            summary_parts.append("\n⚠️ Cần cải thiện:")
            for issue in analysis_result['issues']:
                summary_parts.append(f"   • {issue}")
        
        if analysis_result['advices']:
            summary_parts.append("\n💡 Lời khuyên:")
            for advice in analysis_result['advices'][:5]:  # Chỉ lấy 5 lời khuyên đầu
                summary_parts.append(f"   {advice}")
        
        return "\n".join(summary_parts) if summary_parts else "Không có dữ liệu để phân tích."

