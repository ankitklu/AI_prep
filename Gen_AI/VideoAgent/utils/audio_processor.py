import yt_dlp 
from pydub import AudioSegment
import os

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format":"FFmpefExtractAudio",
        "outtmpl": output_path,
        "postprocessors":[
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec":"wav",
                "preferredquality": "192",
            }
        ],
        "quiete": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
    return filename

