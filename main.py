from typing import Literal, TypeAlias
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  
from fastapi.responses import StreamingResponse
import pytube
from pydub import AudioSegment
from TTS.api import TTS
import io

Lang:TypeAlias = Literal["en","es"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
def download_audio(url: str) -> io.BytesIO:
    yt = pytube.YouTube(url)
    stream = yt.streams.filter(only_audio=True).first()
    audio_file = io.BytesIO()
    stream.stream_to_buffer(audio_file)
    audio_file.seek(0)
    audio = AudioSegment.from_file(audio_file, format="mp4")
    wav_file = io.BytesIO()
    audio.export(wav_file, format="wav")
    wav_file.seek(0)
    return wav_file

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")

def generate_audio(text: str, lang:Lang, speaker_wav: io.BytesIO) -> io.BytesIO:
    output_audio = io.BytesIO()
    tts.tts_to_file(
        text=text,
        file_path=output_audio,
        speaker_wav=speaker_wav,
        split_sentences=True,
        emotion="cheerful",
        language=lang,
    )
    output_audio.seek(0)
    return output_audio

@app.post("/generate")
async def generate(text: str, lang: Lang):
    generated_audio = generate_audio(text, lang, "./audio.wav")
    return StreamingResponse(generated_audio, media_type="audio/wav", headers={"Content-Disposition": "attachment; filename=generated_audio.wav"})
