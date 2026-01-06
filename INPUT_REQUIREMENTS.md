# 📥 Input Requirements - Yêu Cầu Đầu Vào Cho Thư Viện

## Tổng Quan

Thư viện KaraokeScorer cần **2 file audio** làm input chính, cùng với một số tham số tùy chọn.

---

## 🎯 Input Bắt Buộc

### 1. File Audio của Người Hát (User Audio)

**Tham số:** `user_audio_path` (string)

**Định dạng hỗ trợ:**
- ✅ WAV (`.wav`)
- ✅ MP3 (`.mp3`)
- ✅ FLAC (`.flac`)
- ✅ Các định dạng khác được librosa hỗ trợ

**Yêu cầu:**
- File phải tồn tại và có thể đọc được
- File phải chứa giọng hát (vocal)
- Khuyến nghị: Mono hoặc Stereo, sample rate 16kHz trở lên
- Độ dài: Không giới hạn, nhưng nên > 1 giây

**Ví dụ:**
```cpp
std::string user_audio = "C:/Users/User/Desktop/my_singing.wav";
```

---

### 2. File Audio/MIDI Tham Chiếu (Reference)

**Tham số:** `reference_path` (string)

**Định dạng hỗ trợ:**

#### Audio Files:
- ✅ WAV (`.wav`)
- ✅ MP3 (`.mp3`)
- ✅ FLAC (`.flac`)

#### MIDI Files:
- ✅ MIDI (`.mid`)
- ✅ MIDI (`.midi`)

**Yêu cầu:**
- File phải tồn tại và có thể đọc được
- Nếu là audio: Phải chứa giọng hát chuẩn (ca sĩ mẫu)
- Nếu là MIDI: Phải chứa track vocal (tự động detect hoặc chỉ định)

**Ví dụ:**
```cpp
// Audio reference
std::string ref_audio = "C:/Music/reference_singer.wav";

// MIDI reference
std::string ref_midi = "C:/Music/song_vocal.mid";
```

---

## ⚙️ Input Tùy Chọn (Optional Parameters)

### 3. Method - Phương Pháp Trích Xuất Pitch

**Tham số:** `method` (string, default: `"crepe"`)

**Giá trị:**
- `"crepe"` - Sử dụng CREPE model (khuyến nghị, nhanh hơn)
- `"basic_pitch"` - Sử dụng Basic Pitch model

**Ví dụ:**
```cpp
scorer.score(user_audio, ref_audio, "crepe");  // Mặc định
scorer.score(user_audio, ref_audio, "basic_pitch");
```

**So sánh:**
| Method | Tốc độ | Độ chính xác | Yêu cầu |
|--------|--------|--------------|---------|
| `crepe` | ⭐⭐⭐ Nhanh | ⭐⭐⭐ Cao | TensorFlow |
| `basic_pitch` | ⭐⭐ Trung bình | ⭐⭐⭐ Rất cao | TensorFlow < 2.15 |

---

### 4. Tolerance - Độ Lệch Cho Phép

**Tham số:** `tolerance_cents` (double, default: `200.0`)

**Đơn vị:** Cents (1 semitone = 100 cents)

**Ý nghĩa:**
- Độ lệch pitch cho phép giữa user và reference
- Giá trị càng cao → dễ đạt điểm cao hơn
- Giá trị càng thấp → khó đạt điểm cao hơn (chấm điểm nghiêm hơn)

**Ví dụ:**
```cpp
// Dễ (200 cents = 2 semitones)
scorer.score(user_audio, ref_audio, "crepe", 200.0);

// Trung bình (100 cents = 1 semitone)
scorer.score(user_audio, ref_audio, "crepe", 100.0);

// Khó (50 cents = 0.5 semitone)
scorer.score(user_audio, ref_audio, "crepe", 50.0);
```

**Khuyến nghị:**
- **Easy mode:** 200.0 cents (mặc định)
- **Normal mode:** 100.0 - 150.0 cents
- **Hard mode:** 50.0 - 75.0 cents

---

### 5. Difficulty Mode - Độ Khó Chấm Điểm

**Tham số:** `difficulty_mode` (string, default: `"easy"`)

**Giá trị:**
- `"easy"` - Dễ (khuyến nghị cho người mới)
- `"normal"` - Trung bình
- `"hard"` - Khó (chấm điểm nghiêm ngặt)

**Ý nghĩa:**
- Ảnh hưởng đến cách tính điểm tổng hợp
- `easy`: Ưu tiên accuracy (80%), DTW (20%)
- `normal`: Cân bằng accuracy (75%), DTW (25%)
- `hard`: Cân bằng hơn accuracy (70%), DTW (30%)

**Ví dụ:**
```cpp
scorer.score(user_audio, ref_audio, "crepe", 200.0, "easy");
scorer.score(user_audio, ref_audio, "crepe", 150.0, "normal");
scorer.score(user_audio, ref_audio, "crepe", 100.0, "hard");
```

---

## 📋 Tóm Tắt Input

### Input Tối Thiểu (Chỉ 2 file):
```cpp
KaraokeScorer scorer;
auto result = scorer.score(
    "user_audio.wav",    // Bắt buộc
    "reference.wav"      // Bắt buộc
);
```

### Input Đầy Đủ (Với tất cả tham số):
```cpp
KaraokeScorer scorer;
auto result = scorer.score(
    "user_audio.wav",      // Bắt buộc: File audio người hát
    "reference.wav",       // Bắt buộc: File audio/MIDI tham chiếu
    "crepe",               // Tùy chọn: Method ("crepe" hoặc "basic_pitch")
    200.0,                 // Tùy chọn: Tolerance (cents)
    "easy"                 // Tùy chọn: Difficulty mode
);
```

