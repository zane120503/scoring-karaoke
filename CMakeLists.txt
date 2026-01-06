
# CMake minimum version
cmake_minimum_required(VERSION 3.10)

# Project Name - Có thể được dùng như library hoặc standalone
project(KaraokeScorer VERSION 1.0.0 LANGUAGES CXX)

# C++ Standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# --- Find Python ---
# This is crucial for embedding Python interpreter in C++
# Try to find Python 3 first, then fall back to Python
find_package(Python3 COMPONENTS Interpreter Development QUIET)
if(Python3_FOUND)
    set(PYTHON_INCLUDE_DIRS ${Python3_INCLUDE_DIRS})
    set(PYTHON_LIBRARIES ${Python3_LIBRARIES})
    message(STATUS "Found Python3: ${Python3_EXECUTABLE}")
    message(STATUS "Python3 Include: ${Python3_INCLUDE_DIRS}")
    message(STATUS "Python3 Libraries: ${Python3_LIBRARIES}")
else()
    # Fallback to old PythonLibs
    find_package(PythonLibs REQUIRED)
    set(PYTHON_INCLUDE_DIRS ${PYTHON_INCLUDE_DIRS})
    set(PYTHON_LIBRARIES ${PYTHON_LIBRARIES})
    message(STATUS "Found Python (legacy): ${PYTHON_INCLUDE_DIRS}")
endif()

# ============================================================================
# TẠO LIBRARY TARGET - Có thể được sử dụng bởi project khác
# ============================================================================
add_library(KaraokeScorer STATIC
    KaraokeScorer.cpp
)

# Public include - các project khác sẽ tự động có access
target_include_directories(KaraokeScorer
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}  # Để include KaraokeScorer.h
        ${PYTHON_INCLUDE_DIRS}
)

# Link Python libraries
target_link_libraries(KaraokeScorer
    PUBLIC
        ${PYTHON_LIBRARIES}
)

# ============================================================================
# EXECUTABLES - Ví dụ sử dụng library
# ============================================================================
add_executable(scorer_client main.cpp)
add_executable(test_cpp test_cpp.cpp)

# Link với library
target_link_libraries(scorer_client PRIVATE KaraokeScorer)
target_link_libraries(test_cpp PRIVATE KaraokeScorer)

# --- Platform-specific settings ---
if (WIN32)
    # On Windows, you might need to handle DLLs
    # This is a placeholder for more complex build scenarios
    message(STATUS "Configuring for Windows")
else()
    # On Linux/macOS, you may need to set RPATH so the executable can find
    # the Python library at runtime.
    # set(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib")
    # set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)
    message(STATUS "Configuring for Linux/macOS")
endif()

# --- Instructions ---
#
# HƯỚNG DẪN BIÊN DỊCH VÀ CHẠY:
#
# 1. Cài đặt Python và các thư viện cần thiết:
#    pip install crepe librosa numpy scipy fastdtw mido
#
# 2. Tạo thư mục build:
#    mkdir build && cd build
#
# 3. Chạy CMake (Windows):
#    cmake .. -DPython3_EXECUTABLE=python
#    Hoặc chỉ định đường dẫn Python cụ thể:
#    cmake .. -DPython3_EXECUTABLE=C:/Python39/python.exe
#
# 4. Biên dịch:
#    cmake --build .
#    Hoặc trên Linux/Mac: make
#
# 5. Chạy chương trình:
#    - Đảm bảo các file Python (library_interface.py, pitch_extractor.py, pitch_matcher.py)
#      nằm trong cùng thư mục với executable hoặc trong PYTHONPATH
#    - Cập nhật đường dẫn file audio trong main.cpp
#    - Chạy: ./scorer_client (Linux/Mac) hoặc scorer_client.exe (Windows)
#
