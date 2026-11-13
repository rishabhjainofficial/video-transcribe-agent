import yt_dlp
import os
from pydub import AudioSegment

DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR,exist_ok=True)

def download_youtube_audio(url:str)->str:
    """Download Audio from Youtube as MP3 and return path"""
    try:
        output_path = os.path.join(DOWNLOAD_DIR,"%(title)s.%(ext)s")
        ydl_opts = {
            'format':'bestaudio/best',
            'outtmpl':output_path,
            'postprocessors':[{'key': 'FFmpegExtractAudio','preferredcodec':'wav','preferredquality':'192',}],
            'quite':True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url,download=True)
            filename = ydl.prepare_filename(info).replace('.webm','.wav').replace('.mp4','.wav').replace('.mkv','.wav')
            return filename
    except Exception as e:
        print(e)
        return None

def convert_to_wav(input_path:str) -> str:
    """Convert any audio/video file to wav format using pydub"""
    try:
        output_path = os.path.splitext(input_path)[0]+"_converted.wav"
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_channels(1).set_frame_rate(16000) #16khz
        audio.export(output_path,format="wav")
        return output_path
    except Exception as e:
        print(e)
        return None

def chunk_audio(wav_path:str, chunk_minutes: int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        end = start + chunk_ms
        chunk = audio[start:end]
        chunk_audio = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_audio,format="wav")
        chunks.append(chunk_audio)

    return chunks

def process_input(source:str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Processing YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Processing local file...")
        wav_path = convert_to_wav(source)
            
    
    if wav_path:
        print("Chunking audio...")
        chunks = chunk_audio(wav_path,10)
        print(f"Generated {len(chunks)} chunks from {wav_path}")
        return chunks

# data = download_youtube_audio("https://youtu.be/PoWXevbw-Uk?si=yOSpcShneqTAukz0")
# output_path = convert_to_wav(data)
# print(chunk_audio(output_path,chunk_minutes=5))

print(process_input("https://youtu.be/PoWXevbw-Uk?si=yOSpcShneqTAukz0"))