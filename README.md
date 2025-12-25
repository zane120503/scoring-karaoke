# 🎤 Karaoke Scoring System - Pitch Detection Based

Hệ thống chấm điểm karaoke sử dụng **Pitch Detection** mạnh mẽ, không cần tách nhạc nền. Hệ thống sử dụng các model AI hiện đại để nhận diện cao độ (pitch) trực tiếp từ audio hỗn hợp (Vocal + Beat).

## ✨ Tính năng

- 🎯 **Pitch Detection mạnh mẽ**: Sử dụng CREPE hoặc Basic Pitch để trích xuất pitch từ audio hỗn hợp
- 🎵 **So khớp thông minh**: Sử dụng DTW (Dynamic Time Warping) để so khớp pitch người hát với pitch chuẩn
- 📊 **Điểm số chi tiết**: Cung cấp nhiều metrics (accuracy, DTW score, MAE, ...)
- 🎼 **Hỗ trợ MIDI**: Có thể so sánh với file MIDI reference hoặc audio ca sĩ mẫu
- ⚡ **Không cần tách nhạc**: Hoạt động trực tiếp trên audio hỗn hợp

## 📋 Yêu cầu

- Python 3.8+
- Các thư viện trong `requirements.txt`

## 🚀 Cài đặt

1. **Clone hoặc tải project**

2. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

**Lưu ý**: 
- CREPE yêu cầu TensorFlow (sẽ tự động cài khi cài `crepe`)
- **Basic Pitch không được khuyến nghị**: Basic Pitch yêu cầu TensorFlow < 2.15.1, nhưng Python 3.12+ chỉ hỗ trợ TensorFlow >= 2.16.0. Nếu bạn thực sự cần Basic Pitch, hãy dùng Python 3.10 hoặc 3.11.
- Nếu bạn có `paddlepaddle-gpu` đã cài, có thể có cảnh báo về xung đột protobuf, nhưng không ảnh hưởng đến chức năng chính.

## 📖 Hướng dẫn sử dụng

### Cách 1: Sử dụng GUI (Khuyên dùng) 🖥️

Chạy giao diện đồ họa trực quan và dễ sử dụng:

**Windows:**
```bash
# Cách 1: Double-click file
run_gui.bat

# Cách 2: Chạy từ command line
python gui.py
```

**Linux/Mac:**
```bash
# Cách 1: Chạy script
chmod +x run_gui.sh
./run_gui.sh

# Cách 2: Chạy trực tiếp
python3 gui.py
```

**Tính năng GUI:**
- 🎯 Chọn file dễ dàng với file browser
- ⚙️ Điều chỉnh settings trực quan (method, tolerance)
- 📊 Hiển thị kết quả chi tiết với màu sắc phân biệt
- 📈 Visualize pitch contour (cần matplotlib)
- 💾 Lưu kết quả ra file JSON
- ⏳ Progress bar hiển thị tiến trình xử lý

**Các bước sử dụng:**
1. Chạy `python gui.py`
2. Chọn file audio người hát (nút "📂 Chọn file...")
3. Chọn file reference - MIDI hoặc Audio (nút "📂 Chọn file...")
4. Chọn phương pháp (CREPE hoặc Basic Pitch)
5. Điều chỉnh tolerance bằng slider (25-100 cents)
6. Nhấn "🚀 Bắt Đầu Chấm Điểm"
7. Xem kết quả và có thể:
   - Nhấn "📊 Xem Pitch Contour" để xem biểu đồ
   - Nhấn "💾 Lưu Kết Quả" để lưu ra file JSON

### Cách 2: Sử dụng Command Line

#### So sánh với file MIDI reference:
```bash
python karaoke_scorer.py --user audio_user.wav --reference reference.mid
```

#### So sánh với audio ca sĩ mẫu:
```bash
python karaoke_scorer.py --user audio_user.wav --reference reference_audio.wav --method crepe
```

#### Sử dụng Basic Pitch thay vì CREPE:
```bash
python karaoke_scorer.py --user audio_user.wav --reference reference.mid --method basic_pitch
```

#### Tùy chỉnh tolerance (độ lệch cho phép):
```bash
python karaoke_scorer.py --user audio_user.wav --reference reference.mid --tolerance 25.0
```
- Tolerance mặc định: 50 cents (≈ 1/4 tone)
- Tolerance nhỏ hơn = chấm điểm chặt chẽ hơn

#### Lưu kết quả vào file JSON:
```bash
python karaoke_scorer.py --user audio_user.wav --reference reference.mid --output results.json
```

