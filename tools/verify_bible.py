#!/usr/bin/env python3
import json
from pathlib import Path

p=Path("bible_1961_krv.json")
if not p.exists():
    raise SystemExit("bible_1961_krv.json 파일이 저장소 루트에 없습니다.")

raw=json.loads(p.read_text(encoding="utf-8"))

if isinstance(raw,list):
    books=raw
elif isinstance(raw,dict):
    books=raw.get("books") or raw.get("bible") or raw.get("data") or []
else:
    books=[]

chapters=sum(len(b.get("chapters",[])) for b in books)
entries=sum(len(c.get("verses",[])) for b in books for c in b.get("chapters",[]))
readable=sum(
    1 for b in books for c in b.get("chapters",[]) for v in c.get("verses",[])
    if str(v.get("text",v.get("hangulText",v.get("content","")))).strip()
    and str(v.get("text",v.get("hangulText",v.get("content","")))).strip()!="(없음)"
)

print("books:",len(books))
print("chapters:",chapters)
print("verse entries:",entries)
print("readable verse texts:",readable)

expected=(66,1189,31102)
actual=(len(books),chapters,entries)
if actual!=expected:
    raise SystemExit(f"구조 검증 실패: expected={expected}, actual={actual}")

print("OK: 66권 / 1,189장 / 31,102 절 위치 구조")
