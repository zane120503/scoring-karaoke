# 🔄 Pipeline Xử Lý - Karaoke Scoring System

Tài liệu này mô tả chi tiết quy trình xử lý (pipeline) của hệ thống chấm điểm karaoke.

## 📊 Sơ Đồ Tổng Quan

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT: Audio Files                           │
│  ┌──────────────────┐         ┌──────────────────┐           │
│  │ Audio người hát   │         │ Reference        │           │
│  │ (Vocal + Beat)   │         │ (MIDI/Audio)     │           │
│  └──────────────────┘         └──────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              BƯỚC 1: Pitch Extraction (Trích xuất Pitch)        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  PitchExtractor.extract_pitch()                          │ │
│  │  - Load audio: librosa.load() → 16kHz                    │ │
│  │  - CREPE/Basic Pitch: Detect pitch từ audio              │ │
│  │  - Filter: Loại bỏ pitch không đáng tin (confidence<0.5)│ │
│  │  - Output: (time[], frequency[])                         │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  PitchExtractor.extract_pitch_from_midi() (nếu MIDI)     │ │
│  │  - Parse MIDI: mido.MidiFile()                           │ │
│  │  - Extract notes: note_on events                         │ │
│  │  - Convert: MIDI note → Hz (f = 440 * 2^((n-69)/12))    │ │
│  │  - Output: (time[], frequency[])                         │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│         BƯỚC 2: Time Alignment (Căn chỉnh thời gian)          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  PitchMatcher.align_time_series()                        │ │
│  │  - Tìm khoảng thời gian chung                            │ │
│  │  - Tạo timeline mới: resolution 10ms (100Hz)            │ │
│  │  - Nội suy: interpolate_pitch() → cùng timeline         │ │
│  │  - Output: (aligned_time[], aligned_freq1[], aligned_freq2[])│
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│      BƯỚC 3: Unit Conversion (Chuyển đổi đơn vị)              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  PitchMatcher.hz_to_cents()                              │ │
│  │  - Convert Hz → Cents                                    │ │
│  │  - Formula: cents = 1200 * log2(Hz / 440)               │ │
│  │  - Lý do: Cents là đơn vị tương đối, dễ so sánh         │ │
│  │  - Output: (cents_user[], cents_reference[])           │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│     BƯỚC 4: Pitch Matching (So khớp Pitch)                    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  4.1. Accuracy Calculation                               │ │
│  │  PitchMatcher.calculate_accuracy()                      │ │
│  │  - Tính độ lệch: |cents_user - cents_ref|               │ │
│  │  - Đếm số điểm trong tolerance (mặc định 50 cents)      │ │
│  │  - Accuracy = số điểm đúng / tổng số điểm              │ │
│  │  - Output: accuracy (0-1)                                │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  4.2. DTW Distance Calculation                           │ │
│  │  PitchMatcher.calculate_dtw_distance()                  │ │
│  │  - Dynamic Time Warping: So khớp 2 chuỗi có độ dài khác │ │
│  │  - Tìm đường đi tối ưu: fastdtw()                       │ │
│  │  - Tính khoảng cách: euclidean distance                 │ │
│  │  - Output: (dtw_distance, dtw_path)                     │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  4.3. Mean Absolute Error (MAE)                            │ │
│  │  - Tính độ lệch trung bình: mean(|cents_user - cents_ref|)│
│  │  - Output: mae_cents                                      │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│         BƯỚC 5: Score Calculation (Tính điểm)                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  PitchMatcher.calculate_score()                           │ │
│  │                                                           │ │
│  │  5.1. Normalize DTW Score                                │ │
│  │  - max_distance = len(timeline) * tolerance * 2         │ │
│  │  - dtw_score = max(0, 100 - (distance/max_distance)*100)│ │
│  │                                                           │ │
│  │  5.2. Final Score (Weighted Average)                    │ │
│  │  - final_score = accuracy * 60 + (dtw_score/100) * 40   │ │
│  │  - Accuracy weight: 60%                                 │ │
│  │  - DTW Score weight: 40%                                 │ │
│  │                                                           │ │
│  │  Output: {                                                │ │
│  │    'final_score': 0-100,                                 │ │
│  │    'accuracy': 0-100%,                                   │ │
│  │    'dtw_score': 0-100,                                  │ │
│  │    'dtw_distance': cents,                               │ │
│  │    'mae_cents': cents,                                   │ │
│  │    'duration': seconds                                  │ │
│  │  }                                                        │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT: Kết Quả                              │
│  - Hiển thị trên console/GUI                                   │
│  - Lưu vào file JSON (tùy chọn)                                │
└─────────────────────────────────────────────────────────────────┘
```

## 📝 Chi Tiết Từng Bước

### BƯỚC 1: Pitch Extraction (Trích xuất Pitch)

**Mục đích**: Trích xuất đường biểu diễn cao độ (pitch contour) từ audio hoặc MIDI.

**Input**:
- File audio: `.wav`, `.mp3`, `.flac`, ... (hỗn hợp Vocal + Beat)
- File MIDI: `.mid`, `.midi` (cho reference)

**Xử lý**:

#### 1.1. Audio → Pitch (CREPE)
```python
# Load audio và resample về 16kHz
audio, sr = librosa.load(audio_path, sr=16000)

