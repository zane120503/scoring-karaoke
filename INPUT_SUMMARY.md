# 📥 Tóm Tắt Input Cần Thiết

## ✅ Input Bắt Buộc (2 file)

### 1. File Audio của Người Hát
- **Định dạng:** WAV, MP3, FLAC
- **Ví dụ:** `"C:/Recordings/my_singing.wav"`

### 2. File Audio/MIDI Tham Chiếu
- **Định dạng:** WAV, MP3, FLAC, MID, MIDI
- **Ví dụ:** `"C:/Music/reference.wav"` hoặc `"song.mid"`

---

## ⚙️ Input Tùy Chọn (Có giá trị mặc định)

### 3. Method (Mặc định: `"crepe"`)
- `"crepe"` - Nhanh, chính xác (khuyến nghị)
- `"basic_pitch"` - Rất chính xác nhưng chậm hơn

### 4. Tolerance (Mặc định: `200.0` cents)
- Độ lệch pitch cho phép
- **200.0** = Dễ (2 semitones)
- **100.0** = Trung bình (1 semitone)
- **50.0** = Khó (0.5 semitone)

### 5. Difficulty Mode (Mặc định: `"easy"`)
- `"easy"` - Dễ đạt điểm cao
- `"normal"` - Cân bằng
- `"hard"` - Khó đạt điểm cao

---

## 💻 Code Mẫu

### Cách Đơn Giản Nhất (Chỉ 2 file):
```cpp
#include "KaraokeScorer.h"

int main() {
    KaraokeScorer scorer;
    
    // Chỉ cần 2 file audio
    auto result = scorer.score(
        "user_audio.wav",    // File của người hát
        "reference.wav"      // File tham chiếu
    );
    
    std::cout << "Điểm: " << result["final_score"] << std::endl;
    return 0;
}
```

### Với Tất Cả Tham Số:
```cpp
KaraokeScorer scorer;

auto result = scorer.score(
    "user_audio.wav",      // 1. File người hát (BẮT BUỘC)
    "reference.wav",       // 2. File tham chiếu (BẮT BUỘC)
    "crepe",              // 3. Method (tùy chọn)
    200.0,                // 4. Tolerance (tùy chọn)
    "easy"                // 5. Difficulty (tùy chọn)
);
```

---

## 📋 Bảng Tóm Tắt

| Tham số | Bắt buộc? | Kiểu | Default | Ví dụ |
|---------|-----------|------|---------|-------|
| `user_audio_path` | ✅ | string | - | `"singing.wav"` |
| `reference_path` | ✅ | string | - | `"ref.wav"` hoặc `"ref.mid"` |
| `method` | ❌ | string | `"crepe"` | `"crepe"` hoặc `"basic_pitch"` |
| `tolerance_cents` | ❌ | double | `200.0` | `50.0`, `100.0`, `200.0` |
| `difficulty_mode` | ❌ | string | `"easy"` | `"easy"`, `"normal"`, `"hard"` |

---

## 🎯 Kết Luận

**Tối thiểu cần:** 2 file audio  
**Đầy đủ:** 2 file + 3 tham số tùy chọn

Xem `INPUT_REQUIREMENTS.md` để biết chi tiết.
