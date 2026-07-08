# ERD — 데이터 모델

> PRD 기반. Tortoise ORM + Postgres. 8개 테이블(핵심 7 + 자격증명 분리 1).
> 최종 갱신: 2026-07-08 · Status: pending approval

---

## 다이어그램

```mermaid
erDiagram
    users ||--o{ sns_accounts : owns
    users ||--o{ sources : owns
    users ||--o{ keywords : owns
    users ||--o{ reply_templates : owns
    users ||--o{ reply_actions : reviews
    sns_accounts ||--|| sns_account_secrets : "1:1 (분리 저장)"
    sns_accounts ||--o{ reply_actions : "sent via"
    sources ||--o{ matched_posts : produces
    sources ||--o{ keywords : "scope (nullable)"
    keywords ||--o{ matched_posts : matched_by
    matched_posts ||--o{ reply_actions : "attempts (audit)"
    reply_templates ||--o{ reply_actions : "used (nullable)"

    users {
        int id PK
        string email UK
        string password_hash
        string role "admin | reviewer"
        datetime created_at
    }
    sns_accounts {
        int id PK
        int user_id FK
        string platform "threads | naver | community"
        string display_name
        datetime token_expires_at "nullable"
        string status "active | expired | revoked"
        datetime created_at
    }
    sns_account_secrets {
        int sns_account_id PK "FK, 1:1"
        bytes encrypted_credentials "Fernet ciphertext"
        int key_version "MultiFernet 회전용"
        datetime updated_at
    }
    sources {
        int id PK
        int user_id FK
        string type "threads | naver_cafe | community"
        json config "cafe id / RSS url / 검색쿼리"
        int poll_interval_sec
        bool enabled
        datetime last_polled_at "nullable"
        datetime last_success_at "nullable, 백필 커서"
        string health_status "ok | degraded | down"
        datetime backoff_until "nullable"
        datetime created_at
    }
    keywords {
        int id PK
        int user_id FK
        string pattern
        string match_type "substring | regex"
        bool enabled
        int source_scope FK "nullable = 전체 소스"
        datetime created_at
    }
    matched_posts {
        int id PK
        int source_id FK
        string external_post_id "안정적 ID (FR-3)"
        string author
        string url
        text content
        string content_hash "편집 재매칭용"
        int matched_keyword_id FK
        datetime published_at "nullable, canonical 게시시각"
        datetime matched_at
        string status "new | reviewing | sending | replied | ignored"
        datetime sending_claimed_at "nullable, sweep 회수용"
    }
    reply_templates {
        int id PK
        int user_id FK
        string name
        text body "placeholder 지원"
        bool enabled
        datetime created_at
    }
    reply_actions {
        int id PK
        int matched_post_id FK
        int reviewer_user_id FK
        int template_id FK "nullable"
        text final_body
        string action "approved | sent | failed | canceled"
        int sns_account_id FK "nullable"
        string external_reply_id "nullable"
        string idempotency_key "nullable"
        text error "nullable"
        datetime created_at
    }
```

---

## 인덱스 & 제약 (핵심)

| 테이블 | 제약/인덱스 | 목적 |
|---|---|---|
| users | `UNIQUE(email)` | 로그인 식별 |
| sns_account_secrets | PK=`sns_account_id`, **read path 미로드** | 토큰 구조적 배제 (MUST-FIX #3) |
| sources | `INDEX(enabled, backoff_until)` | poller 픽업 대상 조회 |
| matched_posts | **`UNIQUE(source_id, external_post_id)`** | 인바운드 dedup (FR-2) |
| matched_posts | `INDEX(status)`, `INDEX(source_id, matched_at)` | 대시보드 필터 |
| reply_actions | **`UNIQUE(matched_post_id) WHERE action='sent'`** (partial) | 이중발송 구조적 차단 (MUST-FIX #1) |
| reply_actions | `INDEX(matched_post_id)` | 감사 조회 |

---

## 상태 전이 (matched_posts.status)

```
new ──(reviewer 열람)──▶ reviewing ──(승인 CAS)──▶ sending ──┬─(성공)─▶ replied
 │                          ▲                        │        └─(실패)─▶ reviewing (+failed reply_action, 수동 재시도)
 │                          └────(sweep, >N분 정체)──┘
 └──(무시)──▶ ignored
```

- **CAS 클레임 (MUST-FIX #1):** `UPDATE matched_posts SET status='sending', sending_claimed_at=now() WHERE id=$1 AND status IN ('new','reviewing') RETURNING id` — 0행이면 abort.
- **정체 회수 (MUST-FIX #4):** `sending_claimed_at` 초과 시 sweep이 `reviewing`으로 복귀.

---

## 설계 노트

- **자격증명 분리:** `sns_account_secrets`는 1:1 별도 테이블. 어떤 read 스키마도 이 테이블을 join/load하지 않으므로 직렬화기가 물리적으로 암호문에 접근 불가.
- **content_hash:** 편집된 글 재매칭(NICE-TO-HAVE). MVP는 저장만, 재매칭 로직은 후속.
- **published_at:** `external_post_id` 해시 입력의 canonical timestamp 출처(FR-3). null인 소스는 hash에서 timestamp 제외.
- **JSON config:** 소스 타입별 이질적 설정을 유연하게. 스키마는 어댑터가 검증.
