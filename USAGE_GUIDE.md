# Hướng Dẫn Sử Dụng Thư Viện Karaoke Scorer trong C++

## Tổng Quan

Thư viện này cho phép bạn chấm điểm karaoke từ C++ bằng cách sử dụng thư viện Python được nhúng (embedded). Thư viện sẽ so sánh pitch của người hát với pitch tham chiếu và trả về điểm số chi tiết.

## Cấu Trúc

```
scoring karaoke/
├── library_interface.py      # Module Python chính
├── pitch_extractor.py        # Trích xuất pitch từ audio
├── pitch_matcher.py          # So khớp và tính điểm
├── KaraokeScorer.h           # Header file C++
├── KaraokeScorer.cpp          # Implementation C++
├── main.cpp                   # Ví dụ sử dụng cơ bản
└── test_cpp.cpp              # Test program
```

## Cài Đặt

### 1. Cài đặt Python và dependencies

```bash
# Cài đặt các thư viện Python cần thiết
pip install crepe librosa numpy scipy fastdtw mido
```

### 2. Biên dịch C++

```bash
# Tạo thư mục build
mkdir build && cd build

# Chạy CMake
cmake .. -DPython3_EXECUTABLE=python

# Biên dịch
cmake --build .
```

## Cách Sử Dụng

### Cách 1: Sử dụng Wrapper Class (KaraokeScorer) - Khuyến nghị

#### Bước 1: Include header

```cpp
#include "KaraokeScorer.h"
```

#### Bước 2: Khởi tạo và sử dụng

```cpp
#include "KaraokeScorer.h"
#include <iostream>

int main() {
    // Khởi tạo scorer
    KaraokeScorer scorer;
    
    // Kiểm tra đã khởi tạo thành công chưa
    if (!scorer.isInitialized()) {
        std::cerr << "Lỗi: " << scorer.getLastError() << std::endl;
        return 1;
    }
    
    // Chấm điểm - Cách 1: Lấy JSON string
    std::string json_result = scorer.scoreAsJson(
        "user_audio.wav",      // File audio của người hát
        "reference.wav"         // File audio/MIDI tham chiếu
    );
    std::cout << "Kết quả JSON: " << json_result << std::endl;
    
    // Chấm điểm - Cách 2: Lấy map (đã parse)
    auto result = scorer.score(
        "user_audio.wav",
        "reference.wav",
        "crepe",        // method: "crepe" hoặc "basic_pitch"
        200.0,          // tolerance_cents: độ lệch cho phép
        "easy"          // difficulty_mode: "easy", "normal", "hard"
    );
    
    // Truy cập kết quả
    double final_score = result["final_score"];    // Điểm tổng hợp (0-100)
    double accuracy = result["accuracy"];          // Độ chính xác (0-100)
    double dtw_score = result["dtw_score"];        // Điểm DTW (0-100)
    double dtw_distance = result["dtw_distance"];  // Khoảng cách DTW
    double mae_cents = result["mae_cents"];        // Độ lệch trung bình (cents)
    double duration = result["duration"];          // Thời lượng (giây)
    
    // Kiểm tra lỗi
    if (result.find("error") != result.end()) {
        std::cerr << "Có lỗi xảy ra!" << std::endl;
    } else {
        std::cout << "Điểm số: " << final_score << std::endl;
        std::cout << "Độ chính xác: " << accuracy << "%" << std::endl;
    }
    
    return 0;
}
```

### Cách 2: Sử dụng trực tiếp Python C API (Advanced)

Xem file `main.cpp` để biết cách sử dụng trực tiếp Python C API.

## API Reference

### Class: KaraokeScorer

#### Constructor
```cpp
KaraokeScorer();
```
Khởi tạo Python interpreter và thiết lập môi trường.

#### Destructor
```cpp
~KaraokeScorer();
```
Dọn dẹp tài nguyên (không finalize Python interpreter).

#### Methods

##### `score()`
```cpp
std::map<std::string, double> score(
    const std::string& user_audio_path,
    const std::string& reference_path,
    const std::string& method = "crepe",
    double tolerance_cents = 200.0,
    const std::string& difficulty_mode = "easy"
);
```

