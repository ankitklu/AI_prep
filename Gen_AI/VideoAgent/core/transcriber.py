import whisper
import os
import requests
from pydub import AudioSegment

# Sarvam's sync STT-translate API rejects audio longer than 30s.
# We slice each chunk into 25s pieces (with a 5s safety margin) before sending.
SARVAM_PIECE_SECONDS = 25

WHISPER_MODEL = os.getenv("WHISPER_MODEL","small")

_model = None

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")



def load_model():
    global _model

    if _model is None:
        print("Loading model....")
        _model = whisper.load_model(WHISPER_MODEL)
        print("Whisper model loaded successfully")

    return _model

def transcribe_chunk(chunk_path: str, translate: bool = False) -> str:

    model = load_model()


    task = "translate" if translate else "transcribe"

    result = model.transcribe(chunk_path, task = task)

    return result['text']


def transcribe_all(chunks: list, translate : bool = False):

    full_transcript = ""

    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i+1} ")
        text = transcribe_chunk(chunk, translate=translate)

        full_transcript+= text+" "

    print("Transcription completed !!")

    return full_transcript

