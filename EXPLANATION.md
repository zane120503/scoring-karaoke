# Giải Thích Cách Thức Hoạt Động Của Thư Viện

## 🎯 Tổng Quan

Thư viện này cho phép C++ gọi code Python để chấm điểm karaoke. C++ sẽ nhúng (embed) Python interpreter và gọi các hàm Python thông qua Python C API.

## 🔄 Luồng Hoạt Động

```
┌─────────────┐
│   C++ Code  │
│  (main.cpp) │
└──────┬──────┘
       │
       │ 1. Khởi tạo Python Interpreter
       ▼
┌─────────────────────┐
│  Python C API       │
│  (Py_Initialize)    │
└──────┬──────────────┘
       │
       │ 2. Import module Python
       ▼
┌─────────────────────┐
│  library_interface.py │
│  (Python Module)      │
└──────┬──────────────┘
       │
       │ 3. Gọi hàm score_karaoke_and_get_json()
       ▼
┌─────────────────────┐
│  pitch_extractor.py │
│  pitch_matcher.py   │
│  (Xử lý audio)      │
└──────┬──────────────┘
       │
       │ 4. Trả về JSON string
       ▼
┌─────────────┐
│   C++ Code  │
│  (Parse &   │
│   Sử dụng)  │
└─────────────┘
```

## 📦 Cấu Trúc Thư Viện

### 1. Python Layer (Backend)

**`library_interface.py`**
- Module chính được C++ gọi
- Hàm `score_karaoke_and_get_json()` nhận 5 tham số:
  - `user_audio_path`: File audio của người hát
  - `reference_path`: File audio/MIDI tham chiếu
  - `method`: "crepe" hoặc "basic_pitch"
  - `tolerance_cents`: Độ lệch cho phép
  - `difficulty_mode`: "easy", "normal", "hard"
- Trả về JSON string chứa kết quả

**`pitch_extractor.py`**
- Trích xuất pitch từ audio/MIDI
- Hỗ trợ CREPE và Basic Pitch
- Trả về mảng thời gian và tần số

**`pitch_matcher.py`**
- So khớp pitch giữa user và reference
- Sử dụng DTW (Dynamic Time Warping)
- Tính điểm dựa trên độ chính xác và khoảng cách

### 2. C++ Layer (Frontend)

**`KaraokeScorer.h` / `KaraokeScorer.cpp`**
- Wrapper class C++ che giấu Python C API
- Cung cấp interface C++ thuận tiện
- Tự động quản lý Python interpreter

**`main.cpp`**
- Ví dụ sử dụng trực tiếp Python C API
- Cho thấy cách gọi Python từ C++

## 🔧 Cách Thức Hoạt Động Chi Tiết

### Bước 1: Khởi Tạo Python Interpreter

```cpp
// Trong KaraokeScorer constructor
Py_Initialize();  // Khởi tạo Python interpreter

// Thêm thư mục hiện tại vào Python path
PyObject* sysPath = PySys_GetObject("path");
PyList_Append(sysPath, currentDir);
```

**Mục đích:**
- Khởi động Python runtime trong C++
- Cho phép C++ import và gọi module Python

### Bước 2: Import Module Python

```cpp
PyObject* pModule = PyImport_ImportModule("library_interface");
```

**Mục đích:**
- Load module `library_interface.py` vào memory
- Có thể gọi các hàm trong module này

### Bước 3: Lấy Function Pointer

```cpp
PyObject* pFunc = PyObject_GetAttrString(pModule, "score_karaoke_and_get_json");
```

**Mục đích:**
- Lấy reference đến hàm Python cần gọi
- Kiểm tra hàm có thể gọi được không

### Bước 4: Chuẩn Bị Arguments

```cpp
PyObject* pArgs = PyTuple_New(5);  // Tạo tuple 5 phần tử
PyTuple_SetItem(pArgs, 0, pUserPath);      // user_audio_path
PyTuple_SetItem(pArgs, 1, pRefPath);       // reference_path
PyTuple_SetItem(pArgs, 2, pMethod);        // method
PyTuple_SetItem(pArgs, 3, pTolerance);     // tolerance_cents
PyTuple_SetItem(pArgs, 4, pDifficulty);     // difficulty_mode
```

