#include "KaraokeScorer.h"
#include <Python.h>
#include <sstream>
#include <iostream>
#include <cmath>

// Simple JSON parser (basic implementation)
// For production, consider using a proper JSON library like nlohmann/json
std::map<std::string, double> parseSimpleJson(const std::string& json_str) {
    std::map<std::string, double> result;
    
    // Very basic JSON parsing - chỉ parse số và string đơn giản
    // Trong production nên dùng thư viện JSON chuyên nghiệp
    size_t pos = 0;
    std::string key, value_str;
    bool in_string = false;
    bool in_key = false;
    bool in_value = false;
    
    // Tìm các cặp key:value
    for (size_t i = 0; i < json_str.length(); i++) {
        char c = json_str[i];
        
        if (c == '"' && (i == 0 || json_str[i-1] != '\\')) {
            in_string = !in_string;
            if (!in_string && in_key) {
                in_key = false;
                in_value = true;
            } else if (in_string && !in_key && !in_value) {
                in_key = true;
                key.clear();
            }
        } else if (in_string) {
            if (in_key) {
                key += c;
            }
        } else if (c == ':' && !in_string) {
            in_value = true;
            value_str.clear();
        } else if ((c == ',' || c == '}') && in_value) {
            // Parse value
            if (!key.empty() && !value_str.empty()) {
                try {
                    double value = std::stod(value_str);
                    result[key] = value;
                } catch (...) {
                    // Nếu không parse được số, bỏ qua
                }
            }
            key.clear();
            value_str.clear();
            in_value = false;
        } else if (in_value && (std::isdigit(c) || c == '.' || c == '-' || c == 'e' || c == 'E')) {
            value_str += c;
        }
    }
    
    return result;
}

KaraokeScorer::KaraokeScorer() : initialized(false), lastError("") {
    // Khởi tạo Python interpreter với error handling
    try {
        if (!Py_IsInitialized()) {
            // Đảm bảo Python path được set trước khi initialize
            Py_SetProgramName(L"KaraokeScorer");
            Py_Initialize();
        }
        
        if (Py_IsInitialized()) {
            initialized = true;
            
            // Thêm thư mục hiện tại vào Python path
            PyObject* sysPath = PySys_GetObject("path");
            if (sysPath) {
                PyObject* currentDir = PyUnicode_FromString(".");
                if (currentDir) {
                    PyList_Append(sysPath, currentDir);
                    Py_DECREF(currentDir);
                }
            }
        } else {
            lastError = "Không thể khởi tạo Python interpreter - Py_Initialize() failed";
        }
    } catch (...) {
        lastError = "Exception khi khởi tạo Python interpreter";
        initialized = false;
    }
}

KaraokeScorer::~KaraokeScorer() {
    // Không finalize Python ở đây vì có thể có nhiều instance
    // Nên để caller quyết định khi nào finalize
}

bool KaraokeScorer::isInitialized() const {
    return initialized && Py_IsInitialized();
}

std::string KaraokeScorer::getLastError() const {
    return lastError;
}

std::string KaraokeScorer::callPythonFunction(
    const std::string& user_audio_path,
    const std::string& reference_path,
    const std::string& method,
    double tolerance_cents,
    const std::string& difficulty_mode) {
    
    if (!isInitialized()) {
        return "{\"error\": \"Python interpreter not initialized\"}";
    }
    
    // Import module
    PyObject* pModule = PyImport_ImportModule("library_interface");
    if (!pModule) {
        PyErr_Print();
        lastError = "Failed to import library_interface module";
        return "{\"error\": \"" + lastError + "\"}";
    }
    
    // Get function
    PyObject* pFunc = PyObject_GetAttrString(pModule, "score_karaoke_and_get_json");
    if (!pFunc || !PyCallable_Check(pFunc)) {
        Py_XDECREF(pFunc);
        Py_DECREF(pModule);
        PyErr_Print();
        lastError = "Function score_karaoke_and_get_json not found";
        return "{\"error\": \"" + lastError + "\"}";
    }
    
    // Prepare arguments
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
    
    // Call function
    PyObject* pResult = PyObject_CallObject(pFunc, pArgs);
    Py_DECREF(pArgs);
    Py_DECREF(pFunc);
    Py_DECREF(pModule);
    
    if (!pResult) {
        PyErr_Print();
        lastError = "Python function call failed";
        return "{\"error\": \"" + lastError + "\"}";
    }
    
    // Convert to string
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

std::string KaraokeScorer::scoreAsJson(
    const std::string& user_audio_path,
    const std::string& reference_path,
    const std::string& method,
    double tolerance_cents,
    const std::string& difficulty_mode) {
    
    return callPythonFunction(user_audio_path, reference_path, method, tolerance_cents, difficulty_mode);
}

std::map<std::string, double> KaraokeScorer::score(
    const std::string& user_audio_path,
    const std::string& reference_path,
    const std::string& method,
    double tolerance_cents,
    const std::string& difficulty_mode) {
    
    std::string json_result = callPythonFunction(user_audio_path, reference_path, method, tolerance_cents, difficulty_mode);
    return parseSimpleJson(json_result);
}

std::map<std::string, double> KaraokeScorer::parseJsonResult(const std::string& json_str) {
    return parseSimpleJson(json_str);
}
