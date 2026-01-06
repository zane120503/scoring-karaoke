"""
Test thư viện với file audio thật
"""
import sys
import json
import io
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from library_interface import score_karaoke_and_get_json

def test_with_real_audio():
    """Test với file audio thật"""
    print("=" * 70)
    print("TEST THƯ VIỆN VỚI FILE AUDIO THẬT")
    print("=" * 70)
    print()
    
    # File paths
    user_audio = r"C:\Users\admin\Downloads\giọng khách\khách 3.1.mp3"
    reference_audio = r"C:\Users\admin\Downloads\Hẹn Lần Sau.wav"
    
    # Kiểm tra file tồn tại
    print("Kiểm tra file...")
    if not Path(user_audio).exists():
        print(f"❌ File người hát không tồn tại: {user_audio}")
        return
    else:
        print(f"✅ File người hát: {user_audio}")
        file_size = Path(user_audio).stat().st_size / (1024 * 1024)  # MB
        print(f"   Kích thước: {file_size:.2f} MB")
    
    if not Path(reference_audio).exists():
        print(f"❌ File ca sĩ không tồn tại: {reference_audio}")
        return
    else:
        print(f"✅ File ca sĩ: {reference_audio}")
        file_size = Path(reference_audio).stat().st_size / (1024 * 1024)  # MB
        print(f"   Kích thước: {file_size:.2f} MB")
    
    print()
    print("=" * 70)
    print("BẮT ĐẦU CHẤM ĐIỂM...")
    print("=" * 70)
    print()
    print("⚠️  Lưu ý: Quá trình này có thể mất vài phút tùy độ dài audio")
    print("   Đang xử lý...")
    print()
    
    try:
        # Chấm điểm với default settings
        result_json = score_karaoke_and_get_json(
            user_audio,
            reference_audio,
            method='crepe',           # Sử dụng CREPE (nhanh hơn)
            tolerance_cents=300.0,    # Tolerance 200 cents (easy mode)
            difficulty_mode='easy'     # Độ khó: easy
        )
        
        # Parse JSON
        result = json.loads(result_json)
        
        # Kiểm tra lỗi
        if "error" in result:
            print("❌ LỖI KHI XỬ LÝ:")
            print("=" * 70)
            print(result["error"])
            print("=" * 70)
            return
        
        # Hiển thị kết quả
        print("=" * 70)
        print("KẾT QUẢ CHẤM ĐIỂM")
        print("=" * 70)
        print()
        
        final_score = result.get("final_score", 0.0)
        accuracy = result.get("accuracy", 0.0)
        dtw_score = result.get("dtw_score", 0.0)
        dtw_distance = result.get("dtw_distance", 0.0)
        mae_cents = result.get("mae_cents", 0.0)
        duration = result.get("duration", 0.0)
        
        # Hiển thị điểm với màu sắc
        print(f"📊 ĐIỂM TỔNG HỢP: {final_score:.2f} / 100", end="")
        if final_score >= 80:
            print(" 🟢 (Xuất sắc!)")
        elif final_score >= 60:
            print(" 🟡 (Tốt)")
        else:
            print(" 🔴 (Cần cải thiện)")
        print()
        
        print(f"🎯 Độ Chính Xác:     {accuracy:.2f}%")
        print(f"📈 Điểm DTW:         {dtw_score:.2f} / 100")
        print(f"📏 Khoảng Cách DTW:  {dtw_distance:.2f}")
        print(f"📉 Độ Lệch TB:       {mae_cents:.2f} cents")
        print(f"⏱️  Thời Lượng:      {duration:.2f} giây")
        print()
        
        # JSON đầy đủ
        print("=" * 70)
        print("JSON ĐẦY ĐỦ:")
        print("=" * 70)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print()
        
        # Đánh giá
        print("=" * 70)
        print("ĐÁNH GIÁ:")
        print("=" * 70)
        if final_score >= 90:
            print("🌟 XUẤT SẮC! Bạn hát rất tốt!")
        elif final_score >= 80:
            print("👍 TỐT! Bạn hát khá đúng pitch!")
        elif final_score >= 70:
            print("✅ KHÁ! Có thể cải thiện thêm!")
        elif final_score >= 60:
            print("⚠️  TRUNG BÌNH! Cần luyện tập thêm!")
        else:
            print("📚 CẦN CẢI THIỆN! Hãy luyện tập nhiều hơn!")
        print()
        
    except Exception as e:
        print("=" * 70)
        print("❌ LỖI:")
        print("=" * 70)
        print(str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_real_audio()
