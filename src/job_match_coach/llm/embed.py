from openai import OpenAI
from dotenv import load_dotenv
import os

def embed(text: str) -> list[float]:
    load_dotenv()
    client = OpenAI(
        api_key=os.environ["DASHSCOPE_API_KEY"],
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    resp = client.embeddings.create(
        model="qwen3.7-text-embedding",
        input=text,
        dimensions=1024,
        encoding_format="float"
    )

    return resp.data[0].embedding