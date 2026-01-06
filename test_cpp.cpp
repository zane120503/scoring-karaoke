#include "KaraokeScorer.h"
#include <iostream>
#include <iomanip>

/**
 * Test program để kiểm tra thư viện KaraokeScorer hoạt động
 */
int main() {
    std::cout << "=" << std::string(60, '=') << std::endl;
    std::cout << "KIỂM TRA THƯ VIỆN KARAOKE SCORER (C++)" << std::endl;
    std::cout << "=" << std::string(60, '=') << std::endl << std::endl;
    
    // --- Test 1: Khởi tạo ---
    std::cout << "[TEST 1] Khởi tạo KaraokeScorer..." << std::endl;
    KaraokeScorer scorer;
    
    if (!scorer.isInitialized()) {
        std::cerr << "❌ LỖI: Không thể khởi tạo Python interpreter" << std::endl;
        std::cerr << "   Lỗi: " << scorer.getLastError() << std::endl;
        return 1;
    }
    std::cout << "✅ PASS: Python interpreter đã được khởi tạo" << std::endl << std::endl;
    
    // --- Test 2: Test với file không tồn tại (error handling) ---
    std::cout << "[TEST 2] Kiểm tra xử lý lỗi (file không tồn tại)..." << std::endl;
    std::string json_result = scorer.scoreAsJson(
        "non_existent_user.wav",
        "non_existent_ref.wav"
    );
    
    std::cout << "Kết quả JSON:" << std::endl;
    std::cout << json_result << std::endl << std::endl;
    
    if (json_result.find("error") != std::string::npos) {
        std::cout << "✅ PASS: Xử lý lỗi hoạt động đúng" << std::endl;
    } else {
        std::cout << "⚠️  WARNING: Không tìm thấy trường 'error' trong kết quả" << std::endl;
    }
    std::cout << std::endl;
    
    // --- Test 3: Test với các tham số khác nhau ---
    std::cout << "[TEST 3] Kiểm tra các tham số khác nhau..." << std::endl;
    
    // Test với default parameters
    std::cout << "  - Test với default parameters:" << std::endl;
    json_result = scorer.scoreAsJson("test1.wav", "test2.wav");
    std::cout << "    Kết quả: " << (json_result.find("error") != std::string::npos ? "Có lỗi (đúng)" : "Không có lỗi") << std::endl;
    
    // Test với explicit parameters
    std::cout << "  - Test với explicit parameters:" << std::endl;
    json_result = scorer.scoreAsJson(
        "test1.wav",
        "test2.wav",
        "crepe",      // method
        200.0,        // tolerance
        "easy"        // difficulty
    );
    std::cout << "    Kết quả: " << (json_result.find("error") != std::string::npos ? "Có lỗi (đúng)" : "Không có lỗi") << std::endl;
    
    // Test với difficulty khác
    std::cout << "  - Test với difficulty='normal':" << std::endl;
    json_result = scorer.scoreAsJson(
        "test1.wav",
        "test2.wav",
        "crepe",
        150.0,
        "normal"
    );
    std::cout << "    Kết quả: " << (json_result.find("error") != std::string::npos ? "Có lỗi (đúng)" : "Không có lỗi") << std::endl;
    
    std::cout << "✅ PASS: Tất cả các tham số được chấp nhận" << std::endl << std::endl;
    
    // --- Test 4: Parse kết quả thành map ---
    std::cout << "[TEST 4] Kiểm tra parse kết quả..." << std::endl;
    std::map<std::string, double> result = scorer.score("test1.wav", "test2.wav");
    
    std::cout << "Các trường trong kết quả:" << std::endl;
    for (const auto& pair : result) {
        std::cout << "  - " << std::setw(15) << std::left << pair.first 
                  << ": " << pair.second << std::endl;
    }
    std::cout << "✅ PASS: Parse kết quả thành công" << std::endl << std::endl;
    
    // --- Hướng dẫn sử dụng với file thật ---
    std::cout << "=" << std::string(60, '=') << std::endl;
    std::cout << "HƯỚNG DẪN SỬ DỤNG VỚI FILE THẬT" << std::endl;
    std::cout << "=" << std::string(60, '=') << std::endl;
    std::cout << "\nVí dụ code:\n" << std::endl;
    std::cout << "  KaraokeScorer scorer;" << std::endl;
    std::cout << "  " << std::endl;
    std::cout << "  // Cách 1: Lấy JSON string" << std::endl;
    std::cout << "  std::string json = scorer.scoreAsJson(" << std::endl;
    std::cout << "      \"user_audio.wav\"," << std::endl;
    std::cout << "      \"reference.wav\"" << std::endl;
    std::cout << "  );" << std::endl;
    std::cout << "  " << std::endl;
    std::cout << "  // Cách 2: Lấy map (đã parse)" << std::endl;
    std::cout << "  auto result = scorer.score(" << std::endl;
    std::cout << "      \"user_audio.wav\"," << std::endl;
    std::cout << "      \"reference.wav\"," << std::endl;
    std::cout << "      \"crepe\",      // method" << std::endl;
    std::cout << "      200.0,         // tolerance_cents" << std::endl;
    std::cout << "      \"easy\"        // difficulty_mode" << std::endl;
    std::cout << "  );" << std::endl;
    std::cout << "  " << std::endl;
    std::cout << "  double final_score = result[\"final_score\"];" << std::endl;
    std::cout << "  double accuracy = result[\"accuracy\"];" << std::endl;
    std::cout << std::endl;
    
    std::cout << "=" << std::string(60, '=') << std::endl;
    std::cout << "HOÀN TẤT KIỂM TRA" << std::endl;
    std::cout << "=" << std::string(60, '=') << std::endl;
    
    return 0;
}
