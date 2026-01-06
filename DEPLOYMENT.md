# 🚀 Hướng Dẫn Deploy và Sử Dụng Thư Viện

## Tóm Tắt: Có Cần Clone Code Không?

### ❌ KHÔNG BẮT BUỘC phải clone toàn bộ code!

Có **3 cách** để project C++ bên ngoài sử dụng thư viện này:

---

## 🎯 Cách 1: Add Subdirectory (Khuyến nghị)

### Khi nào dùng:
- Development/Testing
- Muốn dễ dàng customize
- Muốn tự động update khi thư viện thay đổi

### Cách làm:

**1. Clone thư viện về một nơi:**
```bash
git clone <repo-url> /path/to/scoring-karaoke
```

**2. Trong CMakeLists.txt của project bạn:**
```cmake
cmake_minimum_required(VERSION 3.10)
project(MyApp)

# Chỉ cần 1 dòng này!
add_subdirectory(/path/to/scoring-karaoke)

add_executable(my_app main.cpp)
target_link_libraries(my_app PRIVATE KaraokeScorer)
```

**3. Sử dụng trong code:**
```cpp
#include "KaraokeScorer.h"

int main() {
    KaraokeScorer scorer;
    auto result = scorer.score("user.wav", "ref.wav");
    return 0;
}
```

**✅ Ưu điểm:**
- Đơn giản nhất
- Tự động link dependencies
- Có thể sửa code nếu cần

**❌ Nhược điểm:**
- Phải clone code về (nhưng chỉ 1 lần)

---

## 🎯 Cách 2: Install và Find Package

### Khi nào dùng:
- Production
- Muốn dùng cho nhiều project
- Không muốn clone code vào project

### Cách làm:

**1. Build và install thư viện (1 lần):**
```bash
cd scoring-karaoke
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local
cmake --build .
cmake --install .
```

**2. Trong CMakeLists.txt của project bạn:**
```cmake
find_package(KaraokeScorer REQUIRED)
target_link_libraries(my_app PRIVATE KaraokeScorer::KaraokeScorer)
```

**3. Build project của bạn:**
```bash
cmake .. -DKaraokeScorer_DIR=/usr/local/lib/cmake/KaraokeScorer
cmake --build .
```

**✅ Ưu điểm:**
- Không cần clone code vào project
- Sạch sẽ, professional
- Có thể dùng cho nhiều project

**❌ Nhược điểm:**
- Cần build và install trước
- Phức tạp hơn một chút

---

## 🎯 Cách 3: Copy Files

### Khi nào dùng:
- Quick prototype
- Muốn tối giản
- Không muốn phụ thuộc vào cấu trúc thư mục

### Cách làm:

**1. Copy 3 files vào project:**
- `KaraokeScorer.h`
- `KaraokeScorer.cpp`
- Các file Python

**2. Thêm vào CMakeLists.txt:**
```cmake
find_package(Python3 REQUIRED)

add_library(KaraokeScorer STATIC KaraokeScorer.cpp)
target_include_directories(KaraokeScorer PUBLIC .)
target_link_libraries(KaraokeScorer PUBLIC ${Python3_LIBRARIES})
```

**✅ Ưu điểm:**
- Không cần clone gì cả
- Tự do customize

**❌ Nhược điểm:**
- Phải tự quản lý dependencies
- Không tự động update

---

## 📊 So Sánh Nhanh

| | Add Subdirectory | Find Package | Copy Files |
|---|---|---|---|
| **Cần clone?** | ✅ Có (1 lần) | ❌ Không | ❌ Không |
| **Độ phức tạp** | ⭐ Dễ | ⭐⭐ Trung bình | ⭐ Dễ |
| **Phù hợp** | Development | Production | Prototype |

---

## 🎓 Khuyến Nghị

- **Lần đầu sử dụng:** Dùng Cách 1 (add_subdirectory) - đơn giản nhất
- **Production:** Dùng Cách 2 (find_package) - professional
- **Quick test:** Dùng Cách 3 (copy files) - nhanh nhất

---

## 📝 Checklist

Khi tích hợp vào project của bạn, đảm bảo:

- [ ] Python đã được cài đặt
- [ ] Đã cài dependencies: `pip install crepe librosa numpy scipy fastdtw mido`
- [ ] Các file Python có trong PYTHONPATH hoặc cùng thư mục với executable
- [ ] CMake tìm thấy Python
- [ ] Link đúng với KaraokeScorer library

---

## 🔗 Tài Liệu Tham Khảo

- `README_INTEGRATION.md` - Hướng dẫn chi tiết
- `INTEGRATION_GUIDE.md` - Hướng dẫn tích hợp
- `example_external_project/` - Ví dụ đầy đủ
