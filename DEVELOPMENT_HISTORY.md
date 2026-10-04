# KoreanBible Reader — Development History & Handoff

## v0.3.11 — Private Modern Translation Mode

- 기본 공개 판본: 개역한글 1961
- 개인용 현대 판본 JSON import 추가
- 기본 이름: 개역개정
- 현대 판본 원문은 GitHub 저장소에 포함하지 않음
- 개인 판본 IndexedDB key: `bible-personal-v1`
- 개인 판본 metadata localStorage key: `krv-personal-bible-meta-v1`
- 66권 / 1,189장 / 31,102절 구조 검증
- 현대 판본은 개역한글 문구 fingerprint 검사를 적용하지 않음
- 선택한 개인 판본은 다음 접속 시 우선 자동 로드
- 개역한글 1961 ↔ 개인 판본 전환
- 개인 판본 삭제 시 사용자 형광펜/메모/태그/통독 기록 유지
- v0.3.10 장 선택 → 첫 절 이동 수정 유지
- Storage Schema 4 유지

### 저작권/배포 원칙
개역개정 등 저작권 보호 판본의 전체 본문은 공개 repository 또는 GitHub Pages 배포 파일에 포함하지 않는다.
사용자가 합법적으로 보유한 데이터만 브라우저 로컬 저장소에 import하는 구조를 사용한다.
