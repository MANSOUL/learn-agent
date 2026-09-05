import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            model=os.getenv("LLM_MODEL"),
            temperature=0.7,
        )
    return _llm