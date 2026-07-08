# AGENTS — sns댓글봇 프로젝트 개요

## 파이프라인 (감지 → 승인 → 전송)

`poll(수집)` → `match(키워드)` → `dashboard(검토)` → `approve(사람 승인)` → `send/clipboard(전송)` → `audit(기록)`

- **poll** (`adapters/`): 소스별 주기 폴링. Threads=Meta API, 네이버 카페=검색 OpenAPI+RSS, 커뮤니티=RSS. `last_success_at` 커서로 백필.
- **match** (`matching.py`): substring/regex 매칭. 한국어 형태소(Kiwi)는 필요 시에만(CPU-bound → ProcessPoolExecutor).
- **dashboard/approve** (FastAPI 라우트 + `frontend/**`): 매칭 글 검토, 템플릿 편집, 승인.
- **send** (`adapters/`): `can_write=True`(Threads)만 자동 전송, 그 외는 클립보드 복사. CAS 로 이중발송 차단.
- **audit** (`reply_actions`, append-only): 누가/언제/무엇을 승인·전송했는지 불변 기록.

## Key Files (계획 — M1 구현)

- `app/config.py` — pydantic-settings, `DATABASE_URL`/`FERNET_KEY` 등 환경변수.
- `app/models/__init__.py` — Tortoise 모델(User/SnsAccount/SnsAccountSecret/Source/Keyword/MatchedPost/ReplyTemplate/ReplyActionLog) + enum.
- `app/db.py` — `TORTOISE_ORM` 설정(aerich 공용).
- `app/adapters/` — `SourceAdapter` ABC + Threads/Naver/Community 어댑터(`can_write` 플래그, `fetch()`/`send_reply()`).
- `app/crypto.py` — Fernet 암/복호화(자격증명), MultiFernet 회전 경로.

## 핵심 계약

- **자동 게시 없음.** 전송은 사람의 approve 클릭 뒤에만.
- **external_post_id 안정성.** 재폴링·URL 변형에도 동일 ID(canonical 게시시각 기반, 미노출 소스는 URL+author).
- **토큰 분리.** 자격증명은 `sns_account_secrets` 별도 테이블, read path 미로드.
- **테스트는 네트워크 없이.** 어댑터는 mock/fixture 로 테스트(실 API 호출 없음).

## 규칙

한국어 주석·docstring, Tortoise ORM, `docker compose` 기동, aerich forward-only 마이그레이션,
`ruff check .` + `pytest -q` green 후 커밋. 상세 규칙은 `CLAUDE.md`.
