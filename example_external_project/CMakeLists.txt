# Ví dụ: Project C++ bên ngoài sử dụng KaraokeScorer library
cmake_minimum_required(VERSION 3.10)

project(MyKaraokeApp)

set(CMAKE_CXX_STANDARD 11)

# --- Cách 1: Sử dụng add_subdirectory (Clone về và add vào project) ---
# Giả sử bạn đã clone KaraokeScorer vào thư mục con
add_subdirectory(../.. KaraokeScorer)

# --- Cách 2: Sử dụng find_package (Nếu đã install library) ---
# find_package(KaraokeScorer REQUIRED)

# --- Tạo executable của bạn ---
add_executable(my_app main.cpp)

# --- Link với KaraokeScorer library ---
target_link_libraries(my_app
    PRIVATE
        KaraokeScorer::KaraokeScorer  # Nếu dùng namespace
        # Hoặc: KaraokeScorer  # Nếu không dùng namespace
)

# Include directories sẽ tự động được thêm vào nhờ PUBLIC trong KaraokeScorer
