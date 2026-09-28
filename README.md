# KoreanBible Reader v0.3.7 — Static GitHub Pages

## 이번 버전은 GitHub Actions를 사용하지 않습니다.

저장소 루트에 딱 두 파일이 핵심입니다.

```text
index.html
bible_1961_krv.json
```

GitHub Pages가 같은 저장소의 JSON을 직접 읽습니다.

따라서:
- Actions build 없음
- workflow 없음
- CORS proxy 없음
- JSONP 없음
- 66권 분할 복구 없음

## 첫 방문
`bible_1961_krv.json` 약 6.44MB를 같은 origin에서 읽습니다.

검증 후 IndexedDB에 전체 본문을 저장하므로 이후 방문은 캐시를 먼저 사용합니다.

## 구조 검증 정책 수정

31,102는 **절 위치/엔트리 수**입니다.

이전 빌드 스크립트는 `(없음)` 또는 빈 본문을 제외한 검색 가능한 본문 수를
31,102와 비교해 잘못 실패했습니다.

v0.3.7에서는:
- 66권
- 1,189장
- 31,102 verse entries

를 구조 검증 기준으로 사용합니다.

검색 인덱스는 실제 읽을 수 있는 본문만 대상으로 별도 계산합니다.