# CREPE predict
time, frequency, confidence, activation = crepe.predict(
    audio, sr, 
    viterbi=True,           # Làm mượt kết quả
    model_capacity='full',   # Model size
    step_size=10            # 10ms resolution
)

# Filter: Loại bỏ pitch không đáng tin
mask = confidence > 0.5
frequency = frequency[mask]
```

**Output**: 
- `time[]`: Mảng thời gian (giây)
- `frequency[]`: Mảng tần số (Hz)

#### 1.2. MIDI → Pitch
```python
# Parse MIDI
midi = MidiFile(midi_path)

# Extract notes
for msg in track:
    if msg.type == 'note_on':
        # Convert MIDI note → Hz
        freq = 440 * (2 ** ((msg.note - 69) / 12))
```

**Output**: 
- `time[]`: Thời gian bắt đầu nốt
- `frequency[]`: Tần số nốt (Hz)

---

### BƯỚC 2: Time Alignment (Căn chỉnh thời gian)

**Mục đích**: Căn chỉnh hai chuỗi pitch về cùng resolution thời gian để so sánh.

**Input**:
- `time_user[]`, `freq_user[]`: Pitch người hát
- `time_ref[]`, `freq_ref[]`: Pitch reference

**Xử lý**:
```python
# Tìm khoảng thời gian chung
start_time = max(time_user[0], time_ref[0])
end_time = min(time_user[-1], time_ref[-1])

# Tạo timeline mới với resolution 10ms
dt = 0.01  # 10ms
aligned_time = np.arange(start_time, end_time, dt)

