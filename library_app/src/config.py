from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl

from typing import List, Optional, Union
import secrets

from pydantic import PydanticUserError, create_model

try:
    create_model('FooModel', foo=(str, 'default value', 'more'))
except PydanticUserError as exc_info:
    assert exc_info.code == 'create-model-field-definitions'

class Settings(BaseSettings):
    PROJECT_NAME: str = "Library Management System"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 jours

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Base de données
    DATABASE_URL: str = "sqlite:///./library.db"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()