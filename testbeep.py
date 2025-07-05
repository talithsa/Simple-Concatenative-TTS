import os,sys
ffmpeg_bin = r"D:\ffmpeg_essentials_build\bin"
os.environ["PATH"] += os.pathsep + ffmpeg_bin
os.environ["FFMPEG_BINARY"] = os.path.join(ffmpeg_bin, "ffmpeg.exe")

import random
from pydub.generators import Sine
import warnings
warnings.filterwarnings("ignore", message="Couldn't find ffmpeg")

WORDS = ["ambulans","bahaya","bencana","cepat","darurat",
         "evakuasi","gawat","hati-hati","mendesak","tolong"]

for w in WORDS:
    folder = os.path.join("train", w)
    os.makedirs(folder, exist_ok=True) 
    beep = Sine(random.choice([440, 550, 660])).to_audio_segment(duration=500)
    path = os.path.join(folder, f"{w}_test.wav")
    beep.export(path, format="wav")
    print("✅  Added", path)
print("Semua kata berhasil dikasih sample dummy. Coba jalanin program utama lagi!")
