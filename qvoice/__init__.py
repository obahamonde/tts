import io
from typing import Literal, TypeAlias

import aiofiles
import numpy as np  # type: ignore
import pytube  # pylint: disable=E0401  # type: ignore
import scipy.io.wavfile as wavfile  # type: ignore
from cachetools import (  # type: ignore # pylint: disable=import-error
    LRUCache, cached)
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydub import AudioSegment  # type: ignore # pylint: disable=E0401
# from pydub import AudioSegment  # type: ignore
from TTS.api import TTS  # type: ignore

cache = LRUCache(maxsize=1)  # type: ignore
Lang: TypeAlias = Literal["en", "es"]
Gender: TypeAlias = Literal["female", "male"]


@cached(cache)  # type: ignore
def load_model():
    return TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")


tts = load_model()


def download_audio(url: str) -> io.BytesIO:
    yt = pytube.YouTube(url)
    stream = yt.streams.filter(only_audio=True).first()  # type: ignore
    audio_file = io.BytesIO()
    stream.stream_to_buffer(audio_file)  # type: ignore
    audio_file.seek(0)
    audio = AudioSegment.from_file(audio_file, format="mp4")  # type: ignore # pylint: disable=E0602
    wav_file = io.BytesIO()
    audio.export(wav_file, format="wav")  # type: ignore
    wav_file.seek(0)
    return wav_file


def generate_audio(text: str, lang: Lang, speaker_wav: str):
    output_audio = io.BytesIO()
    tts.tts_to_file(  # type: ignore
        text=text,
        file_path=output_audio,  # type: ignore
        speaker_wav=speaker_wav,
        split_sentences=True,
        emotion="cheerful",
        language=lang,
    )
    output_audio.seek(0)
    return output_audio


def create_app():
    app = FastAPI(
        title="QVoice",
        description="A simple API to generate voice from text",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/generate")
    def _(text: str, lang: Lang, gender: Gender = "female"):
        return StreamingResponse(
            generate_audio(text, lang, f"/app/samples/{gender}_{lang}.wav"),
            media_type="audio/wav",
        )

    @app.post("/generate")
    async def _(text: str, lang: Lang, name: str, file: UploadFile = File(...)):
        raw_audio = await file.read()
        async with aiofiles.open(f"/app/samples/{name}.wav", "wb") as f:
            await f.write(raw_audio)

        stream = io.BytesIO()

        tts.tts_to_file(  # type: ignore
            text=text,
            file_path=stream,  # type: ignore
            speaker_wav=f"/app/samples/{name}.wav",
            split_sentences=True,
            emotion="cheerful",
            language=lang,
        )

        stream.seek(0)

        return StreamingResponse(
            stream,
            media_type="audio/wav",
            headers={"Content-Disposition": f'attachment; filename="{name}.wav"'},
        )

    return app
