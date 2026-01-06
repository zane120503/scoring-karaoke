# Hướng Dẫn Tích Hợp KaraokeScorer vào Project C++ Bên Ngoài

## 📦 Các Cách Sử Dụng Thư Viện

Có 3 cách để sử dụng thư viện này trong project C++ của bạn:

### Cách 1: Add Subdirectory (Khuyến nghị cho development)

**Khi nào dùng:** Khi bạn muốn clone code về và phát triển cùng lúc

**Cách làm:**

1. Clone hoặc copy thư mục `scoring karaoke` vào project của bạn:
```
MyProject/
├── CMakeLists.txt
├── src/
│   └── main.cpp
└── external/
    └── scoring-karaoke/    # Clone thư viện vào đây
        ├── CMakeLists.txt
        ├── KaraokeScorer.h
        ├── KaraokeScorer.cpp
        └── ...
```

2. Trong `CMakeLists.txt` của bạn:
```cmake
cmake_minimum_required(VERSION 3.10)
project(MyProject)

# Add thư viện
add_subdirectory(external/scoring-karaoke)

# Tạo executable của bạn
add_executable(my_app src/main.cpp)

# Link với thư viện
target_link_libraries(my_app PRIVATE KaraokeScorer)
```

3. Trong code C++:
```cpp
#include "KaraokeScorer.h"  // Tự động tìm thấy nhờ CMake

int main() {
    KaraokeScorer scorer;
    auto result = scorer.score("user.wav", "ref.wav");
    // ...
}
```

**Ưu điểm:**
- ✅ Dễ debug và phát triển
- ✅ Có thể sửa code thư viện nếu cần
- ✅ Không cần install

**Nhược điểm:**
- ❌ Phải clone toàn bộ code
- ❌ Project của bạn phụ thuộc vào cấu trúc thư mục

---

### Cách 2: Install và Find Package (Khuyến nghị cho production)

**Khi nào dùng:** Khi bạn muốn dùng như một library đã được cài đặt

**Cách làm:**

1. **Build và install thư viện:**
```bash
cd scoring-karaoke
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/path/to/install
cmake --build .
cmake --install .
```

2. **Trong CMakeLists.txt của bạn:**
```cmake
cmake_minimum_required(VERSION 3.10)
project(MyProject)

# Tìm thư viện đã install
find_package(KaraokeScorer REQUIRED)

add_executable(my_app src/main.cpp)
target_link_libraries(my_app PRIVATE KaraokeScorer::KaraokeScorer)
```

3. **Khi build project của bạn:**
```bash
cmake .. -DKaraokeScorer_DIR=/path/to/install/lib/cmake/KaraokeScorer
cmake --build .
```

**Ưu điểm:**
- ✅ Sạch sẽ, không cần clone code
- ✅ Có thể version control
- ✅ Giống như các thư viện khác (Boost, OpenCV, etc.)

**Nhược điểm:**
- ❌ Cần build và install trước
- ❌ Phức tạp hơn một chút

---

### Cách 3: Copy Header và Source (Đơn giản nhất)

**Khi nào dùng:** Khi bạn chỉ cần vài file và muốn đơn giản

**Cách làm:**

1. **Copy các file cần thiết vào project:**
```
MyProject/
├── CMakeLists.txt
├── include/
│   └── KaraokeScorer.h
├── src/
│   ├── main.cpp
│   └── KaraokeScorer.cpp
└── python/              # Copy các file Python
    ├── library_interface.py
    ├── pitch_extractor.py
    └── pitch_matcher.py
```

2. **Trong CMakeLists.txt:**
```cmake
cmake_minimum_required(VERSION 3.10)
project(MyProject)

# Tìm Python
find_package(Python3 REQUIRED COMPONENTS Development)

# Tạo library từ source
add_library(KaraokeScorer STATIC
    src/KaraokeScorer.cpp
)

target_include_directories(KaraokeScorer PUBLIC include)
target_link_libraries(KaraokeScorer PUBLIC ${Python3_LIBRARIES})
target_include_directories(KaraokeScorer PUBLIC ${Python3_INCLUDE_DIRS})

# Executable của bạn
add_executable(my_app src/main.cpp)
target_link_libraries(my_app PRIVATE KaraokeScorer)
```

**Ưu điểm:**
- ✅ Đơn giản nhất
- ✅ Không cần clone toàn bộ
- ✅ Dễ customize

**Nhược điểm:**
- ❌ Phải tự quản lý dependencies
- ❌ Không tự động update

---

## 📋 Checklist Khi Tích Hợp

### 1. Python Dependencies
- [ ] Đã cài đặt Python
- [ ] Đã cài đặt các package: `crepe librosa numpy scipy fastdtw mido`
- [ ] Python có trong PATH

### 2. File Python
- [ ] Các file Python (`library_interface.py`, `pitch_extractor.py`, `pitch_matcher.py`) có trong PYTHONPATH
- [ ] Hoặc cùng thư mục với executable
- [ ] Hoặc được copy vào đúng vị trí

### 3. CMake Configuration
- [ ] CMake tìm thấy Python
- [ ] Link đúng với Python libraries
- [ ] Include directories được set đúng

### 4. Runtime
- [ ] Python runtime có sẵn khi chạy
- [ ] Các file Python có thể được import

---

## 🔧 Troubleshooting

### Lỗi: "Cannot find KaraokeScorer"
```bash
# Kiểm tra CMakeLists.txt có add_subdirectory đúng không
# Hoặc set KaraokeScorer_DIR khi chạy cmake
cmake .. -DKaraokeScorer_DIR=/path/to/KaraokeScorer
```

### Lỗi: "Failed to import library_interface module"
- Đảm bảo các file Python trong PYTHONPATH
- Hoặc copy vào cùng thư mục với executable
- Kiểm tra Python version tương thích

### Lỗi: "Python interpreter not initialized"
- Kiểm tra Python đã được cài đặt
- Kiểm tra CMake tìm thấy Python
- Kiểm tra link libraries đúng

---

## 📝 Ví Dụ Đầy Đủ

Xem thư mục `example_external_project/` để xem ví dụ đầy đủ về cách tích hợp.

---

## 🎯 Khuyến Nghị

- **Development/Testing:** Dùng Cách 1 (add_subdirectory)
- **Production:** Dùng Cách 2 (find_package)
- **Quick Prototype:** Dùng Cách 3 (copy files)
