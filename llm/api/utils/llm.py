from langchain_openai import ChatOpenAI
from config import config

LLM = ChatOpenAI(
    **config.openai_llm,
)