from langchain_huggingface import HuggingFaceEndpointEmbeddings
from config import config

EMBEDDINGS = HuggingFaceEndpointEmbeddings(model=config.embeddings)