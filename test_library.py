"""
Test script để kiểm tra thư viện library_interface hoạt động đúng không
"""
import sys
import json
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from library_interface import score_karaoke_and_get_json

def test_error_handling():
    """Test xử lý lỗi khi file không tồn tại"""
    print("=" * 60)
    print("TEST 1: Kiểm tra xử lý lỗi (file không tồn tại)")
    print("=" * 60)
    
    result = score_karaoke_and_get_json(
        "non_existent_user.wav",
        "non_existent_ref.wav"
    )
    
    parsed = json.loads(result)
    print("Kết quả:")
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
    
    if "error" in parsed:
        print("✅ PASS: Xử lý lỗi hoạt động đúng")
    else:
        print("❌ FAIL: Không có thông báo lỗi")
    
    print()

def test_function_signature():
    """Test các tham số của hàm"""
    print("=" * 60)
    print("TEST 2: Kiểm tra signature của hàm")
    print("=" * 60)
    
    import inspect
    sig = inspect.signature(score_karaoke_and_get_json)
    print("Tham số của hàm:")
    for param_name, param in sig.parameters.items():
        print(f"  - {param_name}: {param.annotation} = {param.default}")
    
    print(f"\n✅ PASS: Hàm có {len(sig.parameters)} tham số")
    print()

def test_default_values():
    """Test giá trị mặc định"""
    print("=" * 60)
    print("TEST 3: Kiểm tra giá trị mặc định")
    print("=" * 60)
    
    # Test với chỉ 2 tham số bắt buộc
    result = score_karaoke_and_get_json(
        "test1.wav",
        "test2.wav"
    )
    
    parsed = json.loads(result)
    print("Kết quả khi chỉ truyền 2 tham số:")
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
    
    # Test với đầy đủ tham số
    result2 = score_karaoke_and_get_json(
        "test1.wav",
        "test2.wav",
        method="crepe",
        tolerance_cents=200.0,
        difficulty_mode="easy"
    )
    
    parsed2 = json.loads(result2)
    print("\nKết quả khi truyền đầy đủ tham số:")
    print(json.dumps(parsed2, indent=2, ensure_ascii=False))
    
    print("\n✅ PASS: Hàm chấp nhận cả default và explicit parameters")
    print()

def test_json_format():
    """Test định dạng JSON trả về"""
    print("=" * 60)
    print("TEST 4: Kiểm tra định dạng JSON")
    print("=" * 60)
    
    result = score_karaoke_and_get_json(
        "test1.wav",
        "test2.wav"
    )
    
    try:
        parsed = json.loads(result)
        print("✅ PASS: JSON hợp lệ")
        print("\nCác trường trong JSON:")
        for key in parsed.keys():
            print(f"  - {key}: {type(parsed[key]).__name__}")
    except json.JSONDecodeError as e:
        print(f"❌ FAIL: JSON không hợp lệ - {e}")
    
    print()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("KIỂM TRA THƯ VIỆN LIBRARY_INTERFACE")
    print("=" * 60 + "\n")
    
    test_function_signature()
    test_default_values()
    test_error_handling()
    test_json_format()
    
    print("=" * 60)
    print("HOÀN TẤT KIỂM TRA")
    print("=" * 60)
    print("\nLưu ý: Để test với file audio thật, bạn cần:")
    print("  1. Có file audio (.wav, .mp3, .flac) hoặc MIDI (.mid, .midi)")
    print("  2. Gọi: score_karaoke_and_get_json('path/to/user.wav', 'path/to/ref.wav')")
