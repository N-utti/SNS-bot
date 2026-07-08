from tortoise import BaseDBAsyncClient


# 이중발송 구조적 차단 (MUST-FIX #1): matched_post 당 action='sent' 최대 1건.
# Tortoise 선언으로는 partial index 를 못 만들어 raw SQL 로 추가한다.
async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE UNIQUE INDEX "uniq_reply_sent_per_post"
        ON "reply_actions" ("matched_post_id")
        WHERE "action" = 'sent';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "uniq_reply_sent_per_post";"""
