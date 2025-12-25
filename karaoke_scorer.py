"""
Script chính để chấm điểm karaoke sử dụng Pitch Detection
"""
import argparse
import os
import sys
from pathlib import Path
from pitch_extractor import PitchExtractor
from pitch_matcher import PitchMatcher
import numpy as np


def main():
    parser = argparse.ArgumentParser(
        description='Chấm điểm karaoke sử dụng Pitch Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  # So sánh với file MIDI reference
  python karaoke_scorer.py --user audio_user.wav --reference reference.mid
  
  # So sánh với audio reference (ca sĩ mẫu)
  python karaoke_scorer.py --user audio_user.wav --reference reference.wav --method crepe
  
  # Sử dụng Basic Pitch thay vì CREPE
  python karaoke_scorer.py --user audio_user.wav --reference reference.mid --method basic_pitch
        """
    )
    
    parser.add_argument('--user', '-u', required=True,
                       help='Đường dẫn file audio người hát (Vocal + Beat)')
    parser.add_argument('--reference', '-r', required=True,
                       help='Đường dẫn file reference (MIDI hoặc Audio)')
    parser.add_argument('--method', '-m', default='crepe',
                       choices=['crepe', 'basic_pitch'],
                       help='Phương pháp trích xuất pitch (default: crepe)')
    parser.add_argument('--tolerance', '-t', type=float, default=50.0,
                       help='Độ lệch cho phép tính bằng cents (default: 50)')
    parser.add_argument('--output', '-o',
                       help='Lưu kết quả vào file JSON (tùy chọn)')
    
    args = parser.parse_args()
    
    # Kiểm tra file tồn tại
    if not os.path.exists(args.user):
        print(f"❌ Không tìm thấy file: {args.user}")
        sys.exit(1)
    
    if not os.path.exists(args.reference):
        print(f"❌ Không tìm thấy file: {args.reference}")
        sys.exit(1)
    
    print("🎤 Bắt đầu chấm điểm karaoke...")
    print(f"📁 File người hát: {args.user}")
    print(f"📁 File reference: {args.reference}")
    print(f"🔧 Phương pháp: {args.method}")
    print()
    
    # Khởi tạo Pitch Extractor
    print("⏳ Đang trích xuất pitch từ audio người hát...")
    extractor_user = PitchExtractor(method=args.method)
    try:
        time_user, freq_user = extractor_user.extract_pitch(args.user)
        print(f"✅ Đã trích xuất {len(time_user)} điểm pitch từ audio người hát")
    except Exception as e:
        print(f"❌ Lỗi khi trích xuất pitch từ audio người hát: {e}")
        sys.exit(1)
    
    # Trích xuất pitch từ reference
    print("⏳ Đang trích xuất pitch từ file reference...")
    ref_ext = Path(args.reference).suffix.lower()
    
    if ref_ext == '.mid' or ref_ext == '.midi':
        # File MIDI
        try:
            time_ref, freq_ref = extractor_user.extract_pitch_from_midi(args.reference)
            print(f"✅ Đã trích xuất {len(time_ref)} điểm pitch từ MIDI")
        except Exception as e:
            print(f"❌ Lỗi khi đọc MIDI: {e}")
            sys.exit(1)
    else:
        # File Audio
        extractor_ref = PitchExtractor(method=args.method)
        try:
            time_ref, freq_ref = extractor_ref.extract_pitch(args.reference)
            print(f"✅ Đã trích xuất {len(time_ref)} điểm pitch từ audio reference")
        except Exception as e:
            print(f"❌ Lỗi khi trích xuất pitch từ audio reference: {e}")
            sys.exit(1)
    
    # So khớp và tính điểm
    print()
    print("⏳ Đang so khớp pitch và tính điểm...")
    matcher = PitchMatcher(tolerance_cents=args.tolerance)
    
    try:
        results = matcher.calculate_score(
            time_user, freq_user,
            time_ref, freq_ref
        )
        
        # Hiển thị kết quả
        print()
        print("=" * 50)
        print("📊 KẾT QUẢ CHẤM ĐIỂM")
        print("=" * 50)
        print(f"🎯 Điểm tổng hợp: {results['final_score']:.2f}/100")
        print(f"📈 Độ chính xác: {results['accuracy']:.2f}%")
        print(f"🎵 Điểm DTW: {results['dtw_score']:.2f}/100")
        print(f"📏 Khoảng cách DTW: {results['dtw_distance']:.2f} cents")
        print(f"📉 Độ lệch trung bình: {results['mae_cents']:.2f} cents")
        print(f"⏱️  Thời lượng: {results['duration']:.2f} giây")
        print("=" * 50)
        
        # Lưu kết quả nếu có yêu cầu
        if args.output:
            import json
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Đã lưu kết quả vào: {args.output}")
        
    except Exception as e:
        print(f"❌ Lỗi khi tính điểm: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

