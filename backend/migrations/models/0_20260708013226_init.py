from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password_hash" VARCHAR(255) NOT NULL,
    "role" VARCHAR(16) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "users"."role" IS 'admin: admin\nreviewer: reviewer';
CREATE TABLE IF NOT EXISTS "reply_templates" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "body" TEXT NOT NULL,
    "enabled" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "sns_accounts" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "platform" VARCHAR(16) NOT NULL,
    "display_name" VARCHAR(255) NOT NULL,
    "token_expires_at" TIMESTAMPTZ,
    "status" VARCHAR(16) NOT NULL  DEFAULT 'active',
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "sns_accounts"."platform" IS 'threads: threads\nnaver: naver\ncommunity: community';
COMMENT ON COLUMN "sns_accounts"."status" IS 'active: active\nexpired: expired\nrevoked: revoked';
CREATE TABLE IF NOT EXISTS "sns_account_secrets" (
    "encrypted_credentials" BYTEA NOT NULL,
    "key_version" INT NOT NULL  DEFAULT 1,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "account_id" INT NOT NULL  PRIMARY KEY REFERENCES "sns_accounts" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "sources" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "type" VARCHAR(16) NOT NULL,
    "config" JSONB NOT NULL,
    "poll_interval_sec" INT NOT NULL  DEFAULT 300,
    "enabled" BOOL NOT NULL  DEFAULT True,
    "last_polled_at" TIMESTAMPTZ,
    "last_success_at" TIMESTAMPTZ,
    "health_status" VARCHAR(16) NOT NULL  DEFAULT 'ok',
    "backoff_until" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_sources_enabled_8c6f99" ON "sources" ("enabled", "backoff_until");
COMMENT ON COLUMN "sources"."type" IS 'threads: threads\nnaver_cafe: naver_cafe\ncommunity: community';
COMMENT ON COLUMN "sources"."health_status" IS 'ok: ok\ndegraded: degraded\ndown: down';
CREATE TABLE IF NOT EXISTS "keywords" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "pattern" VARCHAR(512) NOT NULL,
    "match_type" VARCHAR(16) NOT NULL  DEFAULT 'substring',
    "enabled" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "source_scope_id" INT REFERENCES "sources" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "keywords"."match_type" IS 'substring: substring\nregex: regex';
CREATE TABLE IF NOT EXISTS "matched_posts" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "external_post_id" VARCHAR(512) NOT NULL,
    "author" VARCHAR(255),
    "url" VARCHAR(1024),
    "content" TEXT NOT NULL,
    "content_hash" VARCHAR(64),
    "published_at" TIMESTAMPTZ,
    "matched_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "status" VARCHAR(16) NOT NULL  DEFAULT 'new',
    "sending_claimed_at" TIMESTAMPTZ,
    "matched_keyword_id" INT REFERENCES "keywords" ("id") ON DELETE CASCADE,
    "source_id" INT NOT NULL REFERENCES "sources" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_matched_pos_source__be8e01" UNIQUE ("source_id", "external_post_id")
);
CREATE INDEX IF NOT EXISTS "idx_matched_pos_status_cdba4f" ON "matched_posts" ("status");
CREATE INDEX IF NOT EXISTS "idx_matched_pos_source__9a9727" ON "matched_posts" ("source_id", "matched_at");
COMMENT ON COLUMN "matched_posts"."status" IS 'new: new\nreviewing: reviewing\nsending: sending\nreplied: replied\nignored: ignored';
CREATE TABLE IF NOT EXISTS "reply_actions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "final_body" TEXT NOT NULL,
    "action" VARCHAR(16) NOT NULL,
    "external_reply_id" VARCHAR(512),
    "idempotency_key" VARCHAR(128),
    "error" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "matched_post_id" INT NOT NULL REFERENCES "matched_posts" ("id") ON DELETE CASCADE,
    "reviewer_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "sns_account_id" INT REFERENCES "sns_accounts" ("id") ON DELETE CASCADE,
    "template_id" INT REFERENCES "reply_templates" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_reply_actio_matched_73202a" ON "reply_actions" ("matched_post_id");
COMMENT ON COLUMN "reply_actions"."action" IS 'approved: approved\nsent: sent\nfailed: failed\ncanceled: canceled';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
