// Ví dụ: Sử dụng KaraokeScorer library trong project C++ bên ngoài
#include "KaraokeScorer.h"
#include <iostream>

int main() {
    std::cout << "=== Sử dụng KaraokeScorer Library ===" << std::endl;
    
    // Khởi tạo scorer
    KaraokeScorer scorer;
    
    if (!scorer.isInitialized()) {
        std::cerr << "❌ Lỗi: " << scorer.getLastError() << std::endl;
        return 1;
    }
    
    std::cout << "✅ Library đã được khởi tạo thành công!" << std::endl;
    
    // Sử dụng library
    auto result = scorer.score(
        "path/to/user_audio.wav",
        "path/to/reference.wav"
    );
    
    // Xử lý kết quả
    if (result.find("error") != result.end()) {
        std::cerr << "❌ Lỗi: " << result["error"] << std::endl;
    } else {
        std::cout << "\n📊 Kết quả chấm điểm:" << std::endl;
        std::cout << "  Điểm tổng hợp: " << result["final_score"] << "/100" << std::endl;
        std::cout << "  Độ chính xác: " << result["accuracy"] << "%" << std::endl;
        std::cout << "  Điểm DTW: " << result["dtw_score"] << "/100" << std::endl;
    }
    
    return 0;
}