# Nội suy cả hai chuỗi về timeline mới
aligned_freq_user = np.interp(aligned_time, time_user, freq_user)
aligned_freq_ref = np.interp(aligned_time, time_ref, freq_ref)
```

**Output**:
- `aligned_time[]`: Timeline chung
- `aligned_freq_user[]`: Pitch người hát đã căn chỉnh
- `aligned_freq_ref[]`: Pitch reference đã căn chỉnh

---

### BƯỚC 3: Unit Conversion (Chuyển đổi đơn vị)

**Mục đích**: Chuyển từ Hz sang Cents để so sánh dễ dàng hơn.

**Lý do dùng Cents**:
- Cents là đơn vị tương đối (logarithmic)
- 1 semitone = 100 cents
- Dễ tính độ lệch giữa các nốt

**Công thức**:
```python
cents = 1200 * log2(Hz / 440)
```

**Input**: `frequency[]` (Hz)  
**Output**: `cents[]` (cents)

---

### BƯỚC 4: Pitch Matching (So khớp Pitch)

#### 4.1. Accuracy Calculation

**Mục đích**: Tính tỷ lệ các nốt người hát nằm trong tolerance.

**Công thức**:
```python
deviation = |cents_user - cents_ref|
in_tolerance = sum(deviation <= tolerance_cents)
accuracy = in_tolerance / total_points
```

**Input**: 
- `cents_user[]`, `cents_ref[]`
- `tolerance_cents` (mặc định: 50 cents ≈ 1/4 tone)

**Output**: `accuracy` (0-1)

#### 4.2. DTW Distance Calculation

**Mục đích**: So khớp hai chuỗi có độ dài khác nhau bằng Dynamic Time Warping.

**Thuật toán DTW**:
- Tìm đường đi tối ưu giữa hai chuỗi
- Cho phép "co giãn" thời gian
- Tính tổng khoảng cách euclidean

**Công thức**:
```python
distance, path = fastdtw(
    cents_user.reshape(-1, 1),
    cents_ref.reshape(-1, 1),
    dist=euclidean
)
```

**Input**: `cents_user[]`, `cents_ref[]`  
**Output**: `dtw_distance` (cents)

#### 4.3. Mean Absolute Error (MAE)

**Mục đích**: Tính độ lệch trung bình.

**Công thức**:
```python
mae = mean(|cents_user - cents_ref|)
```

**Output**: `mae_cents` (cents)

---

### BƯỚC 5: Score Calculation (Tính điểm)

#### 5.1. Normalize DTW Score

**Mục đích**: Chuyển DTW distance thành điểm 0-100.

**Công thức**:
```python
max_expected_distance = len(timeline) * tolerance_cents * 2
dtw_score = max(0, 100 - (dtw_distance / max_expected_distance) * 100)
```

#### 5.2. Final Score

**Mục đích**: Tính điểm tổng hợp.

**Công thức**:
```python
final_score = accuracy * 60 + (dtw_score / 100) * 40
```

**Weight**:
- Accuracy: 60% (tỷ lệ nốt đúng)
- DTW Score: 40% (độ tương đồng tổng thể)

**Output**:
```python
{
    'final_score': 0-100,      # Điểm tổng hợp
    'accuracy': 0-100%,        # Độ chính xác
    'dtw_score': 0-100,        # Điểm DTW
    'dtw_distance': cents,     # Khoảng cách DTW
    'mae_cents': cents,        # Độ lệch trung bình
    'duration': seconds         # Thời lượng so sánh
}
```

---

## 🔧 Các Module Chính

### 1. `PitchExtractor` (`pitch_extractor.py`)

**Chức năng**: Trích xuất pitch từ audio/MIDI

**Methods**:
- `extract_pitch(audio_path)`: Trích xuất từ audio
- `extract_pitch_from_midi(midi_path)`: Trích xuất từ MIDI
- `extract_pitch_crepe()`: Sử dụng CREPE
- `extract_pitch_basic_pitch()`: Sử dụng Basic Pitch

### 2. `PitchMatcher` (`pitch_matcher.py`)

**Chức năng**: So khớp pitch và tính điểm

**Methods**:
- `align_time_series()`: Căn chỉnh timeline
- `interpolate_pitch()`: Nội suy pitch
- `hz_to_cents()`: Chuyển Hz → Cents
- `calculate_accuracy()`: Tính accuracy
- `calculate_dtw_distance()`: Tính DTW distance
- `calculate_score()`: Tính điểm tổng hợp

### 3. `karaoke_scorer.py`

**Chức năng**: Script chính (command line)

**Flow**:
1. Parse arguments
2. Validate files
3. Extract pitch (user + reference)
4. Match và tính điểm
5. Hiển thị/lưu kết quả

### 4. `gui.py`

**Chức năng**: Giao diện đồ họa

**Flow**:
1. User chọn files và settings
2. Chạy scoring trong thread riêng
3. Hiển thị kết quả real-time
4. Có thể visualize pitch contour

---

## 📈 Độ Phức Tạp

- **Pitch Extraction**: O(n) với n = số mẫu audio
- **Time Alignment**: O(n) với n = độ dài timeline
- **DTW**: O(n*m) với n, m = độ dài hai chuỗi
- **Tổng thể**: O(n*m) - phụ thuộc vào DTW

---

## 🎯 Tối Ưu Hóa

1. **CREPE Model Capacity**: Có thể dùng 'tiny', 'small' để nhanh hơn (kém chính xác hơn)
2. **Step Size**: Tăng step_size (10ms → 20ms) để giảm số điểm
3. **DTW Radius**: Có thể giới hạn radius trong fastdtw để nhanh hơn
4. **Parallel Processing**: Có thể xử lý nhiều file song song

---

## 🔍 Xử Lý Lỗi

- **File không tồn tại**: Validate trước khi xử lý
- **Audio không có pitch**: Filter confidence > 0.5
- **Không có overlap**: Tạo timeline từ cả hai
- **NaN/Inf values**: Loại bỏ bằng mask
- **Empty arrays**: Return 0 score

---

## 📚 Tham Khảo

- **CREPE**: https://github.com/marl/crepe
- **DTW**: https://en.wikipedia.org/wiki/Dynamic_time_warping
- **Cents**: https://en.wikipedia.org/wiki/Cent_(music)

