# 📦 Hướng Dẫn Cài Đặt và Sử Dụng Thư Viện Karaoke Scorer

Hướng dẫn chi tiết để clone, build và sử dụng thư viện Karaoke Scorer (hỗ trợ cả Python và C++).

---

## 📋 Mục Lục

1. [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
2. [Clone Repository](#clone-repository)
3. [Cài Đặt Python Dependencies](#cài-đặt-python-dependencies)
4. [Build Thư Viện C++](#build-thư-viện-c)
5. [Sử Dụng Thư Viện Python](#sử-dụng-thư-viện-python)
6. [Sử Dụng Thư Viện C++](#sử-dụng-thư-viện-c)
7. [Troubleshooting](#troubleshooting)

---

## 🖥️ Yêu Cầu Hệ Thống

### Yêu Cầu Chung
- **Python 3.8+** (khuyến nghị Python 3.10 hoặc 3.11)
- **Git** (để clone repository)
- **CMake 3.10+** (nếu muốn build C++ library)
- **C++ Compiler** (nếu muốn build C++ library):
  - Windows: Visual Studio 2019+ hoặc Build Tools
  - Linux: GCC 7+ hoặc Clang 8+
  - macOS: Xcode Command Line Tools

### Yêu Cầu Cho Python Library
- Python 3.8+
- pip (package manager)

### Yêu Cầu Cho C++ Library
- CMake 3.10+
- C++ Compiler hỗ trợ C++11
- Python development headers và libraries (tự động tìm bởi CMake)

---

## 📥 Clone Repository

### Bước 1: Clone Repository

```bash
git clone <repository-url>
cd "scoring karaoke"
```

**Lưu ý:** Nếu repository nằm trong thư mục có khoảng trắng (như "scoring karaoke"), nhớ dùng dấu ngoặc kép khi cd.

### Bước 2: Kiểm Tra Cấu Trúc

Sau khi clone, bạn sẽ thấy các file/folder sau:

```
scoring karaoke/
├── README.md                    # Tài liệu tổng quan
├── INSTALLATION_GUIDE.md        # File này
├── requirements.txt             # Python dependencies
├── CMakeLists.txt              # CMake config cho C++
├── CMakeLists_library.txt      # CMake config cho library
├── KaraokeScorer.h              # Header file C++
├── KaraokeScorer.cpp            # Source file C++
├── library_interface.py         # Python interface
├── pitch_extractor.py           # Pitch extraction
├── pitch_matcher.py             # Pitch matching
├── gui.py                       # GUI application
└── ... (các file khác)
```

---

## 🐍 Cài Đặt Python Dependencies

### Bước 1: Tạo Virtual Environment (Khuyến nghị)

**Windows:**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Bước 2: Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

**Lưu ý quan trọng:**
- CREPE yêu cầu TensorFlow (sẽ tự động cài khi cài `crepe`)
- **Basic Pitch không được khuyến nghị** với Python 3.12+ vì yêu cầu TensorFlow < 2.15.1
- Nếu bạn thực sự cần Basic Pitch, hãy dùng Python 3.10 hoặc 3.11

### Bước 3: Kiểm Tra Cài Đặt

```bash
python -c "import crepe; import librosa; import numpy; print('✅ Dependencies đã cài đặt thành công!')"
```

---

## 🔨 Build Thư Viện C++

### Bước 1: Tạo Thư Mục Build

**Windows (PowerShell):**
```powershell
mkdir build
cd build
```

**Linux/macOS:**
```bash
mkdir build && cd build
```

### Bước 2: Chạy CMake

**Windows:**
```powershell
cmake ..
```

Nếu CMake không tìm thấy Python, chỉ định đường dẫn:
```powershell
cmake .. -DPython3_EXECUTABLE=C:/Python39/python.exe
```

**Linux/macOS:**
```bash
cmake ..
```

### Bước 3: Build Library

**Windows:**
```powershell
cmake --build . --config Release
```

**Linux/macOS:**
```bash
cmake --build . --config Release
# hoặc
make
```

### Bước 4: Kiểm Tra Kết Quả

Sau khi build thành công, bạn sẽ thấy các file sau trong `build/Release/` (Windows) hoặc `build/` (Linux/macOS):

- ✅ `KaraokeScorer.lib` (Windows) hoặc `libKaraokeScorer.a` (Linux/macOS) - **Thư viện C++**
- ✅ `scorer_client.exe` (Windows) hoặc `scorer_client` (Linux/macOS) - Executable ví dụ
- ✅ `test_cpp.exe` (Windows) hoặc `test_cpp` (Linux/macOS) - Executable test

---

## 🐍 Sử Dụng Thư Viện Python

### Cách 1: Sử Dụng GUI (Khuyến nghị cho người mới)

**Windows:**
```powershell
python gui.py
# hoặc double-click: run_gui.bat
```

**Linux/macOS:**
```bash
python3 gui.py
# hoặc
chmod +x run_gui.sh && ./run_gui.sh
```

### Cách 2: Sử Dụng Command Line

```bash
python karaoke_scorer.py --user user_audio.wav --reference reference.wav
```

### Cách 3: Sử Dụng Trong Python Code

Xem file `example_usage.py` để biết các ví dụ chi tiết.

**Ví dụ cơ bản:**
```python
from library_interface import score_karaoke_and_get_json
import json

# Chấm điểm
result_json = score_karaoke_and_get_json(
    "user_audio.wav",
    "reference.wav",
    method='crepe',
    tolerance_cents=200.0,
    difficulty_mode='easy'
)

# Parse kết quả
result = json.loads(result_json)
print(f"Điểm: {result['final_score']:.2f}/100")
```

---

## 🔧 Sử Dụng Thư Viện C++

### Cách 1: Sử Dụng Trong Project C++ Của Bạn

#### Option A: Add Subdirectory (Khuyến nghị cho development)

**1. Copy hoặc clone thư mục vào project của bạn:**
```
MyProject/
├── CMakeLists.txt
├── src/
│   └── main.cpp
└── external/
    └── scoring-karaoke/    # Clone vào đây
```

**2. Trong CMakeLists.txt của bạn:**
```cmake
cmake_minimum_required(VERSION 3.10)
project(MyProject)

# Add thư viện
add_subdirectory(external/scoring-karaoke)

# Tạo executable
add_executable(my_app src/main.cpp)

# Link với thư viện
target_link_libraries(my_app PRIVATE KaraokeScorer)
```

**3. Trong code C++:**
```cpp
#include "KaraokeScorer.h"
#include <iostream>

int main() {
    KaraokeScorer scorer;
    
    auto result = scorer.score(
        "user_audio.wav",
        "reference.wav"
    );
    
    std::cout << "Điểm: " << result["final_score"] << std::endl;
    return 0;
}
```

#### Option B: Link Với File .lib Đã Build

```cmake
# Link với library đã build
target_link_libraries(your_app PRIVATE 
    "D:/scoring karaoke/build/Release/KaraokeScorer.lib"
)

# Include headers
target_include_directories(your_app PRIVATE 
    "D:/scoring karaoke"
)
```

### Cách 2: Sử Dụng Executable Đã Build

**Windows:**
```powershell
cd build\Release
.\scorer_client.exe
```

**Linux/macOS:**
```bash
cd build
./scorer_client
```

**Lưu ý:** Cần chỉnh sửa đường dẫn file audio trong `main.cpp` trước khi build.

### Ví Dụ Code C++ Đầy Đủ

```cpp
#include "KaraokeScorer.h"
#include <iostream>
#include <iomanip>

int main() {
    // Khởi tạo scorer
    KaraokeScorer scorer;
    
    if (!scorer.isInitialized()) {
        std::cerr << "❌ Không thể khởi tạo Python interpreter!" << std::endl;
        std::cerr << "Lỗi: " << scorer.getLastError() << std::endl;
        return 1;
    }
    
    // Chấm điểm với default settings
    std::cout << "Đang chấm điểm..." << std::endl;
    auto result = scorer.score(
        "C:/path/to/user_audio.wav",
        "C:/path/to/reference.wav"
    );
    
    // Kiểm tra lỗi
    if (result.find("error") != result.end()) {
        std::cerr << "❌ Lỗi: " << result["error"] << std::endl;
        return 1;
    }
    
    // Hiển thị kết quả
    std::cout << "\n📊 KẾT QUẢ CHẤM ĐIỂM" << std::endl;
    std::cout << "=" << std::setfill('=') << std::setw(50) << "" << std::endl;
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Điểm tổng hợp:  " << result["final_score"] << " / 100" << std::endl;
    std::cout << "Độ chính xác:  " << result["accuracy"] << "%" << std::endl;
    std::cout << "Điểm DTW:       " << result["dtw_score"] << " / 100" << std::endl;
    std::cout << "Khoảng cách DTW: " << result["dtw_distance"] << std::endl;
    std::cout << "Độ lệch TB:     " << result["mae_cents"] << " cents" << std::endl;
    std::cout << "Thời lượng:     " << result["duration"] << " giây" << std::endl;
    
    return 0;
}
```

---

## ⚠️ Lưu Ý Quan Trọng Khi Sử Dụng C++ Library

### 1. Python Runtime Phải Có Sẵn

Thư viện C++ này là wrapper gọi Python, nên khi chạy chương trình C++:

- ✅ Python phải được cài đặt trên hệ thống
- ✅ Các file Python (`library_interface.py`, `pitch_extractor.py`, `pitch_matcher.py`) phải có trong:
  - PYTHONPATH, hoặc
  - Cùng thư mục với executable, hoặc
  - Được copy vào đúng vị trí

### 2. Python Dependencies Phải Được Cài Đặt

Đảm bảo đã cài đặt tất cả dependencies từ `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 3. Set PYTHONPATH (Nếu Cần)

**Windows:**
```powershell
$env:PYTHONPATH = "D:\scoring karaoke"
```

**Linux/macOS:**
```bash
export PYTHONPATH=/path/to/scoring-karaoke
```

---

## 🔍 Troubleshooting

### Lỗi: "ModuleNotFoundError: No module named 'numpy'"

**Giải pháp:**
```bash
pip install -r requirements.txt
```

### Lỗi: "CMake không tìm thấy Python"

**Giải pháp:**
Chỉ định đường dẫn Python khi chạy CMake:
```bash
cmake .. -DPython3_EXECUTABLE=C:/Python39/python.exe
```

### Lỗi: "Failed to import library_interface module"

**Giải pháp:**
- Đảm bảo các file Python trong PYTHONPATH
- Hoặc copy các file Python vào cùng thư mục với executable
- Kiểm tra Python version tương thích

### Lỗi: "Python interpreter not initialized"

**Giải pháp:**
- Kiểm tra Python đã được cài đặt
- Kiểm tra CMake tìm thấy Python (xem output khi chạy `cmake ..`)
- Kiểm tra link libraries đúng

### Lỗi Build: "Cannot find Python.h"

**Giải pháp:**
- Cài đặt Python development headers:
  - Windows: Đảm bảo đã cài Python với "Development headers" option
  - Linux: `sudo apt-get install python3-dev` (Ubuntu/Debian)
  - macOS: Thường đã có sẵn với Xcode

### Lỗi Runtime: "DLL load failed" (Windows)

**Giải pháp:**
- Đảm bảo Python DLLs trong PATH
- Hoặc copy Python DLLs vào cùng thư mục với executable

---

## 📚 Tài Liệu Tham Khảo

- **README.md** - Tổng quan về project
- **QUICK_START.md** - Hướng dẫn nhanh
- **USAGE_GUIDE.md** - Hướng dẫn sử dụng chi tiết
- **INTEGRATION_GUIDE.md** - Hướng dẫn tích hợp vào project C++
- **INPUT_REQUIREMENTS.md** - Yêu cầu về input files
- **BUILD_INSTRUCTIONS.md** - Hướng dẫn build chi tiết

---

## ✅ Checklist Sau Khi Cài Đặt

Sau khi cài đặt, hãy kiểm tra:

- [ ] Python dependencies đã được cài đặt (`pip list` để kiểm tra)
- [ ] Có thể import các module Python (`python -c "import crepe; import librosa"`)
- [ ] CMake tìm thấy Python (xem output khi chạy `cmake ..`)
- [ ] Build thành công (có file `.lib` hoặc `.a` trong thư mục build)
- [ ] Các file Python có trong PYTHONPATH hoặc cùng thư mục với executable

---

## 🎯 Bước Tiếp Theo

Sau khi cài đặt thành công:

1. **Test Python library:** Chạy `python test_with_real_audio.py`
2. **Test C++ library:** Chạy executable `test_cpp` đã build
3. **Xem ví dụ:** Đọc `example_usage.py` và `test_cpp.cpp`
4. **Sử dụng trong project:** Tham khảo `INTEGRATION_GUIDE.md`

---

## 💬 Hỗ Trợ

Nếu gặp vấn đề, hãy:
1. Kiểm tra lại các bước trong hướng dẫn này
2. Xem phần Troubleshooting
3. Kiểm tra các file tài liệu khác trong project
4. Tạo issue trên repository (nếu có)

---

**Chúc bạn sử dụng thư viện thành công! 🎤🎵**