**Mục đích:**
- Chuyển đổi tham số C++ sang Python objects
- Tạo tuple chứa các tham số

### Bước 5: Gọi Hàm Python

```cpp
PyObject* pResult = PyObject_CallObject(pFunc, pArgs);
```

**Mục đích:**
- Thực thi hàm Python
- Nhận kết quả trả về

### Bước 6: Chuyển Đổi Kết Quả

```cpp
// Chuyển Python string sang C++ string
PyObject* pBytes = PyUnicode_AsUTF8String(pResult);
std::string result = std::string(PyBytes_AsString(pBytes));
```

**Mục đích:**
- Chuyển đổi Python string sang C++ string
- Có thể parse JSON để lấy các giá trị cụ thể

### Bước 7: Dọn Dẹp Memory

```cpp
Py_DECREF(pResult);  // Giảm reference count
Py_DECREF(pArgs);
Py_DECREF(pFunc);
Py_DECREF(pModule);
```

**Mục đích:**
- Giải phóng memory Python objects
- Tránh memory leak

## 💡 Tại Sao Dùng Python C API?

### Ưu Điểm:
1. **Không cần biên dịch Python code**: Giữ nguyên code Python, chỉ cần có Python runtime
2. **Dễ bảo trì**: Sửa Python code không cần biên dịch lại C++
3. **Tận dụng thư viện Python**: Sử dụng các thư viện ML/Audio processing mạnh mẽ
4. **Linh hoạt**: Có thể thay đổi logic Python mà không cần rebuild C++

### Nhược Điểm:
1. **Cần Python runtime**: Phải có Python cài đặt khi chạy
2. **Performance**: Chậm hơn một chút so với native C++
3. **Phức tạp**: Cần hiểu Python C API

## 🎨 Wrapper Class - Tại Sao Cần?

### Vấn Đề Khi Dùng Trực Tiếp Python C API:

```cpp
// Phức tạp, dễ lỗi
PyObject* pModule = PyImport_ImportModule("library_interface");
PyObject* pFunc = PyObject_GetAttrString(pModule, "score_karaoke_and_get_json");
// ... nhiều code phức tạp ...
Py_DECREF(...);  // Dễ quên, gây memory leak
```

### Giải Pháp - Wrapper Class:

```cpp
// Đơn giản, an toàn
KaraokeScorer scorer;
auto result = scorer.score("user.wav", "ref.wav");
```

**Lợi ích:**
- ✅ Che giấu độ phức tạp của Python C API
- ✅ Tự động quản lý memory
- ✅ Interface C++ thuận tiện
- ✅ Dễ sử dụng và bảo trì

## 🔍 Xử Lý Lỗi

### Trong Python:
```python
try:
    # Xử lý audio
    results = matcher.calculate_score(...)
except Exception as e:
    results = {
        'error': str(e),
        'final_score': 0.0,
        ...
    }
```

### Trong C++:
```cpp
if (!pModule) {
    PyErr_Print();  // In lỗi Python
    return "{\"error\": \"...\"}";
}
```

## 📊 Luồng Dữ Liệu

```
Audio Files
    │
    ▼
[Python: Extract Pitch]
    │
    ▼
Time + Frequency Arrays
    │
    ▼
[Python: Match & Score]
    │
    ▼
JSON String
    │
    ▼
[C++: Parse & Use]
    │
    ▼
C++ Application
```

## 🚀 Tối Ưu Hóa

1. **Reuse Python Interpreter**: Không khởi tạo lại nhiều lần
2. **Cache Module**: Import module một lần, dùng nhiều lần
3. **Batch Processing**: Xử lý nhiều file trong một lần gọi Python

## 📝 Kết Luận

Thư viện này sử dụng **Python C API** để nhúng Python vào C++, cho phép:
- C++ gọi code Python một cách seamless
- Tận dụng thư viện Python mạnh mẽ
- Giữ code Python dễ bảo trì
- Cung cấp interface C++ thuận tiện
