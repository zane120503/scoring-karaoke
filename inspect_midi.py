"""
Script để kiểm tra và hiển thị thông tin các track trong file MIDI
"""
import argparse
import sys
from pathlib import Path

try:
    from mido import MidiFile
    import mido
except ImportError:
    print("❌ Cần cài đặt mido: pip install mido")
    sys.exit(1)


def inspect_midi(midi_path: str):
    """
    Kiểm tra và hiển thị thông tin các track trong file MIDI
    
    Args:
        midi_path: Đường dẫn file MIDI
    """
    
    if not Path(midi_path).exists():
        print(f"❌ Không tìm thấy file: {midi_path}")
        sys.exit(1)
    
    print(f"📁 File MIDI: {midi_path}")
    print("=" * 70)
    
    midi = MidiFile(midi_path)
    
    print(f"📊 Thông tin tổng quan:")
    print(f"   - Số track: {len(midi.tracks)}")
    print(f"   - Ticks per beat: {midi.ticks_per_beat}")
    print(f"   - Độ dài: {midi.length:.2f} giây")
    print()
    
    # Từ khóa để nhận diện track vocal
    vocal_keywords = ['vocal', 'voice', 'sing', 'melody', 'lead', 'solo', 'vox']
    beat_keywords = ['drum', 'beat', 'percussion', 'kick', 'snare', 'hihat', 'bass']
    
    print("🎵 Danh sách các track:")
    print("-" * 70)
    
    track_info = []
    
    for track_idx, track in enumerate(midi.tracks):
        # Lấy tên track
        track_name = ""
        for msg in track:
            if msg.type == 'track_name':
                track_name = msg.name
                break
        
        if not track_name:
            track_name = f"Track {track_idx + 1}"
        
        # Đếm số note
        note_count = 0
        note_range = []
        tempo = 500000  # Mặc định 120 BPM
        current_time = 0.0
        
        for msg in track:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
            
            if midi.ticks_per_beat > 0:
                current_time += mido.tick2second(msg.time, midi.ticks_per_beat, tempo)
            
            if msg.type == 'note_on' and msg.velocity > 0:
                note_count += 1
                # Convert MIDI note to Hz
                freq = 440 * (2 ** ((msg.note - 69) / 12))
                note_range.append(freq)
        
        # Phân loại track
        track_name_lower = track_name.lower()
        track_type = "❓ Khác"
        
        if any(keyword in track_name_lower for keyword in vocal_keywords):
            track_type = "🎤 VOCAL"
        elif any(keyword in track_name_lower for keyword in beat_keywords):
            track_type = "🥁 BEAT"
        elif note_count > 0:
            # Phân loại theo pitch range
            if note_range:
                min_freq = min(note_range)
                max_freq = max(note_range)
                if min_freq >= 80 and max_freq <= 2000:
                    track_type = "🎵 Có thể là VOCAL (pitch 80-2000 Hz)"
                elif max_freq < 200:
                    track_type = "🥁 Có thể là BEAT (pitch < 200 Hz)"
        
        track_info.append({
            'idx': track_idx,
            'name': track_name,
            'type': track_type,
            'note_count': note_count,
            'min_freq': min(note_range) if note_range else 0,
            'max_freq': max(note_range) if note_range else 0
        })
        
        print(f"Track {track_idx + 1}: {track_type}")
        print(f"   Tên: {track_name}")
        print(f"   Số note: {note_count}")
        if note_range:
            print(f"   Pitch range: {min(note_range):.1f} - {max(note_range):.1f} Hz")
        print()
    
    # Tổng kết
    print("=" * 70)
    print("📋 Tổng kết:")
    
    vocal_tracks = [t for t in track_info if 'VOCAL' in t['type']]
    beat_tracks = [t for t in track_info if 'BEAT' in t['type']]
    other_tracks = [t for t in track_info if 'VOCAL' not in t['type'] and 'BEAT' not in t['type']]
    
    print(f"   🎤 Track VOCAL: {len(vocal_tracks)}")
    for t in vocal_tracks:
        print(f"      - Track {t['idx'] + 1}: {t['name']}")
    
    print(f"   🥁 Track BEAT: {len(beat_tracks)}")
    for t in beat_tracks:
        print(f"      - Track {t['idx'] + 1}: {t['name']}")
    
    print(f"   ❓ Track khác: {len(other_tracks)}")
    for t in other_tracks:
        print(f"      - Track {t['idx'] + 1}: {t['name']} ({t['note_count']} notes)")
    
    print()
    print("💡 Gợi ý:")
    if len(vocal_tracks) > 0:
        print("   ✅ File MIDI có track vocal - hệ thống sẽ tự động lọc khi dùng --midi-track auto")
    elif len(track_info) > 1:
        print("   ⚠️  File MIDI có nhiều track nhưng không rõ track nào là vocal")
        print("   💡 Nên kiểm tra và chỉ định track cụ thể hoặc dùng --midi-pitch-range 80 2000")
    else:
        print("   ✅ File MIDI chỉ có 1 track - sẽ lấy tất cả")


def main():
    parser = argparse.ArgumentParser(
        description='Kiểm tra và hiển thị thông tin các track trong file MIDI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('midi_file', help='Đường dẫn file MIDI cần kiểm tra')
    
    args = parser.parse_args()
    
    inspect_midi(args.midi_file)


if __name__ == '__main__':
    main()

