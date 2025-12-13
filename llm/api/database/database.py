import psycopg
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    async_sessionmaker
)
from config import config
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from langchain_postgres.chat_message_histories import PostgresChatMessageHistory

CONNECT_STRING = f"postgresql://{config.db_url.username}:{config.db_url.password}\
@{config.db_url.host}:\
{config.db_url.port}/{config.db_url.database}"

class Base(DeclarativeBase):
    pass

sync_engine = create_engine(
    config.db_url,
    pool_size=100,
    max_overflow=2,
    pool_recycle=300,
    pool_pre_ping=True,
    pool_use_lifo=True,
    connect_args={
        "connect_timeout": 600,
        "keepalives": 1,
        "keepalives_idle": 600,
        "keepalives_interval": 10,
        "keepalives_count": 60,
    },
)

async_engine = create_async_engine(
    config.db_url,
    pool_size=100,
    max_overflow=2,
    pool_recycle=300,
    pool_pre_ping=True,
    pool_use_lifo=True,
    connect_args={
        "connect_timeout": 600,
        "keepalives": 1,
        "keepalives_idle": 600,
        "keepalives_interval": 10,
        "keepalives_count": 60,
    },
)

db_session_local = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=async_engine, 
    expire_on_commit=False
)

connect = sync_engine.connect()
try:
    sync_connection = connect.connection
    sync_raw_psycopg_conn = sync_connection.driver_connection
    if sync_raw_psycopg_conn is not None:
        PostgresChatMessageHistory.create_tables(sync_raw_psycopg_conn, "chat_history")
finally:
    connect.close()
    
async def clear_chat_history(session_id: str):
    connection = await psycopg.AsyncConnection.connect(CONNECT_STRING)
    try:
        await PostgresChatMessageHistory(
            "chat_history", 
            session_id, 
            async_connection=connection
        ).aclear()
    finally:
        await connection.close()


async def get_chat_history(session_id: str):
    connection = await psycopg.AsyncConnection.connect(CONNECT_STRING)
    try:
        return await PostgresChatMessageHistory(
            "chat_history", 
            session_id, 
            async_connection=connection
        ).aget_messages()
    finally:
        await connection.close()

async def add_messages_to_chat_history(session_id: str, messages: list):
    connection = await psycopg.AsyncConnection.connect(CONNECT_STRING)
    chat_history = PostgresChatMessageHistory(
        "chat_history", 
        session_id, 
        async_connection=connection
    )
    await chat_history.aadd_messages(messages)
    await connection.close()