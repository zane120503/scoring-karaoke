#include <iostream>
#include <string>
#include <memory>
#include <Python.h>

// Helper function to call Python function and get JSON result
std::string call_python_scorer(const std::string& user_audio_path, 
                                const std::string& reference_path,
                                const std::string& method = "crepe",
                                double tolerance_cents = 200.0,
                                const std::string& difficulty_mode = "easy") {
    // Import the library_interface module
    PyObject* pModule = PyImport_ImportModule("library_interface");
    if (!pModule) {
        PyErr_Print();
        return "{\"error\": \"Failed to import library_interface module\"}";
    }

    // Get the function
    PyObject* pFunc = PyObject_GetAttrString(pModule, "score_karaoke_and_get_json");
    if (!pFunc || !PyCallable_Check(pFunc)) {
        Py_XDECREF(pFunc);
        Py_DECREF(pModule);
        PyErr_Print();
        return "{\"error\": \"Function score_karaoke_and_get_json not found or not callable\"}";
    }

    // Prepare arguments (5 parameters: user_audio_path, reference_path, method, tolerance_cents, difficulty_mode)
    PyObject* pArgs = PyTuple_New(5);
    PyObject* pUserPath = PyUnicode_FromString(user_audio_path.c_str());
    PyObject* pRefPath = PyUnicode_FromString(reference_path.c_str());
    PyObject* pMethod = PyUnicode_FromString(method.c_str());
    PyObject* pTolerance = PyFloat_FromDouble(tolerance_cents);
    PyObject* pDifficulty = PyUnicode_FromString(difficulty_mode.c_str());

    PyTuple_SetItem(pArgs, 0, pUserPath);
    PyTuple_SetItem(pArgs, 1, pRefPath);
    PyTuple_SetItem(pArgs, 2, pMethod);
    PyTuple_SetItem(pArgs, 3, pTolerance);
    PyTuple_SetItem(pArgs, 4, pDifficulty);

    // Call the function
    PyObject* pResult = PyObject_CallObject(pFunc, pArgs);
    Py_DECREF(pArgs);
    Py_DECREF(pFunc);
    Py_DECREF(pModule);

    if (!pResult) {
        PyErr_Print();
        return "{\"error\": \"Python function call failed\"}";
    }

    // Convert result to C++ string
    std::string result;
    if (PyUnicode_Check(pResult)) {
        PyObject* pBytes = PyUnicode_AsUTF8String(pResult);
        if (pBytes) {
            result = std::string(PyBytes_AsString(pBytes));
            Py_DECREF(pBytes);
        }
    } else if (PyBytes_Check(pResult)) {
        result = std::string(PyBytes_AsString(pResult));
    } else {
        // Try to convert to string
        PyObject* pStr = PyObject_Str(pResult);
        if (pStr) {
            PyObject* pBytes = PyUnicode_AsUTF8String(pStr);
            if (pBytes) {
                result = std::string(PyBytes_AsString(pBytes));
                Py_DECREF(pBytes);
            }
            Py_DECREF(pStr);
        }
    }

    Py_DECREF(pResult);
    return result;
}

void run_karaoke_scoring() {
    // --- 1. Initialize Python interpreter ---
    if (!Py_IsInitialized()) {
        Py_Initialize();
    }
    
    if (!Py_IsInitialized()) {
        std::cerr << "❌ Lỗi: Không thể khởi tạo Python interpreter" << std::endl;
        return;
    }

    // Add current directory to Python path so it can find library_interface.py
    PyObject* sysPath = PySys_GetObject("path");
    if (sysPath) {
        PyObject* currentDir = PyUnicode_FromString(".");
        if (currentDir) {
            PyList_Append(sysPath, currentDir);
            Py_DECREF(currentDir);
        }
    }

    // --- 2. Prepare arguments ---
    // IMPORTANT: Replace these with actual file paths
    std::string user_audio = "path/to/your/user_audio.wav";
    std::string ref_audio = "path/to/your/singer_audio.wav";
    std::string method = "crepe";
    double tolerance = 200.0;  // Default: 200.0 (easy mode - matches library_interface.py)
    std::string difficulty_mode = "easy";  // Options: "easy", "normal", "hard"

    std::cout << "Calling Python karaoke scorer..." << std::endl;
    std::cout << "  User file: " << user_audio << std::endl;
    std::cout << "  Ref file: " << ref_audio << std::endl;
    std::cout << "  Method: " << method << std::endl;
    std::cout << "  Tolerance: " << tolerance << " cents" << std::endl;
    std::cout << "  Difficulty: " << difficulty_mode << std::endl;

    // --- 3. Call the Python function ---
    std::string json_result = call_python_scorer(user_audio, ref_audio, method, tolerance, difficulty_mode);

    std::cout << "\nReceived JSON result from Python:" << std::endl;
    std::cout << json_result << std::endl;

    // --- 4. Finalize Python interpreter ---
    Py_Finalize();
}

int main() {
    // HƯỚNG DẪN SỬ DỤNG:
    // 1. Đảm bảo Python đã được cài đặt và có thể tìm thấy trong PATH
    // 2. Cài đặt các thư viện Python cần thiết:
    //    pip install crepe librosa numpy scipy fastdtw mido
    // 3. Đảm bảo file library_interface.py, pitch_extractor.py, pitch_matcher.py
    //    nằm trong cùng thư mục với executable hoặc trong PYTHONPATH
    // 4. Cập nhật đường dẫn file audio trong hàm run_karaoke_scoring()
    // 5. Biên dịch với CMake (xem CMakeLists.txt)
    
    run_karaoke_scoring();

    return 0;
}
