// Ví dụ đầy đủ về cách sử dụng input cho thư viện KaraokeScorer

#include "KaraokeScorer.h"
#include <iostream>
#include <filesystem>
#include <iomanip>

// Hàm kiểm tra file có tồn tại không
bool fileExists(const std::string& path) {
    return std::filesystem::exists(path);
}

// Hàm hiển thị kết quả
void printResult(const std::map<std::string, double>& result) {
    std::cout << "\n" << std::string(50, '=') << std::endl;
    std::cout << "KẾT QUẢ CHẤM ĐIỂM" << std::endl;
    std::cout << std::string(50, '=') << std::endl;
    
    if (result.find("error") != result.end()) {
        std::cerr << "❌ LỖI: " << result.at("error") << std::endl;
        return;
    }
    
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "📊 Điểm tổng hợp:      " << std::setw(8) << result.at("final_score") << " / 100" << std::endl;
    std::cout << "🎯 Độ chính xác:     " << std::setw(8) << result.at("accuracy") << " %" << std::endl;
    std::cout << "📈 Điểm DTW:         " << std::setw(8) << result.at("dtw_score") << " / 100" << std::endl;
    std::cout << "📏 Khoảng cách DTW:  " << std::setw(8) << result.at("dtw_distance") << std::endl;
    std::cout << "📉 Độ lệch TB:       " << std::setw(8) << result.at("mae_cents") << " cents" << std::endl;
    std::cout << "⏱️  Thời lượng:      " << std::setw(8) << result.at("duration") << " giây" << std::endl;
    std::cout << std::string(50, '=') << std::endl;
}

int main() {
    std::cout << "=== VÍ DỤ SỬ DỤNG KARAOKE SCORER ===" << std::endl;
    
    // Khởi tạo scorer
    KaraokeScorer scorer;
    
    if (!scorer.isInitialized()) {
        std::cerr << "❌ Không thể khởi tạo Python interpreter!" << std::endl;
        std::cerr << "   Lỗi: " << scorer.getLastError() << std::endl;
        return 1;
    }
    
    std::cout << "✅ Python interpreter đã được khởi tạo\n" << std::endl;
    
    // ============================================================
    // VÍ DỤ 1: Sử dụng tối thiểu (chỉ 2 file)
    // ============================================================
    std::cout << "\n[VÍ DỤ 1] Input tối thiểu (chỉ 2 file)" << std::endl;
    std::cout << "----------------------------------------" << std::endl;
    
    std::string user_audio = "user_singing.wav";
    std::string ref_audio = "reference_singer.wav";
    
    // Kiểm tra file tồn tại
    if (!fileExists(user_audio) || !fileExists(ref_audio)) {
        std::cout << "⚠️  File không tồn tại. Thay đổi đường dẫn trong code." << std::endl;
        std::cout << "   User audio: " << user_audio << std::endl;
        std::cout << "   Reference:  " << ref_audio << std::endl;
    } else {
        // Gọi với input tối thiểu
        auto result1 = scorer.score(user_audio, ref_audio);
        printResult(result1);
    }
    
    // ============================================================
    // VÍ DỤ 2: Sử dụng với tất cả tham số
    // ============================================================
    std::cout << "\n[VÍ DỤ 2] Input đầy đủ với tất cả tham số" << std::endl;
    std::cout << "----------------------------------------" << std::endl;
    
    auto result2 = scorer.score(
        "user_singing.wav",      // 1. File người hát (BẮT BUỘC)
        "reference.wav",         // 2. File tham chiếu (BẮT BUỘC)
        "crepe",                 // 3. Method: "crepe" hoặc "basic_pitch"
        200.0,                   // 4. Tolerance: 200 cents (dễ)
        "easy"                   // 5. Difficulty: "easy", "normal", "hard"
    );
    
    std::cout << "Tham số đã sử dụng:" << std::endl;
    std::cout << "  - Method: crepe" << std::endl;
    std::cout << "  - Tolerance: 200.0 cents" << std::endl;
    std::cout << "  - Difficulty: easy" << std::endl;
    printResult(result2);
    
    // ============================================================
    // VÍ DỤ 3: Sử dụng MIDI làm reference
    // ============================================================
    std::cout << "\n[VÍ DỤ 3] Sử dụng MIDI làm reference" << std::endl;
    std::cout << "----------------------------------------" << std::endl;
    
    std::string ref_midi = "song_vocal.mid";
    
    if (fileExists(ref_midi)) {
        auto result3 = scorer.score(
            "user_singing.wav",
            ref_midi,            // MIDI file
            "crepe",
            200.0,
            "easy"
        );
        printResult(result3);
    } else {
        std::cout << "⚠️  MIDI file không tồn tại: " << ref_midi << std::endl;
    }
    
    // ============================================================
    // VÍ DỤ 4: Chấm điểm nghiêm ngặt (tolerance thấp)
    // ============================================================
    std::cout << "\n[VÍ DỤ 4] Chấm điểm nghiêm ngặt" << std::endl;
    std::cout << "----------------------------------------" << std::endl;
    
    auto result4 = scorer.score(
        "user_singing.wav",
        "reference.wav",
        "crepe",
        50.0,                    // Tolerance thấp = chấm điểm nghiêm
        "hard"                   // Difficulty cao
    );
    
    std::cout << "Tham số:" << std::endl;
    std::cout << "  - Tolerance: 50.0 cents (nghiêm ngặt)" << std::endl;
    std::cout << "  - Difficulty: hard" << std::endl;
    printResult(result4);
    
    // ============================================================
    // VÍ DỤ 5: So sánh các method khác nhau
    // ============================================================
    std::cout << "\n[VÍ DỤ 5] So sánh các method" << std::endl;
    std::cout << "----------------------------------------" << std::endl;
    
    std::vector<std::string> methods = {"crepe", "basic_pitch"};
    
    for (const auto& method : methods) {
        std::cout << "\nMethod: " << method << std::endl;
        auto result = scorer.score(
            "user_singing.wav",
            "reference.wav",
            method,              // Thử method khác nhau
            200.0,
            "easy"
        );
        
        if (result.find("error") == result.end()) {
            std::cout << "  Điểm: " << result["final_score"] << std::endl;
        } else {
            std::cout << "  ❌ Lỗi: " << result["error"] << std::endl;
        }
    }
    
    // ============================================================
    // VÍ DỤ 6: Lấy JSON string thay vì map
    // ============================================================
    std::cout << "\n[VÍ DỤ 6] Lấy kết quả dạng JSON" << std::endl;
    std::cout << "----------------------------------------" << std::endl;
    
    std::string json_result = scorer.scoreAsJson(
        "user_singing.wav",
        "reference.wav"
    );
    
    std::cout << "JSON Result:" << std::endl;
    std::cout << json_result << std::endl;
    
    std::cout << "\n✅ Hoàn tất tất cả ví dụ!" << std::endl;
    
    return 0;
}
