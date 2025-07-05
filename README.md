## 📢 Simple Concatenative Text-to-Speech (TTS) For Emergency 🚨✨
This project demonstrates a basic concatenative Text-to-Speech (TTS) system using pre-recorded word units. It includes utilities for dataset preparation, verification, and a simple command-line interface for synthesizing and playing audio.

### 🔎Features
  * **Concatenative TTS:** Synthesizes speech by concatenating pre-recorded individual word audio clips.
  * **Dataset Preparation:**
      * Resamples audio to 16 kHz and converts to mono.
      * Splits datasets into training and testing sets based on a configurable ratio.
      * Automatically creates `.lab` files for each `.wav` file, storing its label (word).
  * **Dataset Verification:** Checks if WAV files are at the required sample rate (16 kHz) and mono, and verifies the presence of corresponding `.lab` files.
  * **FFmpeg Integration:** Utilizes FFmpeg for robust audio processing and playback.
  * **Python-based:** Built entirely using Python and popular audio processing libraries.

-----
## 🚧Prerequisites
Before you begin, ensure you have the following installed:
1.  **Python 3.x**
2.  **FFmpeg:** This is crucial for audio processing and playback.
      * Download FFmpeg from their [official website](https://ffmpeg.org/download.html).
      * **Extract FFmpeg** to a directory on your system (e.g., `D:\ffmpeg_essentials_build\bin` as seen in the code).
      * **Crucially, update the `BIN_PATH` variable** in `mainTTS.py` to point to the `bin` folder within your FFmpeg installation (e.g., `BIN_PATH = r"C:\path\to\your\ffmpeg\bin"`).

-----
## 🎯Installation
1.  **Clone the repository** (or download the files):
    ```bash
    git clone https://github.com/talithsa/Simple-Concatenative-TTS.git
    cd Simple-Concatenative-TTS   # Navigate to your project directory
    ```
2.  **Create a Virtual Environment (recommended):**
    ```bash
    python -m venv venv
    venv\Scripts\activate      # For Windows
    source venv/bin/activate   # For macOS/Linux
    ```
3.  **Install Required Python Libraries:**
    ```bash
    pip install pydub numpy librosa soundfile
    ```

-----
### ⏳Usage
This project offers a command-line interface for its functionalities.

### 1\. Prepare/Convert Dataset
Use `data.py` to process your raw `.wav` files (resample, convert to mono, and split into train/test sets).
1.  Place your raw WAV files into a source folder, organized by labels (e.g., `input_raw_data/ambulans/ambulans_01.wav`).
2.  Run `data.py`:
    ```bash
    python data.py
    ```
3.  Select option `1. Split + Convert`.
4.  Follow the prompts to enter:
      * `Path folder sumber (per label)`: The root path to your raw audio folders (e.g., `input_raw_data`).
      * `Path folder output`: The desired output path for the processed dataset (e.g., `data_processed`).
      * `Persentase training (cth 80)`: The percentage of data to use for the training set (e.g., `80`).
  
### 2\. Verify Dataset
Use `data.py` to verify the structure and properties of your processed dataset.
1.  Run `data.py`:
    ```bash
    python data.py
    ```
2.  Select option `2. Verify`.
3.  Enter the `Path dataset` (e.g., `data_processed`). The script will check sample rates, mono conversion, and `wav`/`lab` file consistency.
   
### 3\. Synthesize Speech
Use `TTS_concatenative.py` to synthesize speech from concatenated word units
1.  **Ensure `data_processed/train/wav` contains your processed audio files**, correctly categorized in subfolders by word.
2.  **Verify `BIN_PATH` in `mainTTS.py` is correct** and points to your FFmpeg `bin` directory.
3.  Run the synthesis script:
    ```bash
    python TTS_concatenative.py
    ```
4.  Follow the prompts to `Masukkan teks` (Enter text). Type words separated by spaces.
5.  The synthesized audio will be played (using `ffplay`) and saved in the `output/` directory along with metadata.
6.  Type `keluar` to exit.

### 4\. (Optional) Generate Dummy Samples
If you want to quickly test the `TTS_concatenative.py` script without a full dataset, you can generate dummy `.wav` files using `testbeep.py`. These files are simple beeps, labeled with the `AVAILABLE_WORDS`.
1.  Run `testbeep.py`:
    ```bash
    python testbeep.py
    ```
    This will create dummy `.wav` files inside `train/<word_label>/` folders.
2.  **Note:** After running `testbeep.py`, you might need to adjust `DATA_PATH` in `mainTTS.py` if the `train` folder is not directly under `data_processed`. For instance, if `testbeep.py` created `train/ambulans/`, you might set `DATA_PATH = "train"`. For the best workflow, `data.py` should be used to prepare your actual dataset into `data_processed/train/wav`.

-----
### 🔡Available Words
The current dictionary of words that the TTS system can synthesize is:
  * `ambulans`
  * `bahaya`
  * `bencana`
  * `cepat`
  * `darurat`
  * `evakuasi`
  * `gawat`
  * `hati-hati`
  * `mendesak`
  * `tolong`

-----
### 📌Configuration
You can modify these variables in the respective Python files:
  * `REQUIRED_SAMPLE_RATE` in `data.py`: Target sample rate for processed audio (default: 16000 Hz).
  * `BIN_PATH` in `mainTTS.py`: Path to your FFmpeg `bin` directory. **(Crucial)**
  * `DATA_PATH` in `mainTTS.py`: Root folder containing the processed `.wav` files for synthesis (default: `data_processed/train/wav`).
  * `OUTPUT_DIR` in `mainTTS.py`: Directory where synthesized audio will be saved (default: `output`).
  * `WORD_PAUSE_MS` in `mainTTS.py`: Pause duration between concatenated words in milliseconds (default: 150 ms).
  * `WORDS` in `testbeep.py`: List of words for which dummy samples are generated.
  * `AVAILABLE_WORDS` in `mainTTS.py`: The dictionary of words the TTS can pronounce. This should ideally match the words in your `data_processed` folder.
-----

*Notes: This project was not created by me individually, but was created together with two of my colleagues for a Introduction to Speech and Text-to-Speech Course.*
