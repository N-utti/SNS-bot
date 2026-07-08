from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # postgres 접속 (docker-compose에서 주입)
    database_url: str = "postgres://sns:sns@db:5432/sns"
    app_env: str = "dev"

    # ponytail: Fernet 키/외부 API 토큰은 sns_accounts 모델이 생기는 M1에서 추가.
    #           지금 넣으면 미사용 설정 = YAGNI.


settings = Settings()
