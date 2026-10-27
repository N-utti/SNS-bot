# SNS-bot — 초기 스캐폴드

> 이 저장소는 2026-07-08 의 초기 스캐폴드(PRD · ERD · API 명세 · 분담표)다.
> **구현은 [wjdtjddns98/auto-comment-bot](https://github.com/wjdtjddns98/auto-comment-bot) 로 이어졌다** — 소스 어댑터, 정확히 한 번 발송, 토큰 암호화, Meta 앱 검수까지 거기에 있다.
>
> 포트폴리오: [AX(AI 활용)](https://wjdtjddns98.github.io/) · [개발자](https://wjdtjddns98.github.io/dev/)

지정한 키워드가 들어간 SNS·커뮤니티 글을 모아 대시보드에 띄우고, **사람이 승인한 답글만** 보내는 소셜 리스닝 도구. 자동 댓글 봇이 아니다.

- `docs/PRD.md` — 제품 정의와 불변 제약(자동 게시 금지 · 이중 발송 금지 · 자격증명 노출 금지 · 예의 있는 수집)
- `docs/ERD.md` · `docs/API-SPEC.md` — 데이터 모델과 FE↔BE 계약
- `docs/OWNERSHIP.md` — 2인(백엔드 정성운 / 프론트 진수연) 분담표
