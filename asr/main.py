from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    from api.routes import asr_router, auth_router
    app.include_router(asr_router)
    app.include_router(auth_router)
    yield

# Initialize FastAPI app
app = FastAPI(
    title="Whisper ASR API",
    description="API for converting audio to text using OpenAI Whisper",
    version="1.0.0",
    lifespan=lifespan,
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)