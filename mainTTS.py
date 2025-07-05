# ──────────────────────────────────────────────────────────────
#   Concatenative TTS Demo — random‑word unit selection
#   (Fixed, Refactored, and Ready for Forced Alignment Data)
# ──────────────────────────────────────────────────────────────
import os
import random
import time
import subprocess
import warnings
from datetime import datetime
from typing import Optional
import tempfile

# ── 0. KONFIGURASI PATH FFmpeg ────────────────────────────────
# Pastikan path ini sesuai dengan lokasi instalasi ffmpeg di sistem Anda.
BIN_PATH = r"D:\ffmpeg_essentials_build\bin"

# Cek apakah direktori BIN_PATH ada
if not os.path.isdir(BIN_PATH):
    raise FileNotFoundError(
        f"Direktori FFmpeg tidak ditemukan di: '{BIN_PATH}'. "
        "Silakan perbarui variabel BIN_PATH dengan lokasi yang benar."
    )

FFMPEG_EXE = os.path.join(BIN_PATH, "ffmpeg.exe")
FFPROBE_EXE = os.path.join(BIN_PATH, "ffprobe.exe")
FFPLAY_EXE = os.path.join(BIN_PATH, "ffplay.exe")

# Tambahkan bin path ke environment variable agar pydub dapat menemukannya
os.environ["PATH"] += os.pathsep + BIN_PATH

# Filter warning dari pydub jika diperlukan
warnings.filterwarnings("ignore", message="Couldn't find ffprobe or avprobe")

# ── 1. IMPORT PYDUB SETELAH ENV SIAP ──────────────────────────
try:
    from pydub import AudioSegment
    # Arahkan pydub secara eksplisit untuk menggunakan binary yang sudah kita tentukan
    AudioSegment.converter = FFMPEG_EXE
    AudioSegment.ffprobe = FFPROBE_EXE
except ImportError:
    print("Error: Pydub tidak terinstal. Silakan instal dengan 'pip install pydub'")
    exit()

# ── 2. LOKASI DATA & PARAMETER ────────────────────────────────
DATA_PATH = "data_processed/train/wav"      # <─ Folder berisi rekaman kata per sub-folder
OUTPUT_DIR = "output"                       # <─ Hasil sintesis akan disimpan di sini
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Daftar kata yang tersedia dalam dataset
AVAILABLE_WORDS = [
    "ambulans", "bahaya", "bencana", "cepat", "darurat",
    "evakuasi", "gawat", "hati-hati", "mendesak", "tolong",
]
WORD_PAUSE_MS = 150  # Jeda antar kata dalam milidetik

# ── 3. FUNGSI UTILITAS ─────────────────────────────────────────
def find_random_sample(word: str) -> Optional[str]:
    """Mengambil satu path file WAV secara acak untuk kata tertentu."""
    folder = os.path.join(DATA_PATH, word)
    if not os.path.isdir(folder):
        print(f"[!] Folder tidak ditemukan: {folder}")
        return None
    
    wavs = [f for f in os.listdir(folder) if f.lower().endswith(".wav")]
    if not wavs:
        print(f"[!] Tidak ada file .wav di folder: {folder}")
        return None
        
    return os.path.join(folder, random.choice(wavs))

def play_audio_with_ffplay(audio_segment: AudioSegment) -> None:
    """
    Memutar AudioSegment menggunakan ffplay untuk playback yang lebih andal.
    Ini menghindari masalah dependensi cross-platform dari simpleaudio/pyaudio.
    """
    print("🔊 Memutar audio...")
    # Ekspor ke file sementara dalam format WAV dan mainkan
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_filename = f.name
    
    try:
        audio_segment.export(temp_filename, format="wav")
        # Gunakan subprocess untuk memanggil ffplay
        # -nodisp: jangan tampilkan jendela video
        # -autoexit: tutup setelah selesai
        # -loglevel quiet: sembunyikan log teknis dari ffplay
        subprocess.run(
            [FFPLAY_EXE, "-nodisp", "-autoexit", "-loglevel", "quiet", temp_filename],
            check=True
        )
    except FileNotFoundError:
        print(f"‼️  Error: 'ffplay.exe' tidak ditemukan di '{FFPLAY_EXE}'.")
        print("    Pastikan path FFmpeg Anda sudah benar.")
    except Exception as e:
        print(f"‼️  Gagal memutar audio dengan ffplay: {e}")
    finally:
        # Hapus file sementara setelah selesai
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