---

## 🎵 Ví Dụ Thực Tế

### Ví dụ 1: Chấm điểm cơ bản
```cpp
#include "KaraokeScorer.h"
#include <iostream>

int main() {
    KaraokeScorer scorer;
    
    // Input: 2 file audio
    auto result = scorer.score(
        "C:/Recordings/my_singing.wav",
        "C:/Music/original_singer.wav"
    );
    
    std::cout << "Điểm: " << result["final_score"] << std::endl;
    return 0;
}
```

### Ví dụ 2: Sử dụng MIDI làm reference
```cpp
KaraokeScorer scorer;
auto result = scorer.score(
    "my_singing.wav",        // User audio
    "song_vocal.mid",        // MIDI reference
    "crepe",                 // Method
    200.0,                   // Tolerance
    "easy"                   // Difficulty
);
```

### Ví dụ 3: Chấm điểm nghiêm ngặt
```cpp
KaraokeScorer scorer;
auto result = scorer.score(
    "my_singing.wav",
    "reference.wav",
    "crepe",
    50.0,        // Tolerance thấp = chấm điểm nghiêm
    "hard"        // Difficulty cao
);
```

---

## ⚠️ Lưu Ý Quan Trọng

### 1. Đường Dẫn File
- **Windows:** Dùng `\\` hoặc `/`, ví dụ: `"C:\\Music\\song.wav"` hoặc `"C:/Music/song.wav"`
- **Linux/Mac:** Dùng `/`, ví dụ: `"/home/user/music/song.wav"`
- **Relative path:** Có thể dùng relative path từ thư mục chạy chương trình

### 2. File Phải Tồn Tại
```cpp
// ❌ SAI - File không tồn tại
scorer.score("non_existent.wav", "ref.wav");

// ✅ ĐÚNG - Kiểm tra file trước
#include <filesystem>
if (std::filesystem::exists("user.wav")) {
    auto result = scorer.score("user.wav", "ref.wav");
}
```

### 3. Format File
- File audio phải là format hợp lệ (WAV, MP3, FLAC)
- File MIDI phải có track vocal (tự động detect nếu có tên track chứa "vocal", "voice", "sing")

### 4. Chất Lượng Audio
- **Khuyến nghị:** Sample rate ≥ 16kHz
- **Khuyến nghị:** Mono hoặc Stereo
- File quá ngắn (< 0.5s) có thể không detect được pitch

---

## 🔍 Kiểm Tra Input

### Code mẫu để validate input:
```cpp
#include <filesystem>
#include <iostream>

bool validateInput(const std::string& user_path, const std::string& ref_path) {
    // Kiểm tra file tồn tại
    if (!std::filesystem::exists(user_path)) {
        std::cerr << "❌ User audio không tồn tại: " << user_path << std::endl;
        return false;
    }
    
    if (!std::filesystem::exists(ref_path)) {
        std::cerr << "❌ Reference file không tồn tại: " << ref_path << std::endl;
        return false;
    }
    
    // Kiểm tra extension
    std::string user_ext = std::filesystem::path(user_path).extension();
    std::string ref_ext = std::filesystem::path(ref_path).extension();
    
    std::vector<std::string> valid_audio = {".wav", ".mp3", ".flac"};
    std::vector<std::string> valid_midi = {".mid", ".midi"};
    
    bool user_valid = std::find(valid_audio.begin(), valid_audio.end(), user_ext) != valid_audio.end();
    bool ref_valid = std::find(valid_audio.begin(), valid_audio.end(), ref_ext) != valid_audio.end() ||
                     std::find(valid_midi.begin(), valid_midi.end(), ref_ext) != valid_midi.end();
    
    if (!user_valid) {
        std::cerr << "❌ User audio format không hợp lệ: " << user_ext << std::endl;
        return false;
    }
    
    if (!ref_valid) {
        std::cerr << "❌ Reference format không hợp lệ: " << ref_ext << std::endl;
        return false;
    }
    
    std::cout << "✅ Input hợp lệ!" << std::endl;
    return true;
}

int main() {
    std::string user = "my_singing.wav";
    std::string ref = "reference.wav";
    
    if (validateInput(user, ref)) {
        KaraokeScorer scorer;
        auto result = scorer.score(user, ref);
        // ...
    }
    
    return 0;
}
```

---

## 📊 Bảng Tóm Tắt Input

| Tham số | Bắt buộc | Kiểu | Default | Giá trị hợp lệ |
|---------|----------|------|---------|----------------|
| `user_audio_path` | ✅ | string | - | Đường dẫn file audio |
| `reference_path` | ✅ | string | - | Đường dẫn file audio/MIDI |
| `method` | ❌ | string | `"crepe"` | `"crepe"`, `"basic_pitch"` |
| `tolerance_cents` | ❌ | double | `200.0` | Số dương (cents) |
| `difficulty_mode` | ❌ | string | `"easy"` | `"easy"`, `"normal"`, `"hard"` |

---

## 🎯 Kết Luận

**Input tối thiểu cần thiết:**
1. ✅ File audio của người hát (WAV, MP3, FLAC)
2. ✅ File audio/MIDI tham chiếu (WAV, MP3, FLAC, MID, MIDI)

**Input tùy chọn (có default):**
3. Method (mặc định: "crepe")
4. Tolerance (mặc định: 200.0 cents)
5. Difficulty mode (mặc định: "easy")

**Cách sử dụng đơn giản nhất:**
```cpp
KaraokeScorer scorer;
auto result = scorer.score("user.wav", "ref.wav");
```
