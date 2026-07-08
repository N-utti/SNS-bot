"""네트워크/DB 없이 도는 스모크 테스트 — 모델 계약(ERD)을 고정한다.

CI 의 `test` 잡은 DB 없이 이걸 돌려 green 을 확보한다. DB 통합/동시성
테스트(테스트 게이트 5종)는 M1 진행 중 pg 잡에서 추가된다.
"""
from app import models


def test_table_names():
    assert models.MatchedPost._meta.db_table == "matched_posts"
    assert models.SnsAccountSecret._meta.db_table == "sns_account_secrets"
    assert models.ReplyActionLog._meta.db_table == "reply_actions"


def test_post_status_has_sending_state():
    # 이중발송 CAS 의 중간 상태(MUST-FIX #1) 가 존재해야 한다.
    assert models.PostStatus.sending.value == "sending"


def test_reply_action_sent_value():
    # partial unique index 가 거는 값과 일치해야 한다.
    assert models.ReplyAction.sent.value == "sent"


def test_secret_is_separate_model():
    # 자격증명은 sns_accounts 가 아닌 별도 모델에 있어야 한다(MUST-FIX #3).
    account_fields = set(models.SnsAccount._meta.fields_map.keys())
    assert "encrypted_credentials" not in account_fields
