import io
import torch

from transformers import pipeline
from groq import Groq

from langchain.sql_database import SQLDatabase
from langchain_experimental.tools.python.tool import PythonREPLTool
from langgraph.prebuilt import create_react_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

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

def check_query(text: str) -> str:
    result = llm.invoke([
        SystemMessage(content="Тебе предоставлен текст. Если данный текст является запросом на получение данных из базы данных - отправь 'запрос.'. Если данный текст является запросом для построения графика - отправь 'график.'. Иначе - отправь 'отклонен.'."),
        HumanMessage(content=text)
    ])

    return result.content
# Тебе предоставлен текст. Если данный текст является запросом на получение данных из базы данных - отправь 'запрос.'. Если данный текст является запросом для построения графика - отправь 'график.'. Иначе - отправь 'отклонен.'.

async def custom_query(query: str):
    temp = check_query(query)

    if temp != "график." and temp != "запрос.":
        return "Запрос отклонен."

    result = db_agent_model.invoke({
        "messages": [
            {"role": "system", "content": "Ты - лучший помощник по базе данных. За любыми данными обращайся в данную тебе базу данных. Если запрос включает построение графика - не отправляй никакой текст в ответ, только строй график на основе данных из базы и сохраняй его в папку graphics, имя файла: graph.png. Если запрос не включает просьбу построения графика или получения данных из базы отвечай 'Запрос отклонен.'."}, # Если запрос не относится к базе данных или построению графика - отвечай: 'Запрос отклонен.'
            {"role": "user", "content": query}
        ]
    })

    if temp == "график.":
        return "graphics/graph.png"

    return result["messages"][-1].content


async def speech_to_text(audio_buffer: io.BytesIO) -> str:
    translation = recognize_client.audio.transcriptions.create(
        file=('audio.ogg', audio_buffer.read()),
        model=recognize_model,
        response_format="verbose_json"
    )
    return translation.text