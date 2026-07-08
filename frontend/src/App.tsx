import { useEffect, useState } from "react";

// 하네스 확인용 페이지: 백엔드 /health 를 프록시로 호출해 풀스택 연결을 눈으로 검증한다.
// 실제 대시보드/승인 UI 는 프론트 개발자가 M1 에서 구현한다(frontend/** 영역).
type Health = { status: string; db: string };

export default function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/health")
      .then((r) => r.json())
      .then(setHealth)
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <main style={{ fontFamily: "system-ui", padding: 24 }}>
      <h1>SNS 키워드 모니터</h1>
      <p>백엔드 헬스체크:</p>
      {error && <pre style={{ color: "crimson" }}>{error}</pre>}
      {health ? (
        <pre>{JSON.stringify(health, null, 2)}</pre>
      ) : (
        !error && <p>확인 중…</p>
      )}
    </main>
  );
}
