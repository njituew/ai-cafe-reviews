# import os
# import ssl
import io
# import asyncio
import torch
from pprint import pprint
# import ffmpeg

# import speech_recognition as sr
# from tempfile import NamedTemporaryFile
from transformers import pipeline
from langchain_groq import ChatGroq
from groq import Groq

from langchain.sql_database import SQLDatabase
from langchain_experimental.tools.python.tool import PythonREPLTool
from langgraph.prebuilt import create_react_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit

from config import load_config

app_config = load_config()


device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
tonality_pipe = pipeline("text-classification", model="tabularisai/multilingual-sentiment-analysis", device=device)
llm = ChatGroq(model="llama-3.3-70b-specdec", temperature=0)
recognize_client = Groq()
recognize_model = 'whisper-large-v3-turbo'
db = SQLDatabase.from_uri(app_config.database.replace('+aiosqlite', ''))
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

db_agent_model = create_react_agent(
    llm,
    toolkit.get_tools() + [PythonREPLTool()]
)


async def get_tonality(text: str) -> str:
    result = tonality_pipe(text)

    return result[0]["label"]


async def custom_query(query: str):
    result = db_agent_model.invoke({
    "messages": [{"role": "user", "content": query}]
    })

    pprint(result)
    return result["messages"][-1].content


async def speech_to_text(audio_buffer: io.BytesIO) -> str:
    translation = recognize_client.audio.transcriptions.create(
        file=('audio.ogg', audio_buffer.read()),
        model=recognize_model,
        response_format="verbose_json"
    )
    return translation.text