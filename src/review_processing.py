from transformers import pipeline

process = pipeline("text-classification", model="tabularisai/multilingual-sentiment-analysis", device="mps")

async def get_tonality(text: str) -> str:
    result = process(text)

    return result[0]["label"]

