from dotenv import load_dotenv
from openai import OpenAI
import os


# 创建LLM客户端
def get_client() -> OpenAI:
    load_dotenv()
    api_key = os.environ.get("DEEPSEEK_API_KEY")

    if not api_key:
        raise ValueError("缺少 DEEPSEEK_API_KEY")

    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


# 首次调用API（验证是否打通LLM）
def ask(prompt: str) -> str:
    client = get_client()

    response = client.chat.completions.create(
        model="deepseek-v4-pro", 
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content or ""


# TODO：流式输出
def ask_stream(prompt: str):
    client = get_client()

    stream = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def testPDF() -> str:
    client = get_client()

    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[{"role": "user", "content": "用三句话概括这份简历"}],
    )

    print(response)

    return ""


if __name__ == "__main__":
    testPDF()