**Tham số:**
- `user_audio_path`: Đường dẫn file audio của người hát (WAV, MP3, FLAC)
- `reference_path`: Đường dẫn file audio/MIDI tham chiếu (WAV, MP3, FLAC, MID, MIDI)
- `method`: Phương pháp trích xuất pitch ("crepe" hoặc "basic_pitch")
- `tolerance_cents`: Độ lệch cho phép tính bằng cents (mặc định: 200.0)
- `difficulty_mode`: Độ khó ("easy", "normal", "hard")

**Trả về:** Map chứa kết quả chấm điểm

**Kết quả bao gồm:**
- `final_score`: Điểm tổng hợp (0-100)
- `accuracy`: Độ chính xác pitch (0-100)
- `dtw_score`: Điểm DTW (0-100)
- `dtw_distance`: Khoảng cách DTW
- `mae_cents`: Độ lệch trung bình (cents)
- `duration`: Thời lượng audio (giây)
- `error`: Thông báo lỗi (nếu có)

##### `scoreAsJson()`
```cpp
std::string scoreAsJson(
    const std::string& user_audio_path,
    const std::string& reference_path,
    const std::string& method = "crepe",
    double tolerance_cents = 200.0,
    const std::string& difficulty_mode = "easy"
);
```

Tương tự `score()` nhưng trả về JSON string thay vì map.

##### `isInitialized()`
```cpp
bool isInitialized() const;
```
Kiểm tra xem Python interpreter đã được khởi tạo chưa.

##### `getLastError()`
```cpp
std::string getLastError() const;
```
Lấy thông báo lỗi cuối cùng (nếu có).

## Ví Dụ Sử Dụng

### Ví dụ 1: Chấm điểm cơ bản

```cpp
KaraokeScorer scorer;
auto result = scorer.score("user.wav", "reference.wav");
std::cout << "Điểm: " << result["final_score"] << std::endl;
```

### Ví dụ 2: Tùy chỉnh tham số

```cpp
KaraokeScorer scorer;
auto result = scorer.score(
    "user.wav",
    "reference.mid",      // Sử dụng MIDI làm reference
    "crepe",              // Phương pháp CREPE
    150.0,                // Tolerance 150 cents
    "normal"              // Độ khó normal
);
```

### Ví dụ 3: Xử lý lỗi

```cpp
KaraokeScorer scorer;
if (!scorer.isInitialized()) {
    std::cerr << "Lỗi khởi tạo: " << scorer.getLastError() << std::endl;
    return 1;
}

auto result = scorer.score("user.wav", "reference.wav");
if (result.find("error") != result.end()) {
    std::cerr << "Lỗi chấm điểm: " << result["error"] << std::endl;
} else {
    std::cout << "Thành công! Điểm: " << result["final_score"] << std::endl;
}
```

### Ví dụ 4: So sánh nhiều độ khó

```cpp
KaraokeScorer scorer;
std::vector<std::string> difficulties = {"easy", "normal", "hard"};

for (const auto& diff : difficulties) {
    auto result = scorer.score("user.wav", "reference.wav", "crepe", 200.0, diff);
    std::cout << "Độ khó " << diff << ": " << result["final_score"] << std::endl;
}
```

## Định Dạng File Hỗ Trợ

### Input Audio
- WAV
- MP3
- FLAC
- Các định dạng khác được librosa hỗ trợ

### Reference
- Audio files: WAV, MP3, FLAC
- MIDI files: MID, MIDI

## Lưu Ý

1. **Python Runtime**: Cần Python runtime khi chạy chương trình C++
2. **File Python**: Đảm bảo các file Python (`library_interface.py`, `pitch_extractor.py`, `pitch_matcher.py`) nằm trong PYTHONPATH hoặc cùng thư mục với executable
3. **Memory Management**: Python interpreter sẽ được khởi tạo khi tạo `KaraokeScorer` và chỉ finalize khi chương trình kết thúc
4. **Thread Safety**: Hiện tại không thread-safe. Nếu cần multi-threading, mỗi thread nên có instance riêng

## Troubleshooting

### Lỗi: "Failed to import library_interface module"
- Kiểm tra các file Python có trong PYTHONPATH
- Đảm bảo đã cài đặt đầy đủ dependencies

### Lỗi: "Python interpreter not initialized"
- Kiểm tra Python đã được cài đặt
- Kiểm tra CMake đã tìm thấy Python

### Lỗi: "No pitch detected"
- File audio có thể quá ngắn hoặc không có giọng hát
- Thử với file audio khác

## Test

Chạy test program:
```bash
./test_cpp
```

Hoặc test Python trực tiếp:
```bash
python test_library.py
```
