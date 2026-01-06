"""
Script test để kiểm tra xem hệ thống có làm mất note khi MIDI chỉ có giọng hát không
"""
import numpy as np
from pitch_extractor import PitchExtractor


def test_vocal_only_midi():
    """Test với MIDI chỉ có giọng hát"""
    print("🧪 Test: MIDI chỉ có giọng hát (không có beat)")
    print("=" * 70)
    
    # Giả sử bạn có file MIDI chỉ có giọng hát
    # Thay đổi đường dẫn này thành file MIDI thực tế của bạn
    midi_path = input("Nhập đường dẫn file MIDI (hoặc Enter để bỏ qua): ").strip()
    
    if not midi_path:
        print("⚠️  Bỏ qua test (không có file MIDI)")
        return
    
    try:
        extractor = PitchExtractor()
        
        # Test 1: Auto filter
        print("\n📋 Test 1: track_filter='auto'")
        time1, freq1 = extractor.extract_pitch_from_midi(midi_path, track_filter='auto')
        print(f"   ✅ Số note: {len(time1)}")
        print(f"   ✅ Pitch range: {min(freq1):.1f} - {max(freq1):.1f} Hz" if len(freq1) > 0 else "   ⚠️  Không có note")
        
        # Test 2: Không filter (None)
        print("\n📋 Test 2: track_filter=None (lấy tất cả)")
        time2, freq2 = extractor.extract_pitch_from_midi(midi_path, track_filter=None)
        print(f"   ✅ Số note: {len(time2)}")
        print(f"   ✅ Pitch range: {min(freq2):.1f} - {max(freq2):.1f} Hz" if len(freq2) > 0 else "   ⚠️  Không có note")
        
        # So sánh
        print("\n📊 So sánh:")
        if len(time1) == len(time2):
            print(f"   ✅ Số note giống nhau: {len(time1)}")
            print("   ✅ Hệ thống KHÔNG làm mất note khi dùng 'auto'")
        else:
            print(f"   ⚠️  Số note khác nhau: auto={len(time1)}, all={len(time2)}")
            print("   💡 Có thể do lọc theo tên track")
        
        # Test 3: Với pitch range filter
        print("\n📋 Test 3: track_filter='auto' + pitch_range=(80, 2000)")
        time3, freq3 = extractor.extract_pitch_from_midi(
            midi_path, 
            track_filter='auto',
            pitch_range=(80, 2000)
        )
        print(f"   ✅ Số note: {len(time3)}")
        if len(freq3) > 0:
            print(f"   ✅ Pitch range: {min(freq3):.1f} - {max(freq3):.1f} Hz")
            if len(time3) < len(time1):
                print(f"   ⚠️  Đã lọc bỏ {len(time1) - len(time3)} note ngoài range 80-2000 Hz")
            else:
                print("   ✅ Tất cả note đều trong range vocal")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_vocal_only_midi()

