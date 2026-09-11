from utils.audio_processor import process_input
from core.transcriber import transcribe_all

source = "https://www.youtube.com/watch?v=BHGTA6ZEls4"

chunks = process_input(source=source)

print(transcribe_all(chunks))