### Cách 3: Sử dụng trong Python code

Xem file `example_usage.py` để biết các ví dụ chi tiết.

#### Ví dụ cơ bản:
```python
from pitch_extractor import PitchExtractor
from pitch_matcher import PitchMatcher

# Khởi tạo extractor
extractor = PitchExtractor(method='crepe')

# Trích xuất pitch từ audio người hát
time_user, freq_user = extractor.extract_pitch('user_audio.wav')

# Trích xuất pitch từ MIDI reference
time_ref, freq_ref = extractor.extract_pitch_from_midi('reference.mid')

# So khớp và tính điểm
matcher = PitchMatcher(tolerance_cents=50.0)
results = matcher.calculate_score(time_user, freq_user, time_ref, freq_ref)

print(f"Điểm tổng hợp: {results['final_score']:.2f}/100")
print(f"Độ chính xác: {results['accuracy']:.2f}%")
```

## 📊 Kết quả

Hệ thống trả về các metrics sau:

- **final_score**: Điểm tổng hợp (0-100)
- **accuracy**: Độ chính xác (% các nốt trong tolerance)
- **dtw_score**: Điểm DTW (0-100)
- **dtw_distance**: Khoảng cách DTW (cents)
- **mae_cents**: Độ lệch trung bình (cents)
- **duration**: Thời lượng so sánh (giây)

## 🔧 Cấu trúc Project

```
scoring karaoke/
├── README.md                 # File này
├── requirements.txt          # Dependencies
├── pitch_extractor.py        # Trích xuất pitch từ audio/MIDI
├── pitch_matcher.py          # So khớp pitch và tính điểm
├── karaoke_scorer.py         # Script chính (command line)
├── gui.py                    # Giao diện đồ họa (GUI)
├── example_usage.py          # Ví dụ sử dụng trong code
├── run_gui.bat               # Launcher cho Windows
└── run_gui.sh                # Launcher cho Linux/Mac
```

## 🎯 Phương pháp Pitch Detection

### CREPE (Khuyên dùng)
- **Ưu điểm**: Chính xác cao, robust với tiếng ồn/nhạc nền
- **Nhược điểm**: Cần TensorFlow, hơi nặng
- **Link**: https://github.com/marl/crepe

### Basic Pitch (Spotify)
- **Ưu điểm**: Nhẹ, có thể chuyển sang MIDI
- **Nhược điểm**: Có thể kém chính xác hơn CREPE trong môi trường nhiều tiếng ồn
- **Link**: https://github.com/spotify/basic-pitch

## 🔍 Thuật toán

1. **Pitch Extraction**: Trích xuất pitch contour từ audio sử dụng CREPE/Basic Pitch
2. **Time Alignment**: Căn chỉnh timeline của hai chuỗi pitch
3. **DTW Matching**: Sử dụng Dynamic Time Warping để so khớp
4. **Scoring**: Tính điểm dựa trên:
   - Accuracy: Tỷ lệ các nốt trong tolerance
   - DTW Score: Dựa trên khoảng cách DTW
   - Final Score: Weighted average của accuracy và DTW score

## 💡 Tips

1. **Chất lượng audio**: Audio càng rõ, kết quả càng chính xác
2. **Giọng hát đủ lớn**: Giọng hát cần đủ lớn so với nhạc nền để model detect được
3. **Tolerance**: 
   - 25 cents: Rất chặt (cho người hát chuyên nghiệp)
   - 50 cents: Vừa phải (mặc định)
   - 100 cents: Dễ (cho người mới tập)
4. **Reference**: MIDI reference thường cho kết quả tốt hơn audio reference

## 🐛 Xử lý lỗi

### Lỗi "CREPE chưa được cài đặt"
```bash
pip install crepe
```

### Lỗi "Basic Pitch chưa được cài đặt"
```bash
pip install basic-pitch
```

### Lỗi "TensorFlow not found"
```bash
pip install tensorflow
```

### Lỗi khi đọc audio
- Đảm bảo file audio ở định dạng được hỗ trợ (WAV, MP3, FLAC, ...)
- Kiểm tra đường dẫn file có đúng không

## 📝 License

MIT License - Tự do sử dụng và chỉnh sửa

## 🙏 Credits

- **CREPE**: https://github.com/marl/crepe
- **Basic Pitch**: https://github.com/spotify/basic-pitch
- **FastDTW**: https://github.com/slaypni/fastdtw
- **Librosa**: https://github.com/librosa/librosa

