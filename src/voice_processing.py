import os
import whisper
import ssl
import io
import asyncio

from tempfile import NamedTemporaryFile

model = whisper.load_model("medium")

async def speech_to_text(audio_buffer: io.BytesIO) -> str:
    ssl._create_default_https_context = ssl._create_unverified_context

    with NamedTemporaryFile(delete=False, suffix=".oga") as temp_file:
        temp_file.write(audio_buffer.read())
        temp_file_path = temp_file.name

    result = await asyncio.to_thread(model.transcribe, audio=temp_file_path)

    os.unlink(temp_file_path)

    return result["text"]
