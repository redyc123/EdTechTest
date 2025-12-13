from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from dotenv import load_dotenv
from langchain_core.globals import set_debug, set_verbose

set_debug(True)
set_verbose(True)

load_dotenv(".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    from api.routers.chat import chat_router
    from common.auth.router import auth_router
    from api.routers.vectorstore import vectorstore_router
    app.include_router(chat_router)
    app.include_router(auth_router)
    app.include_router(vectorstore_router)
    yield

app = FastAPI(
    title="LLM Сервис",
    description="Сервис для обработки текстовых и аудиозапросов с использованием языковых моделей",
    version="1.0.0",
    docs_url="/docs",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    lifespan=lifespan
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)