from pydub import AudioSegment
import os
import subprocess

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# YouTube's frequent site changes mean yt-dlp needs to stay current, but recent
# yt-dlp releases require Python >= 3.10 while this project's main venv is
# pinned to Python 3.9 (torch/whisper/etc.). So yt-dlp runs from its own
# isolated Python 3.12 venv (.venv-ytdlp) via subprocess instead of being
# imported as a library here.
YTDLP_BIN = os.path.join(os.path.dirname(__file__), "..", ".venv-ytdlp", "bin", "yt-dlp")

def download_youtube_audio(url: str) -> str:
    output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    result = subprocess.run(
        [
            YTDLP_BIN,
            "--extract-audio",
            "--audio-format", "wav",
            "--audio-quality", "192",
            "-o", output_template,
            "--print", "after_move:filepath",
            "--quiet",
            "--no-warnings",
            url,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed for {url}:\n{result.stderr}")

    return result.stdout.strip().splitlines()[-1]

def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) #16khz
    audio.export(output_path, format="wav")
    return output_path

def chunk_audio(wav_path : str , chunk_minutes : int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000 

    chunks = []

    for i, start in enumerate(range(0,len(audio),chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path , format = "wav")

        chunks.append(chunk_path)
    
    return chunks

def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks

