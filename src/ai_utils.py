import os
import whisper
import ssl
import io
import asyncio

from tempfile import NamedTemporaryFile
from transformers import pipeline

process = pipeline("text-classification", model="tabularisai/multilingual-sentiment-analysis")

async def get_tonality(text: str) -> str:
    result = process(text)

    return result[0]["label"]


ssl._create_default_https_context = ssl._create_unverified_context
model = whisper.load_model("medium")

async def speech_to_text(audio_buffer: io.BytesIO) -> str:
    with NamedTemporaryFile(delete=False, suffix=".oga") as temp_file:
        temp_file.write(audio_buffer.read())
        temp_file_path = temp_file.name

    result = await asyncio.to_thread(model.transcribe, audio=temp_file_path)

    os.unlink(temp_file_path)

    return result["text"]
