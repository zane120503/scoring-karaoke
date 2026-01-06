#ifndef KARAOKE_SCORER_H
#define KARAOKE_SCORER_H

#include <string>
#include <map>

/**
 * @class KaraokeScorer
 * @brief Wrapper class C++ để sử dụng thư viện Python karaoke scoring
 * 
 * Class này cung cấp interface C++ thuận tiện để gọi thư viện Python
 * mà không cần trực tiếp làm việc với Python C API.
 */
class KaraokeScorer {
public:
    /**
     * @brief Constructor - Khởi tạo Python interpreter
     */
    KaraokeScorer();
    
    /**
     * @brief Destructor - Dọn dẹp Python interpreter
     */
    ~KaraokeScorer();
    
    /**
     * @brief Chấm điểm karaoke từ 2 file audio
     * 
     * @param user_audio_path Đường dẫn file audio của người hát (WAV, MP3, FLAC)
     * @param reference_path Đường dẫn file audio/MIDI tham chiếu (WAV, MP3, FLAC, MID, MIDI)
     * @param method Phương pháp trích xuất pitch: "crepe" hoặc "basic_pitch" (mặc định: "crepe")
     * @param tolerance_cents Độ lệch cho phép tính bằng cents (mặc định: 200.0)
     * @param difficulty_mode Độ khó: "easy", "normal", "hard" (mặc định: "easy")
     * @return std::map<std::string, double> Map chứa kết quả chấm điểm
     * 
     * Kết quả trả về bao gồm:
     *   - "final_score": Điểm tổng hợp (0-100)
     *   - "accuracy": Độ chính xác pitch (0-100)
     *   - "dtw_score": Điểm DTW (0-100)
     *   - "dtw_distance": Khoảng cách DTW
     *   - "mae_cents": Độ lệch trung bình (cents)
     *   - "duration": Thời lượng audio (giây)
     * 
     * Nếu có lỗi, map sẽ chứa:
     *   - "error": Thông báo lỗi (string)
     *   - Các trường khác = 0.0
     */
    std::map<std::string, double> score(
        const std::string& user_audio_path,
        const std::string& reference_path,
        const std::string& method = "crepe",
        double tolerance_cents = 200.0,
        const std::string& difficulty_mode = "easy"
    );
    
    /**
     * @brief Chấm điểm và trả về JSON string (raw)
     * 
     * @param user_audio_path Đường dẫn file audio của người hát
     * @param reference_path Đường dẫn file audio/MIDI tham chiếu
     * @param method Phương pháp trích xuất pitch
     * @param tolerance_cents Độ lệch cho phép (cents)
     * @param difficulty_mode Độ khó
     * @return std::string JSON string chứa kết quả
     */
    std::string scoreAsJson(
        const std::string& user_audio_path,
        const std::string& reference_path,
        const std::string& method = "crepe",
        double tolerance_cents = 200.0,
        const std::string& difficulty_mode = "easy"
    );
    
    /**
     * @brief Kiểm tra xem Python interpreter đã được khởi tạo chưa
     * @return true nếu đã khởi tạo, false nếu chưa
     */
    bool isInitialized() const;
    
    /**
     * @brief Lấy thông báo lỗi cuối cùng (nếu có)
     * @return std::string Thông báo lỗi
     */
    std::string getLastError() const;

private:
    bool initialized;
    std::string lastError;
    
    // Helper function để gọi Python
    std::string callPythonFunction(
        const std::string& user_audio_path,
        const std::string& reference_path,
        const std::string& method,
        double tolerance_cents,
        const std::string& difficulty_mode
    );
    
    // Helper function để parse JSON
    std::map<std::string, double> parseJsonResult(const std::string& json_str);
};

#endif // KARAOKE_SCORER_H
