"""
GUI cho Karaoke Scoring System
Sử dụng tkinter với ttk để tạo giao diện đẹp và hiện đại
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path
import json
from pitch_extractor import PitchExtractor
from pitch_matcher import PitchMatcher
from pitch_advisor import PitchAdvisor


class KaraokeScorerGUI:
    """Giao diện GUI cho hệ thống chấm điểm karaoke"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎤 Karaoke Scoring System")
        self.root.geometry("1000x900")  # Tăng kích thước để hiển thị đầy đủ
        self.root.resizable(True, True)
        # Đặt cửa sổ ở giữa màn hình
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Biến lưu trữ
        self.user_audio_path = tk.StringVar()
        self.reference_path = tk.StringVar()
        self.method_var = tk.StringVar(value="crepe")
        self.tolerance_var = tk.DoubleVar(value=200.0)  # Mặc định 200 cents (rất dễ)
        self.difficulty_var = tk.StringVar(value="easy")  # Thêm chế độ độ khó
        self.normalize_audio_var = tk.BooleanVar(value=True)  # Normalize audio mặc định bật
        self.midi_track_var = tk.StringVar(value="auto")
        self.midi_pitch_min_var = tk.DoubleVar(value=80.0)
        self.midi_pitch_max_var = tk.DoubleVar(value=2000.0)
        self.use_pitch_filter_var = tk.BooleanVar(value=False)
        self.is_processing = False
        
        # Lưu pitch data để phân tích
        self.last_pitch_data = None  # (time_user, freq_user, time_ref, freq_ref)
        
        # Tạo giao diện
        self.create_widgets()
        
        # Style
        self.setup_styles()
    
    def setup_styles(self):
        """Thiết lập style cho giao diện"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Tùy chỉnh màu sắc
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 11, 'bold'))
        style.configure('Result.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Score.TLabel', font=('Arial', 20, 'bold'), foreground='#2E7D32')
    
    def create_widgets(self):
        """Tạo các widget cho giao diện"""
        # Container chính
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Tiêu đề
        title_label = ttk.Label(
            main_frame, 
            text="🎤 Hệ Thống Chấm Điểm Karaoke",
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # === PHẦN NHẬP LIỆU ===
        input_frame = ttk.LabelFrame(main_frame, text="📁 Chọn File", padding="15")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        input_frame.columnconfigure(1, weight=1)
        
        # File audio người hát
        ttk.Label(input_frame, text="Audio người hát:", style='Heading.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(input_frame, textvariable=self.user_audio_path, width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        ttk.Button(
            input_frame, 
            text="📂 Chọn file...", 
            command=self.browse_user_audio
        ).grid(row=0, column=2, padx=5, pady=5)
        
        # File reference (ca sĩ mẫu)
        ttk.Label(input_frame, text="Audio ca sĩ mẫu:", style='Heading.TLabel').grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(input_frame, textvariable=self.reference_path, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        ttk.Button(
            input_frame, 
            text="📂 Chọn file...", 
            command=self.browse_reference
        ).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Label(
            input_frame, 
            text="(Audio ca sĩ mẫu - chỉ giọng hoặc giọng+beat, WAV/MP3/FLAC)", 
            font=('Arial', 8), 
            foreground='gray'
        ).grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # === PHẦN CÀI ĐẶT ===
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Cài Đặt", padding="15")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        settings_frame.columnconfigure(1, weight=1)
        
        # Phương pháp
        ttk.Label(settings_frame, text="Phương pháp:", style='Heading.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        method_frame = ttk.Frame(settings_frame)
        method_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(
            method_frame, 
            text="CREPE (Khuyên dùng)", 
            variable=self.method_var, 
            value="crepe"
        ).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(
            method_frame, 
            text="Basic Pitch", 
            variable=self.method_var, 
            value="basic_pitch"
        ).pack(side=tk.LEFT, padx=10)
        
        # Tolerance
        ttk.Label(settings_frame, text="Tolerance (cents):", style='Heading.TLabel').grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        tolerance_frame = ttk.Frame(settings_frame)
        tolerance_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        tolerance_scale = ttk.Scale(
            tolerance_frame,
            from_=50.0,
            to=300.0,  # Tăng phạm vi lên 300 để có thể điều chỉnh cao hơn
            variable=self.tolerance_var,
            orient=tk.HORIZONTAL,
            length=300
        )
        tolerance_scale.pack(side=tk.LEFT, padx=5)
        
        tolerance_label = ttk.Label(tolerance_frame, textvariable=self.tolerance_var)
        tolerance_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            tolerance_frame, 
            text="(50=chặt, 100=vừa, 200=dễ, 300=rất dễ)", 
            font=('Arial', 9), 
            foreground='gray'
        ).pack(side=tk.LEFT, padx=10)
        
        # Chế độ độ khó
        ttk.Label(settings_frame, text="Độ khó:", style='Heading.TLabel').grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        difficulty_frame = ttk.Frame(settings_frame)
        difficulty_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(
            difficulty_frame, 
            text="Dễ (Khuyến nghị)", 
            variable=self.difficulty_var, 
            value="easy"
        ).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(
            difficulty_frame, 
            text="Vừa", 
            variable=self.difficulty_var, 
            value="normal"
        ).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(
            difficulty_frame, 
            text="Khó", 
            variable=self.difficulty_var, 
            value="hard"
        ).pack(side=tk.LEFT, padx=10)
        
        # Normalize Audio
        ttk.Label(settings_frame, text="Normalize Audio:", style='Heading.TLabel').grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        normalize_frame = ttk.Frame(settings_frame)
        normalize_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Checkbutton(
            normalize_frame,
            text="Chuẩn hóa âm lượng (Khuyến nghị)",
            variable=self.normalize_audio_var
        ).pack(side=tk.LEFT, padx=5)
        ttk.Label(
            normalize_frame,
            text="(Giúp công bằng khi so sánh 2 file có volume khác nhau)",
            font=('Arial', 8),
            foreground='gray'
        ).pack(side=tk.LEFT, padx=10)
        
        # MIDI Settings - Ẩn vì không còn sử dụng (chỉ dùng audio với audio)
        # Giữ lại code để tương thích ngược nếu cần
        # self.midi_settings_frame = ttk.LabelFrame(settings_frame, text="🎼 MIDI Settings", padding="10")
        # self.midi_settings_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # === NÚT CHẠY ===
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=15)
        
        self.run_button = ttk.Button(
            button_frame,
            text="🚀 Bắt Đầu Chấm Điểm",
            command=self.start_scoring,
            style='Accent.TButton'
        )
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📊 Xem Pitch Contour",
            command=self.show_pitch_contour
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="💾 Lưu Kết Quả",
            command=self.save_results
        ).pack(side=tk.LEFT, padx=5)
        
        # === PROGRESS BAR ===
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        self.progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="")
        self.progress_label = ttk.Label(
            self.progress_frame, 
            textvariable=self.progress_var,
            font=('Arial', 10)
        )
        self.progress_label.grid(row=0, column=0, pady=5)
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='indeterminate',
            length=400
        )
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # === PHẦN KẾT QUẢ ===
        results_frame = ttk.LabelFrame(main_frame, text="📊 Kết Quả", padding="15")
        results_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Điểm tổng hợp
        self.final_score_label = ttk.Label(
            results_frame,
            text="Chưa có kết quả",
            style='Score.TLabel',
            font=('Arial', 24, 'bold')
        )
        self.final_score_label.grid(row=0, column=0, pady=10)
        
        # Các metrics chi tiết
        self.metrics_frame = ttk.Frame(results_frame)
        self.metrics_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        # Cho cột 1 (giá trị bên trái) co giãn để đẩy nhóm cột bên phải ra sát phải hơn
        self.metrics_frame.columnconfigure(1, weight=1)
        
        self.metrics_labels = {}
        metrics = [
            ('accuracy', 'Độ chính xác:'),
            ('dtw_score', 'Điểm DTW:'),
            ('dtw_distance', 'Khoảng cách DTW:'),
            ('mae_cents', 'Độ lệch trung bình:'),
            ('duration', 'Thời lượng:')
        ]
        
        for i, (key, label) in enumerate(metrics):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(
                self.metrics_frame,
                text=label,
                style='Heading.TLabel'
            ).grid(row=row, column=col, sticky=tk.W, padx=(10, 5), pady=5)
            
            value_label = ttk.Label(
                self.metrics_frame,
                text="--",
                font=('Arial', 10)
            )
            # Đẩy số sang bên phải thêm một chút (padding trái = 15)
            value_label.grid(row=row, column=col+1, sticky=tk.W, padx=(15, 20), pady=5)
            self.metrics_labels[key] = value_label
        
        # Phần lời khuyên
        advice_label = ttk.Label(
            results_frame,
            text="💡 Lời Khuyên:",
            style='Heading.TLabel',
            font=('Arial', 11, 'bold')
        )
        advice_label.grid(row=2, column=0, sticky=tk.W, pady=(15, 5))
        
        # Text widget để hiển thị lời khuyên (có scrollbar)
        advice_frame = ttk.Frame(results_frame)
        advice_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        advice_frame.columnconfigure(0, weight=1)
        advice_frame.rowconfigure(0, weight=1)
        results_frame.rowconfigure(3, weight=1)
        
        self.advice_text = tk.Text(
            advice_frame,
            wrap=tk.WORD,
            height=10,  # Tăng chiều cao ô lời khuyên
            font=('Arial', 9),
            bg='#F5F5F5',
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.advice_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        advice_scrollbar = ttk.Scrollbar(advice_frame, orient=tk.VERTICAL, command=self.advice_text.yview)
        advice_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.advice_text.configure(yscrollcommand=advice_scrollbar.set)
        
        # Lưu kết quả
        self.current_results = None
    
    def browse_user_audio(self):
        """Chọn file audio người hát"""
        filename = filedialog.askopenfilename(
            title="Chọn file audio người hát",
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.flac *.m4a *.ogg"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.user_audio_path.set(filename)
    
    def browse_reference(self):
        """Chọn file audio ca sĩ mẫu"""
        filename = filedialog.askopenfilename(
            title="Chọn file audio ca sĩ mẫu",
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.flac *.m4a *.ogg"),
                ("WAV files", "*.wav"),
                ("MP3 files", "*.mp3"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.reference_path.set(filename)
    
    def validate_inputs(self):
        """Kiểm tra đầu vào"""
        if not self.user_audio_path.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn file audio người hát!")
            return False
        
        if not os.path.exists(self.user_audio_path.get()):
            messagebox.showerror("Lỗi", "File audio người hát không tồn tại!")
            return False
        
        if not self.reference_path.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn file audio ca sĩ mẫu!")
            return False
        
        if not os.path.exists(self.reference_path.get()):
            messagebox.showerror("Lỗi", "File audio ca sĩ mẫu không tồn tại!")
            return False
        
        return True
    
    def start_scoring(self):
        """Bắt đầu chấm điểm (chạy trong thread riêng)"""
        if not self.validate_inputs():
            return
        
        if self.is_processing:
            messagebox.showwarning("Cảnh báo", "Đang xử lý, vui lòng đợi...")
            return
        
        # Chạy trong thread riêng để không block GUI
        thread = threading.Thread(target=self.scoring_worker, daemon=True)
        thread.start()
    
    def scoring_worker(self):
        """Worker thread để chấm điểm"""
        self.is_processing = True
        self.run_button.config(state='disabled')
        self.progress_bar.start()
        
        try:
            user_path = self.user_audio_path.get()
            ref_path = self.reference_path.get()
            method = self.method_var.get()
            tolerance = self.tolerance_var.get()
            difficulty = self.difficulty_var.get()  # Lấy chế độ độ khó
            normalize_audio = self.normalize_audio_var.get()  # Lấy tùy chọn normalize
            
            # Trích xuất pitch từ audio người hát
            # Sử dụng tiny model và không dùng viterbi để tăng tốc độ (~10s cho bài hát)
            self.update_progress("⏳ Đang trích xuất pitch từ audio người hát...")
            extractor_user = PitchExtractor(method=method, model_capacity='tiny', normalize_audio=normalize_audio)
            if method == 'crepe':
                time_user, freq_user = extractor_user.extract_pitch(user_path, step_size=50, use_viterbi=False)
            else:
                time_user, freq_user = extractor_user.extract_pitch(user_path)
            
            # Trích xuất pitch từ reference audio (ca sĩ mẫu)
            ref_ext = Path(ref_path).suffix.lower()
            if ref_ext in ['.mid', '.midi']:
                # Vẫn hỗ trợ MIDI nếu cần
                self.update_progress("⏳ Đang đọc file MIDI...")
                track_filter_value = self.midi_track_var.get()
                if track_filter_value and track_filter_value != "None" and track_filter_value != "auto":
                    track_filter = track_filter_value
                elif track_filter_value == "auto":
                    track_filter = "auto"
                else:
                    track_filter = None
                pitch_range = None
                if self.use_pitch_filter_var.get():
                    pitch_range = (self.midi_pitch_min_var.get(), self.midi_pitch_max_var.get())
                time_ref, freq_ref = extractor_user.extract_pitch_from_midi(
                    ref_path,
                    track_filter=track_filter,
                    pitch_range=pitch_range
                )
            else:
                # Xử lý audio reference (ca sĩ mẫu) - sử dụng cùng settings với user audio để công bằng
                self.update_progress("⏳ Đang trích xuất pitch từ audio ca sĩ mẫu...")
                extractor_ref = PitchExtractor(method=method, model_capacity='tiny', normalize_audio=normalize_audio)
                # Sử dụng cùng settings với user audio (step_size, viterbi) để đảm bảo công bằng
                if method == 'crepe':
                    time_ref, freq_ref = extractor_ref.extract_pitch(ref_path, step_size=50, use_viterbi=False)
                else:
                    time_ref, freq_ref = extractor_ref.extract_pitch(ref_path)
            
            # So khớp và tính điểm
            self.update_progress("⏳ Đang so khớp pitch và tính điểm...")
            matcher = PitchMatcher(tolerance_cents=tolerance, difficulty_mode=difficulty)
            results = matcher.calculate_score(
                time_user, freq_user,
                time_ref, freq_ref
            )
            
            # Lưu pitch data để phân tích
            self.last_pitch_data = (time_user, freq_user, time_ref, freq_ref)
            
            # Phân tích và đưa ra lời khuyên
            self.update_progress("⏳ Đang phân tích và tạo lời khuyên...")
            try:
                advisor = PitchAdvisor(tolerance_cents=tolerance)
                advice_result = advisor.analyze_pitch_contour(
                    time_user, freq_user,
                    time_ref, freq_ref
                )
                results['advice'] = advice_result
            except Exception as e:
                # Nếu có lỗi khi phân tích, vẫn tiếp tục nhưng không có advice
                print(f"⚠️ Lỗi khi phân tích lời khuyên: {str(e)}")
                import traceback
                traceback.print_exc()
                results['advice'] = None
            
            # Cập nhật kết quả lên GUI
            self.root.after(0, self.display_results, results)
            self.update_progress("✅ Hoàn thành!")
            
        except Exception as e:
            error_msg = f"Lỗi: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Lỗi", error_msg))
            self.update_progress("❌ Có lỗi xảy ra!")
        finally:
            self.progress_bar.stop()
            self.is_processing = False
            self.run_button.config(state='normal')
            self.root.after(0, lambda: self.progress_var.set(""))
    
    def update_progress(self, message):
        """Cập nhật thông báo tiến trình"""
        self.root.after(0, lambda: self.progress_var.set(message))
    
    def display_results(self, results):
        """Hiển thị kết quả lên giao diện"""
        self.current_results = results
        
        # Đảm bảo advice được reset nếu không có trong results
        if 'advice' not in results:
            results['advice'] = None
        
        # Điểm tổng hợp
        score = results['final_score']
        color = self.get_score_color(score)
        self.final_score_label.config(
            text=f"Điểm: {score:.2f}/100",
            foreground=color
        )
        
        # Các metrics
        self.metrics_labels['accuracy'].config(
            text=f"{results['accuracy']:.2f}%"
        )
        self.metrics_labels['dtw_score'].config(
            text=f"{results['dtw_score']:.2f}/100"
        )
        self.metrics_labels['dtw_distance'].config(
            text=f"{results['dtw_distance']:.2f} cents"
        )
        self.metrics_labels['mae_cents'].config(
            text=f"{results['mae_cents']:.2f} cents"
        )
        self.metrics_labels['duration'].config(
            text=f"{results['duration']:.2f} giây"
        )
        
        # Hiển thị lời khuyên - Enable trước khi xóa để đảm bảo có thể cập nhật
        self.advice_text.config(state='normal')
        # Xóa toàn bộ nội dung cũ
        self.advice_text.delete('1.0', tk.END)
        
        # Kiểm tra và hiển thị advice mới
        if 'advice' in results and results['advice'] is not None:
            try:
                advice_result = results['advice']
                if isinstance(advice_result, dict):
                    advice_summary = self.format_advice(advice_result)
                    self.advice_text.insert('1.0', advice_summary)
                else:
                    self.advice_text.insert('1.0', "Lời khuyên đang được tính toán...")
            except Exception as e:
                import traceback
                error_msg = f"Lỗi khi hiển thị lời khuyên: {str(e)}\n{traceback.format_exc()}"
                print(error_msg)
                self.advice_text.insert('1.0', f"Lỗi khi hiển thị lời khuyên: {str(e)}")
        else:
            # Không có advice - hiển thị thông báo mặc định
            self.advice_text.insert('1.0', "Chưa có lời khuyên. Vui lòng chạy chấm điểm để nhận lời khuyên.")
        
        # Scroll về đầu
        self.advice_text.see('1.0')
        self.advice_text.config(state='disabled')  # Chỉ đọc
    
    def format_advice(self, advice_result: dict) -> str:
        """Format lời khuyên để hiển thị"""
        lines = []
        
        if advice_result.get('strengths'):
            lines.append("✅ ĐIỂM MẠNH:")
            for strength in advice_result['strengths']:
                lines.append(f"   • {strength}")
            lines.append("")
        
        if advice_result.get('issues'):
            lines.append("⚠️ CẦN CẢI THIỆN:")
            for issue in advice_result['issues']:
                lines.append(f"   • {issue}")
            lines.append("")
        
        if advice_result.get('advices'):
            lines.append("💡 LỜI KHUYÊN:")
            for advice in advice_result['advices']:
                lines.append(f"   {advice}")
        
        if not lines:
            return "🎉 Tuyệt vời! Bạn đang hát rất tốt!"
        
        return "\n".join(lines)
    
    def get_score_color(self, score):
        """Lấy màu dựa trên điểm số"""
        if score >= 80:
            return '#2E7D32'  # Xanh lá đậm
        elif score >= 60:
            return '#F57C00'  # Cam
        else:
            return '#C62828'  # Đỏ
    
    def show_pitch_contour(self):
        """Hiển thị biểu đồ pitch contour"""
        if not self.user_audio_path.get() or not self.reference_path.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chạy chấm điểm trước!")
            return
        
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            messagebox.showerror(
                "Lỗi", 
                "Cần cài đặt matplotlib để xem biểu đồ:\npip install matplotlib"
            )
            return
        
        # Tạo cửa sổ mới
        plot_window = tk.Toplevel(self.root)
        plot_window.title("📊 Pitch Contour Visualization")
        plot_window.geometry("1000x600")
        
        try:
            # Trích xuất pitch
            method = self.method_var.get()
            normalize_audio = self.normalize_audio_var.get()
            # Sử dụng tiny model để tăng tốc độ
            extractor_user = PitchExtractor(method=method, model_capacity='tiny', normalize_audio=normalize_audio)
            if method == 'crepe':
                time_user, freq_user = extractor_user.extract_pitch(self.user_audio_path.get(), step_size=50, use_viterbi=False)
            else:
                time_user, freq_user = extractor_user.extract_pitch(self.user_audio_path.get())
            
            ref_path = self.reference_path.get()
            ref_ext = Path(ref_path).suffix.lower()
            if ref_ext in ['.mid', '.midi']:
                track_filter_value = self.midi_track_var.get()
                if track_filter_value and track_filter_value != "None" and track_filter_value != "auto":
                    track_filter = track_filter_value
                elif track_filter_value == "auto":
                    track_filter = "auto"
                else:
                    track_filter = None
                pitch_range = None
                if self.use_pitch_filter_var.get():
                    pitch_range = (self.midi_pitch_min_var.get(), self.midi_pitch_max_var.get())
                time_ref, freq_ref = extractor_user.extract_pitch_from_midi(
                    ref_path,
                    track_filter=track_filter,
                    pitch_range=pitch_range
                )
            else:
                extractor_ref = PitchExtractor(method=method, model_capacity='tiny', normalize_audio=normalize_audio)
                if method == 'crepe':
                    time_ref, freq_ref = extractor_ref.extract_pitch(ref_path, step_size=50, use_viterbi=False)
                else:
                    time_ref, freq_ref = extractor_ref.extract_pitch(ref_path)
            
            # Vẽ biểu đồ
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(time_user, freq_user, label='Người hát', alpha=0.7, linewidth=1.5, color='#FF3333')
            ax.plot(time_ref, freq_ref, label='Reference', alpha=0.7, linewidth=1.5, color='#009900')
            ax.set_xlabel('Thời gian (s)', fontsize=12)
            ax.set_ylabel('Tần số (Hz)', fontsize=12)
            ax.set_title('Pitch Contour Comparison', fontsize=14, fontweight='bold')
            ax.legend(fontsize=11)
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Hiển thị trong tkinter
            canvas = FigureCanvasTkAgg(fig, plot_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể vẽ biểu đồ: {str(e)}")
            plot_window.destroy()
    
    def save_results(self):
        """Lưu kết quả vào file JSON"""
        if not self.current_results:
            messagebox.showwarning("Cảnh báo", "Chưa có kết quả để lưu!")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Lưu kết quả",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.current_results, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Thành công", f"Đã lưu kết quả vào:\n{filename}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file: {str(e)}")


def main():
    """Hàm main để chạy GUI"""
    root = tk.Tk()
    app = KaraokeScorerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

