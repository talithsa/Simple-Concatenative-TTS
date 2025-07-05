import os, shutil, random, librosa, soundfile as sf

REQUIRED_SAMPLE_RATE = 16000  # Hz

# ---------- UTIL ----------
def process_and_save_wav(src, dst):
    """Resample ke 16 kHz & mono, lalu simpan ke dst."""
    audio, sr0 = librosa.load(src, sr=None, mono=False)
    print(f"  ↳ {os.path.basename(src)} | {sr0} Hz {'stereo' if audio.ndim>1 else 'mono'}")
    if audio.ndim > 1:
        audio = librosa.to_mono(audio)
    if sr0 != REQUIRED_SAMPLE_RATE:
        audio = librosa.resample(audio, orig_sr=sr0, target_sr=REQUIRED_SAMPLE_RATE)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    sf.write(dst, audio, REQUIRED_SAMPLE_RATE)
    print(f"    ✅ saved → {REQUIRED_SAMPLE_RATE} Hz mono\n")

# ---------- DATASET BUILD ----------
def create_empty_structure(base):
    for split in ['train', 'test']:
        for sub in ['wav', 'lab']:
            os.makedirs(os.path.join(base, split, sub), exist_ok=True)

def split_and_create_tts_dataset():
    print("\n=== Split + Convert Dataset ===")
    src_root = input("Path folder sumber (per label): ").strip()
    out_root = input("Path folder output: ").strip()
    train_ratio = float(input("Persentase training (cth 80): ")) / 100.0

    # bersihin
    shutil.rmtree(os.path.join(out_root, 'train'), ignore_errors=True)
    shutil.rmtree(os.path.join(out_root, 'test'), ignore_errors=True)
    create_empty_structure(out_root)

    labels = [d for d in os.listdir(src_root) if os.path.isdir(os.path.join(src_root, d))]
    print(f"Label: {labels}")

    for label in labels:
        files = [f for f in os.listdir(os.path.join(src_root, label)) if f.endswith('.wav')]
        random.shuffle(files)
        cut = int(len(files) * train_ratio)
        sets = [('train', files[:cut]), ('test', files[cut:])]

        for split, subset in sets:
            for fname in subset:
                src = os.path.join(src_root, label, fname)
                dst_wav = os.path.join(out_root, split, 'wav', label, fname)
                dst_lab = os.path.join(out_root, split, 'lab', label,
                                       os.path.splitext(fname)[0] + '.lab')

                process_and_save_wav(src, dst_wav)

                os.makedirs(os.path.dirname(dst_lab), exist_ok=True)
                with open(dst_lab, 'w') as f: f.write(label)

        print(f"- {label}: {len(sets[0][1])} train, {len(sets[1][1])} test")

    print("\n✓ Dataset done!")

# ---------- VERIFY ----------
def verify_tts_dataset(base):
    print("\n=== Verifikasi Dataset ===")
    for split in ['train', 'test']:
        wav_root = os.path.join(base, split, 'wav')
        lab_root = os.path.join(base, split, 'lab')

        wav_rel = []
        for root, _, files in os.walk(wav_root):
            for f in files:
                if f.endswith('.wav'):
                    rel = os.path.relpath(os.path.join(root, f), wav_root)
                    wav_rel.append(rel)

        lab_rel = []
        for root, _, files in os.walk(lab_root):
            for f in files:
                if f.endswith('.lab'):
                    rel = os.path.relpath(os.path.join(root, f), lab_root)
                    lab_rel.append(rel.replace('.lab', '.wav'))

        wav_set, lab_set = set(wav_rel), set(lab_rel)

        print(f"\n--- {split.upper()} ---")
        for rel in sorted(wav_set):
            path = os.path.join(wav_root, rel)
            audio, sr = librosa.load(path, sr=None, mono=False)
            ch = 'stereo' if audio.ndim > 1 else 'mono'
            sr_ok = sr == REQUIRED_SAMPLE_RATE
            ch_ok = ch == 'mono'
            print(f"{rel:<40} | {sr} Hz {'OK' if sr_ok else 'WRONG'} | "
                  f"{ch:<6} {'OK' if ch_ok else 'WRONG'}")

        warn_wav = lab_set - wav_set
        warn_lab = wav_set - lab_set
        if warn_lab: print(f"⚠️  {len(warn_lab)} .wav tanpa .lab")
        if warn_wav: print(f"⚠️  {len(warn_wav)} .lab tanpa .wav")

# ---------- MAIN ----------
def main():
    while True:
        print("\n1. Split + Convert  2. Verify  3. Exit")
        c = input("Pilih: ").strip()
        if c == '1': split_and_create_tts_dataset()
        elif c == '2':
            p = input("Path dataset: ").strip()
            verify_tts_dataset(p)
        elif c == '3': break
        else: print("Salah input!")

if __name__ == "__main__":
    main()
