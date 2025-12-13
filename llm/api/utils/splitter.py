from langchain_text_splitters import (
    RecursiveCharacterTextSplitter, 
    TextSplitter
)
import asyncio
from langchain_core.documents import Document

def create_splitter(
        chunk_size: int = 500, 
        chunk_overlap: int = 100
    ) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        separators=["\n", ". "],
        chunk_overlap=chunk_overlap, 
        chunk_size=chunk_size
    )

async def split_text(
        text: str, 
        splitter: TextSplitter, 
        source: str | None = None
    ) -> list[Document]:
    texts = await asyncio.to_thread(splitter.split_text, text)
    return [Document(t, metadata={"source": source}) for t in texts]