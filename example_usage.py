"""
Ví dụ sử dụng Karaoke Scorer
"""
from pitch_extractor import PitchExtractor
from pitch_matcher import PitchMatcher
import numpy as np


def example_1_audio_vs_midi():
    """Ví dụ 1: So sánh audio người hát với MIDI reference"""
    print("=" * 60)
    print("VÍ DỤ 1: So sánh Audio vs MIDI")
    print("=" * 60)
    
    # Khởi tạo extractor
    extractor = PitchExtractor(method='crepe')
    
    # Trích xuất pitch từ audio người hát
    print("\n1. Trích xuất pitch từ audio người hát...")
    time_user, freq_user = extractor.extract_pitch('path/to/user_audio.wav')
    print(f"   ✅ Đã trích xuất {len(time_user)} điểm pitch")
    
    # Trích xuất pitch từ MIDI reference
    print("\n2. Trích xuất pitch từ MIDI reference...")
    time_ref, freq_ref = extractor.extract_pitch_from_midi('path/to/reference.mid')
    print(f"   ✅ Đã trích xuất {len(time_ref)} điểm pitch")
    
    # So khớp và tính điểm
    print("\n3. So khớp và tính điểm...")
    matcher = PitchMatcher(tolerance_cents=50.0)
    results = matcher.calculate_score(time_user, freq_user, time_ref, freq_ref)
    
    print(f"\n📊 Kết quả:")
    print(f"   Điểm tổng hợp: {results['final_score']:.2f}/100")
    print(f"   Độ chính xác: {results['accuracy']:.2f}%")
    print(f"   Điểm DTW: {results['dtw_score']:.2f}/100")


def example_2_audio_vs_audio():
    """Ví dụ 2: So sánh audio người hát với audio ca sĩ mẫu"""
    print("\n" + "=" * 60)
    print("VÍ DỤ 2: So sánh Audio vs Audio")
    print("=" * 60)
    
    # Khởi tạo extractor với Basic Pitch
    extractor = PitchExtractor(method='basic_pitch')
    
    # Trích xuất pitch từ cả hai audio
    print("\n1. Trích xuất pitch từ audio người hát...")
    time_user, freq_user = extractor.extract_pitch('path/to/user_audio.wav')
    print(f"   ✅ Đã trích xuất {len(time_user)} điểm pitch")
    
    print("\n2. Trích xuất pitch từ audio ca sĩ mẫu...")
    time_ref, freq_ref = extractor.extract_pitch('path/to/reference_audio.wav')
    print(f"   ✅ Đã trích xuất {len(time_ref)} điểm pitch")
    
    # So khớp và tính điểm
    print("\n3. So khớp và tính điểm...")
    matcher = PitchMatcher(tolerance_cents=50.0)
    results = matcher.calculate_score(time_user, freq_user, time_ref, freq_ref)
    
    print(f"\n📊 Kết quả:")
    print(f"   Điểm tổng hợp: {results['final_score']:.2f}/100")
    print(f"   Độ chính xác: {results['accuracy']:.2f}%")
    print(f"   Điểm DTW: {results['dtw_score']:.2f}/100")


def example_3_custom_tolerance():
    """Ví dụ 3: Sử dụng tolerance tùy chỉnh"""
    print("\n" + "=" * 60)
    print("VÍ DỤ 3: Tolerance tùy chỉnh")
    print("=" * 60)
    
    extractor = PitchExtractor(method='crepe')
    time_user, freq_user = extractor.extract_pitch('path/to/user_audio.wav')
    time_ref, freq_ref = extractor.extract_pitch_from_midi('path/to/reference.mid')
    
    # Thử với các tolerance khác nhau
    tolerances = [25.0, 50.0, 100.0]  # 25 cents, 50 cents, 100 cents
    
    print("\nSo sánh với các tolerance khác nhau:")
    for tol in tolerances:
        matcher = PitchMatcher(tolerance_cents=tol)
        results = matcher.calculate_score(time_user, freq_user, time_ref, freq_ref)
        print(f"\n  Tolerance: {tol} cents")
        print(f"    Điểm tổng hợp: {results['final_score']:.2f}/100")
        print(f"    Độ chính xác: {results['accuracy']:.2f}%")


def example_4_visualize_pitch():
    """Ví dụ 4: Visualize pitch contour (cần matplotlib)"""
    print("\n" + "=" * 60)
    print("VÍ DỤ 4: Visualize Pitch Contour")
    print("=" * 60)
    
    try:
        import matplotlib.pyplot as plt
        
        extractor = PitchExtractor(method='crepe')
        time_user, freq_user = extractor.extract_pitch('path/to/user_audio.wav')
        time_ref, freq_ref = extractor.extract_pitch_from_midi('path/to/reference.mid')
        
        # Vẽ biểu đồ
        plt.figure(figsize=(12, 6))
        plt.plot(time_user, freq_user, label='Người hát', alpha=0.7, linewidth=1)
        plt.plot(time_ref, freq_ref, label='Reference', alpha=0.7, linewidth=1)
        plt.xlabel('Thời gian (s)')
        plt.ylabel('Tần số (Hz)')
        plt.title('Pitch Contour Comparison')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('pitch_comparison.png', dpi=150)
        print("\n✅ Đã lưu biểu đồ vào: pitch_comparison.png")
        
    except ImportError:
        print("\n⚠️  Cần cài đặt matplotlib để visualize: pip install matplotlib")


if __name__ == '__main__':
    print("🎤 VÍ DỤ SỬ DỤNG KARAOKE SCORER")
    print("\nLưu ý: Cần thay đổi đường dẫn file trong code để chạy thử")
    print("\nCác ví dụ:")
    print("  1. So sánh Audio vs MIDI")
    print("  2. So sánh Audio vs Audio")
    print("  3. Tolerance tùy chỉnh")
    print("  4. Visualize pitch contour")
    
    # Uncomment để chạy ví dụ cụ thể
    # example_1_audio_vs_midi()
    # example_2_audio_vs_audio()
    # example_3_custom_tolerance()
    # example_4_visualize_pitch()

