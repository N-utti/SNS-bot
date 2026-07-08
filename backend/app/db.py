from app.config import settings

# Tortoise + aerich 공용 설정. aerich는 pyproject.toml에서 이 dict를 가리킨다.
# app.models 는 지금 비어 있고(M1에서 채움), aerich.models 는 마이그레이션 이력 테이블.
TORTOISE_ORM = {
    "connections": {"default": settings.database_url},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
