from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    db_host: str
    db_port: int = 3306
    db_user: str
    db_password: str
    db_name: str
    db_pool_size: int = 5

    # Bale
    bale_token: str

    # App
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
