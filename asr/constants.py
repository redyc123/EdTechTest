import os
import whisper


MODEL = whisper.load_model("small")
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "my_secret_token")

