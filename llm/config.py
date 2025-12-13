from pydantic import Field, computed_field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

class SqlDbSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env"), env_prefix="db_", extra="ignore")

    scheme: str = Field("")
    user: str = Field("")
    password: str = Field("", alias="db_pass")
    host: str = Field("")
    port: int = Field(5432)
    name: str = Field("")

    @computed_field
    @property
    def url(self) -> URL:
        return URL.create(self.scheme, self.user, self.password, self.host, self.port, self.name, {})

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env"), extra="ignore")
    root_path: str = Field("")

    asr_url: str = Field("")
    secret_token: str = Field("")

    db_url: URL = SqlDbSettings().url # type: ignore

    openai_llm: dict = Field({})

    embeddings: str = Field("")

    docling_url: str = Field('')

    docling_serve_api_key: str = Field("")
    

config = Config() # type: ignore