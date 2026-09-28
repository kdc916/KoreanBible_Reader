# KoreanBible Reader v0.3.5 — GitHub Ready

이 저장소는 GitHub Actions가 배포 시 개역한글 1961 전체 본문을 `index.html` 안에 직접 삽입하는 구조입니다.

## 저장소에 필요한 파일

```text
/
├─ index.html
├─ README.md
├─ UPLOAD_CHECKLIST.md
├─ VERIFY_DEPLOYMENT.md
├─ WORKFLOW_COPY.txt
├─ tools/
│  └─ build_embedded.py
└─ .github/
   └─ workflows/
      └─ deploy-pages.yml
```

성경 JSON을 이 저장소에 직접 올릴 필요는 없습니다.

GitHub Actions가 공개 데이터 저장소
`bluesaurel/Korean-Bible-1961-KRV`
를 별도로 Checkout한 뒤 `bible_1961_krv.json`을 사용합니다.

## 빌드 검증

배포 전에 반드시 아래 값과 정확히 일치해야 합니다.

- 66권
- 1,189장
- 31,102절

다르면 빌드가 실패하며 Pages에 배포되지 않습니다.

## 최종 배포본

Actions가 생성하는:

`dist/index.html`

에는 성경 본문 전체가 직접 들어 있습니다.

따라서 정상 배포 시 브라우저에서:
- 성경 복구 대기
- CORS 프록시
- JSONP
- 66권 분할 복구

가 필요하지 않습니다.

## Pages 설정

Repository → Settings → Pages → Build and deployment

Source:

`GitHub Actions`

로 설정합니다.
