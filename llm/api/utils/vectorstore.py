from langchain_postgres import PGVector

from api.utils.embeddings import EMBEDDINGS
from api.database.database import async_engine
from langchain_core.documents import Document

def create_vectorstore(collection_name: str) -> PGVector:
    return PGVector(
        EMBEDDINGS, 
        connection=async_engine, 
        collection_name=collection_name,
        use_jsonb=True,
        async_mode=True,
        collection_metadata={
            "hnsw:space": "cosine"
        }
    )

async def load_documents(vectorstore: PGVector, documents: list[Document]):
    await vectorstore.aadd_documents(documents)

async def query_vectorstore(
    vectorstore: PGVector, 
    query: str
) -> list[Document]:
    retriever = vectorstore.as_retriever()
    return await retriever.ainvoke(query)