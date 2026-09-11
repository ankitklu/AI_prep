import whisper
import os

WHISPER_MODEL = os.getenv("WHISPER_MODEL","small")

_model = None

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

