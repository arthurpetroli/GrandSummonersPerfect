from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Grand Summoners Companion API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"


settings = Settings()