# ── 4. FUNGSI UTAMA SINTESIS ────────────────────────────────────
def speak_concatenative(text_input: str) -> None:
    """
    Membuat dan memutar audio dari gabungan klip kata.
    Menyimpan hasil audio dan metadata.
    """
    words = text_input.lower().strip().split()
    if not words:
        print("⚠️  Input kosong. Tidak ada yang perlu disintesis.")
        return

    segments = []
    used_paths = []  # Lacak path file yang digunakan untuk metadata

    print("\n🔄 Memproses kata:")
    for w in words:
        if w not in AVAILABLE_WORDS:
            print(f"🚫 Kata '{w}' tidak tersedia dalam kamus. Dilewati.")
            continue

        file_path = find_random_sample(w)
        if not file_path:
            print(f"🚫 Sampel untuk '{w}' tidak dapat ditemukan. Dilewati.")
            continue

        try:
            # memuat file audio utuh
            word_segment = AudioSegment.from_wav(file_path)
            segments.append(word_segment)
            used_paths.append(file_path)
            print(f"  ✓ {w:<10} ← {os.path.basename(file_path):<25} ({len(word_segment):>4} ms)")
        except Exception as e:
            print(f"‼️  Gagal memuat atau memproses file '{file_path}': {e}")

    if not segments:
        print("\n⚠️  Tidak ada kata yang valid untuk diproses. Operasi dibatalkan.")
        return

    # Gabungkan segmen audio dengan jeda menggunakan operator '+'
    silence = AudioSegment.silent(duration=WORD_PAUSE_MS)
    utterance = segments[0]
    for seg in segments[1:]:
        utterance += silence + seg

    # ── 4a. SIMPAN HASIL (Audio + Metadata) ───────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_text = "_".join(words)[:40].replace(os.path.sep, "-")
    
    wav_output_path = os.path.join(OUTPUT_DIR, f"{timestamp}_{safe_text}.wav")
    txt_output_path = os.path.join(OUTPUT_DIR, f"{timestamp}_{safe_text}.txt")

    try:
        utterance.export(wav_output_path, format="wav")
        with open(txt_output_path, "w", encoding="utf-8") as f:
            f.write(f"Input Teks: {' '.join(words)}\n")
            f.write("="*20 + "\n")
            f.write("Klip Audio yang Digunakan:\n")
            for path in used_paths:
                f.write(f"  - {path}\n")
        
        print(f"\n💾 Rekaman gabungan disimpan di: {wav_output_path}")
        print(f"📝 Metadata disimpan di      : {txt_output_path}")

    except Exception as e:
        print(f"‼️ Gagal menyimpan file output: {e}")
        return

    # ── 4b. PUTAR AUDIO ───────────────────────────────────────
    play_audio_with_ffplay(utterance)
    
# ── 5. INTERAKSI VIA COMMAND LINE (CLI) ───────────────────────
if __name__ == "__main__":
    print("\n" + "="*50)
    print("      📢 Demo Random-Word Concatenative TTS 🚨")
    print("="*50)
    print("Ketik kata-kata yang tersedia, pisahkan dengan spasi.")
    print("Ketik 'keluar' atau tekan Ctrl+C untuk berhenti.")
    print("\nKamus Kata:", ", ".join(AVAILABLE_WORDS))

    while True:
        try:
            input_text = input("\n▶ Masukkan teks: ").strip()
            if input_text.lower() == 'keluar':
                break
            if input_text:
                speak_concatenative(input_text)
        except (EOFError, KeyboardInterrupt):
            break
    
    print("\n👋 Terima Kasih!")
