import os
import whisper
import ssl
import io
import asyncio
import torch

from tempfile import NamedTemporaryFile
from transformers import pipeline

ssl._create_default_https_context = ssl._create_unverified_context

device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
tonality_pipe = pipeline("text-classification", model="tabularisai/multilingual-sentiment-analysis", device=device)

stt_model = whisper.load_model("medium")

async def get_tonality(text: str) -> str:
    result = tonality_pipe(text)

    return result[0]["label"]


async def speech_to_text(audio_buffer: io.BytesIO) -> str:
    with NamedTemporaryFile(delete=False, suffix=".oga") as temp_file:
        temp_file.write(audio_buffer.read())
        temp_file_path = temp_file.name

    result = await asyncio.to_thread(stt_model.transcribe, audio=temp_file_path)

    os.unlink(temp_file_path)

    return result["text"]
