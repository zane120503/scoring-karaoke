# 📚 Hướng Dẫn Sử Dụng Thư Viện Từ Project C++ Bên Ngoài

## ❓ Câu Hỏi: Có Cần Clone Toàn Bộ Code Không?

**Trả lời ngắn gọn:** 
- **Không bắt buộc!** Có 3 cách, tùy nhu cầu của bạn.

## 🎯 3 Cách Sử Dụng Thư Viện

### ✅ Cách 1: Add Subdirectory (Khuyến nghị - Đơn giản nhất)

**Không cần clone toàn bộ, chỉ cần thêm vào CMakeLists.txt của bạn:**

```cmake
# Trong CMakeLists.txt của project bạn
add_subdirectory(path/to/scoring-karaoke)

add_executable(my_app main.cpp)
target_link_libraries(my_app PRIVATE KaraokeScorer)
```

**Cách làm:**
1. Clone hoặc download thư mục `scoring karaoke` về máy
2. Trong project của bạn, thêm:
   ```cmake
   add_subdirectory(/path/to/scoring-karaoke)
   ```
3. Link với library:
   ```cmake
   target_link_libraries(your_target PRIVATE KaraokeScorer)
   ```

**Ưu điểm:**
- ✅ Đơn giản, không cần cấu hình phức tạp
- ✅ Tự động link dependencies
- ✅ Có thể sửa code thư viện nếu cần

**Ví dụ đầy đủ:**
```cmake
cmake_minimum_required(VERSION 3.10)
project(MyKaraokeApp)

# Thêm thư viện (chỉ cần 1 dòng!)
add_subdirectory(external/scoring-karaoke)

# Tạo app của bạn
add_executable(my_app main.cpp)

# Link với thư viện (tự động có include directories)
target_link_libraries(my_app PRIVATE KaraokeScorer)
```

```cpp
// main.cpp
#include "KaraokeScorer.h"  // Tự động tìm thấy!

int main() {
    KaraokeScorer scorer;
    auto result = scorer.score("user.wav", "ref.wav");
    std::cout << "Điểm: " << result["final_score"] << std::endl;
    return 0;
}
```

---

### ✅ Cách 2: Install và Find Package (Production)

**Build một lần, dùng nhiều project:**

```bash
# 1. Build và install thư viện
cd scoring-karaoke
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local
cmake --build .
cmake --install .
```

```cmake
# 2. Trong project của bạn
find_package(KaraokeScorer REQUIRED)
target_link_libraries(my_app PRIVATE KaraokeScorer::KaraokeScorer)
```

**Ưu điểm:**
- ✅ Sạch sẽ, không cần clone code vào project
- ✅ Có thể dùng cho nhiều project
- ✅ Giống như các thư viện khác (Boost, OpenCV)

---

### ✅ Cách 3: Copy Files (Đơn giản nhất cho prototype)

**Chỉ copy vài file cần thiết:**

1. Copy 3 files:
   - `KaraokeScorer.h`
   - `KaraokeScorer.cpp`
   - Các file Python (`library_interface.py`, `pitch_extractor.py`, `pitch_matcher.py`)

2. Thêm vào CMakeLists.txt của bạn:
```cmake
find_package(Python3 REQUIRED)

add_library(KaraokeScorer STATIC KaraokeScorer.cpp)
target_include_directories(KaraokeScorer PUBLIC .)
target_link_libraries(KaraokeScorer PUBLIC ${Python3_LIBRARIES})
target_include_directories(KaraokeScorer PUBLIC ${Python3_INCLUDE_DIRS})
```

**Ưu điểm:**
- ✅ Không cần clone gì cả
- ✅ Tự do customize

---

## 📋 So Sánh 3 Cách

| Tiêu chí | Add Subdirectory | Find Package | Copy Files |
|----------|------------------|--------------|------------|
| **Độ phức tạp** | ⭐ Dễ | ⭐⭐ Trung bình | ⭐ Dễ |
| **Cần clone code?** | ✅ Có (1 lần) | ❌ Không | ❌ Không |
| **Tự động update?** | ✅ Có | ❌ Không | ❌ Không |
| **Dễ customize?** | ✅ Có | ❌ Không | ✅ Có |
| **Phù hợp cho** | Development | Production | Quick test |

---

## 🚀 Quick Start - Cách Nhanh Nhất

**Bước 1:** Clone thư viện về một nơi nào đó
```bash
git clone <your-repo> /path/to/scoring-karaoke
```

**Bước 2:** Trong project của bạn, thêm vào `CMakeLists.txt`:
```cmake
add_subdirectory(/path/to/scoring-karaoke)
```

**Bước 3:** Link với library:
```cmake
target_link_libraries(your_target PRIVATE KaraokeScorer)
```

**Bước 4:** Sử dụng trong code:
```cpp
#include "KaraokeScorer.h"

KaraokeScorer scorer;
auto result = scorer.score("user.wav", "ref.wav");
```

**Xong!** Không cần cấu hình gì thêm.

---

## 📝 Lưu Ý Quan Trọng

### 1. File Python Phải Có Sẵn

Khi chạy chương trình, các file Python phải có trong:
- Cùng thư mục với executable, HOẶC
- Trong PYTHONPATH

**Giải pháp:** Copy các file Python vào thư mục build:
```cmake
# Trong CMakeLists.txt của bạn
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/external/scoring-karaoke/library_interface.py
    ${CMAKE_CURRENT_BINARY_DIR}/library_interface.py
    COPYONLY
)
```

### 2. Python Dependencies

Đảm bảo đã cài:
```bash
pip install crepe librosa numpy scipy fastdtw mido
```

### 3. Python Runtime

Python phải có sẵn khi chạy chương trình.

---

## 🔍 Ví Dụ Đầy Đủ

Xem thư mục `example_external_project/` để xem ví dụ đầy đủ.

---

## ❓ FAQ

**Q: Có thể dùng mà không clone code không?**
A: Có! Dùng Cách 2 (find_package) hoặc Cách 3 (copy files).

**Q: Có thể dùng như header-only library không?**
A: Không, vì cần link với Python libraries.

**Q: Có thể dùng trong nhiều project cùng lúc không?**
A: Có! Dùng Cách 2 (install một lần, dùng nhiều nơi).

**Q: Có cần sửa code thư viện không?**
A: Không cần! Nhưng nếu muốn, dùng Cách 1 hoặc Cách 3.

---

## 📚 Tài Liệu Tham Khảo

- `INTEGRATION_GUIDE.md` - Hướng dẫn chi tiết
- `QUICK_START.md` - Hướng dẫn nhanh
- `USAGE_GUIDE.md` - API reference
