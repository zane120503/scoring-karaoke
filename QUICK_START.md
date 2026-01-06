# Quick Start - Sử Dụng Thư Viện Karaoke Scorer trong C++

## ✅ Kết Quả Test

Thư viện Python đã được test và hoạt động đúng:
- ✅ Hàm có đầy đủ 5 tham số
- ✅ Xử lý lỗi hoạt động đúng
- ✅ JSON format hợp lệ
- ✅ Default parameters hoạt động

## 🚀 Cách Sử Dụng Nhanh

### Bước 1: Cài đặt Dependencies

```bash
pip install crepe librosa numpy scipy fastdtw mido
```

### Bước 2: Biên dịch C++

```bash
mkdir build
cd build
cmake .. -DPython3_EXECUTABLE=python
cmake --build .
```

### Bước 3: Sử dụng trong Code C++

#### Cách Đơn Giản Nhất (Sử dụng Wrapper Class):

```cpp
#include "KaraokeScorer.h"
#include <iostream>

int main() {
    // 1. Khởi tạo
    KaraokeScorer scorer;
    
    // 2. Chấm điểm
    auto result = scorer.score(
        "user_audio.wav",    // File audio của người hát
        "reference.wav"      // File audio/MIDI tham chiếu
    );
    
    // 3. Lấy kết quả
    double final_score = result["final_score"];
    double accuracy = result["accuracy"];
    
    std::cout << "Điểm: " << final_score << std::endl;
    std::cout << "Độ chính xác: " << accuracy << "%" << std::endl;
    
    return 0;
}
```

#### Với Tùy Chọn Nâng Cao:

```cpp
KaraokeScorer scorer;

auto result = scorer.score(
    "user_audio.wav",
    "reference.mid",        // Có thể dùng MIDI
    "crepe",                // Method: "crepe" hoặc "basic_pitch"
    200.0,                  // Tolerance (cents)
    "easy"                  // Difficulty: "easy", "normal", "hard"
);
```

## 📋 API Reference

### Class: `KaraokeScorer`

#### Constructor
```cpp
KaraokeScorer();
```

#### Methods

**`score()`** - Trả về map với kết quả
```cpp
std::map<std::string, double> score(
    const std::string& user_audio_path,
    const std::string& reference_path,
    const std::string& method = "crepe",
    double tolerance_cents = 200.0,
    const std::string& difficulty_mode = "easy"
);
```

**`scoreAsJson()`** - Trả về JSON string
```cpp
std::string scoreAsJson(...);  // Cùng tham số như score()
```

**`isInitialized()`** - Kiểm tra đã khởi tạo chưa
```cpp
bool isInitialized() const;
```

**`getLastError()`** - Lấy lỗi cuối cùng
```cpp
std::string getLastError() const;
```

### Kết Quả Trả Về

Map chứa các trường:
- `final_score`: Điểm tổng hợp (0-100)
- `accuracy`: Độ chính xác (0-100)
- `dtw_score`: Điểm DTW (0-100)
- `dtw_distance`: Khoảng cách DTW
- `mae_cents`: Độ lệch trung bình (cents)
- `duration`: Thời lượng (giây)
- `error`: Thông báo lỗi (nếu có)

## 🧪 Test

### Test Python:
```bash
python test_library.py
```

### Test C++:
```bash
cd build
./test_cpp        # Linux/Mac
test_cpp.exe      # Windows
```

## 📝 Ví Dụ Đầy Đủ

Xem file `test_cpp.cpp` để biết ví dụ đầy đủ về cách sử dụng.

## ⚠️ Lưu Ý

1. Đảm bảo các file Python (`library_interface.py`, `pitch_extractor.py`, `pitch_matcher.py`) nằm trong PYTHONPATH hoặc cùng thư mục với executable
2. Python runtime phải có sẵn khi chạy chương trình C++
3. File audio phải ở định dạng được hỗ trợ: WAV, MP3, FLAC, MID, MIDI

## 📚 Tài Liệu Chi Tiết

Xem `USAGE_GUIDE.md` để biết hướng dẫn chi tiết hơn.
