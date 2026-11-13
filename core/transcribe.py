import whisper
import os
from dotenv import load_dotenv
from pydub import AudioSegment
from sarvamai import SarvamAI
import io

load_dotenv()

WHISPER_MODEL = os.getenv("WHISPER_MODEL","small")
SARVAM_CHUNK_DURATION_SEC = 25

_model = None

def load_model():
    global _model

    if _model is None:
        print("Loading whisper model ....")
        _model = whisper.load_model(WHISPER_MODEL)
        print("Whisper model loaded successfully")

    return _model

def transcribe_chunk_whisper(chunk_path:str, translate:bool = False) -> str:
    print("Using Whisper model for transcription....")
    model = load_model()
    task = "translate" if translate else "transcribe"
    
    result = model.transcribe(chunk_path, task=task)
    return result['text']

def transcribe_chunk_sarvam(chunk_path: str, translate: bool = False,
                            chunk_duration_sec: int = SARVAM_CHUNK_DURATION_SEC) -> str:
    client = SarvamAI(api_subscription_key=os.getenv("SARVAM_API_KEY"))
    model = os.getenv("SARVAM_MODEL", "saaras:v4")
    mode = "translate" if translate else "transcribe"

    audio = AudioSegment.from_file(chunk_path)
    step = chunk_duration_sec * 1000
    texts = []

    for i, start in enumerate(range(0, len(audio), step), 1):
        piece = audio[start:start + step]
        if len(piece) < 200:  # skip tiny tail clips
            continue

        print(f"Sarvam sub-chunk {i} ({len(piece)/1000:.1f}s)...")
        buf = io.BytesIO()
        piece.export(buf, format="wav")
        buf.name = "chunk.wav"  # some SDKs need a filename on the upload

        resp = client.speech_to_text.transcribe(file=buf, model=model, mode=mode)
        text = (getattr(resp, "transcript", "") or "").strip()
        if text:
            texts.append(text)

    return " ".join(texts)

def transcribe_chunk(chunk_path:str, translate:bool = False, language:str = "english") -> str:
    if language.lower() == "hinglish":
        return transcribe_chunk_sarvam(chunk_path, translate)
    else:
        return transcribe_chunk_whisper(chunk_path, translate)

def transcribe_all(chunks:list, translate:bool = False, language:str = "english") -> str:
    full_text = []
    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i+1}/{len(chunks)}....")
        text = transcribe_chunk(chunk, translate, language)
        full_text.append(text)

    print("Transcription completed")
    return "\n\n".join(full_text)