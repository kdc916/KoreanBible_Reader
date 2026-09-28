#!/usr/bin/env python3
import json
from pathlib import Path

BOOKS = [
("Genesis","창세기",50),("Exodus","출애굽기",40),("Leviticus","레위기",27),
("Numbers","민수기",36),("Deuteronomy","신명기",34),("Joshua","여호수아",24),
("Judges","사사기",21),("Ruth","룻기",4),("1Samuel","사무엘상",31),
("2Samuel","사무엘하",24),("1Kings","열왕기상",22),("2Kings","열왕기하",25),
("1Chronicles","역대상",29),("2Chronicles","역대하",36),("Ezra","에스라",10),
("Nehemiah","느헤미야",13),("Esther","에스더",10),("Job","욥기",42),
("Psalms","시편",150),("Proverbs","잠언",31),("Ecclesiastes","전도서",12),
("SongofSolomon","아가",8),("Isaiah","이사야",66),("Jeremiah","예레미야",52),
("Lamentations","예레미야애가",5),("Ezekiel","에스겔",48),("Daniel","다니엘",12),
("Hosea","호세아",14),("Joel","요엘",3),("Amos","아모스",9),("Obadiah","오바댜",1),
("Jonah","요나",4),("Micah","미가",7),("Nahum","나훔",3),("Habakkuk","하박국",3),
("Zephaniah","스바냐",3),("Haggai","학개",2),("Zechariah","스가랴",14),
("Malachi","말라기",4),("Matthew","마태복음",28),("Mark","마가복음",16),
("Luke","누가복음",24),("John","요한복음",21),("Acts","사도행전",28),
("Romans","로마서",16),("1Corinthians","고린도전서",16),("2Corinthians","고린도후서",13),
("Galatians","갈라디아서",6),("Ephesians","에베소서",6),("Philippians","빌립보서",4),
("Colossians","골로새서",4),("1Thessalonians","데살로니가전서",5),
("2Thessalonians","데살로니가후서",3),("1Timothy","디모데전서",6),
("2Timothy","디모데후서",4),("Titus","디도서",3),("Philemon","빌레몬서",1),
("Hebrews","히브리서",13),("James","야고보서",5),("1Peter","베드로전서",5),
("2Peter","베드로후서",3),("1John","요한1서",5),("2John","요한2서",1),
("3John","요한3서",1),("Jude","유다서",1),("Revelation","요한계시록",22)
]

def token(x):
    return ''.join(c.lower() for c in str(x or '') if c.isalnum())

idmap={}
for i,(eng,kor,_) in enumerate(BOOKS):
    idmap[token(eng)]=i
    idmap[token(kor)]=i

def entries(raw):
    if isinstance(raw,list):
        return [(str(i),x) for i,x in enumerate(raw)]
    if isinstance(raw,dict) and isinstance(raw.get("chapters"),list):
        return [("",raw)]
    if isinstance(raw,dict):
        for k in ("books","bible","data"):
            c=raw.get(k)
            if isinstance(c,list):
                return [(str(i),x) for i,x in enumerate(c)]
            if isinstance(c,dict):
                e=[(kk,v) for kk,v in c.items() if isinstance(v,dict) and isinstance(v.get("chapters"),list)]
                if e:return e
        return [(k,v) for k,v in raw.items() if isinstance(v,dict) and isinstance(v.get("chapters"),list)]
    return []

def resolve(key,b):
    vals=[key,b.get("book"),b.get("code"),b.get("id"),b.get("name"),
          b.get("koreanTitle"),b.get("korean_title"),b.get("nameKo"),b.get("name_ko")]
    for v in vals:
        t=token(v)
        if t in idmap:return idmap[t]
    return None

p=Path("bible_1961_krv.json")
raw=json.loads(p.read_text(encoding="utf-8"))
ordered=[None]*66

for key,b in entries(raw):
    i=resolve(key,b)
    if i is None:
        raise SystemExit(f"책 식별 실패: {key} / {b.get('book')} / {b.get('koreanTitle')}")
    if ordered[i] is not None:
        raise SystemExit(f"중복 책: {BOOKS[i][1]}")
    ordered[i]=b

if any(x is None for x in ordered):
    raise SystemExit("66권 중 누락된 책이 있습니다.")

chapters=0
verses=0
for i,b in enumerate(ordered):
    expected=BOOKS[i][2]
    got=len(b.get("chapters",[]))
    if got!=expected:
        raise SystemExit(f"{BOOKS[i][1]} 장 수 오류: {got}/{expected}")
    chapters+=got
    verses+=sum(len(c.get("verses",[])) for c in b["chapters"])

def verse(i,ch,v):
    c=ordered[i]["chapters"][ch-1]
    return str(c["verses"][v-1].get("text",""))

def fp(s):
    return ''.join(c for c in s if c.isalnum())

assert fp(verse(0,1,1)).startswith("태초에하나님이천지를창조하시니라"), verse(0,1,1)
assert fp(verse(12,1,1)).startswith("아담셋에노스"), verse(12,1,1)
assert fp(verse(42,1,1)).startswith("태초에말씀이계시니라"), verse(42,1,1)

print("OK")
print("66권 정규 식별 완료")
print("장:",chapters)
print("절 위치:",verses)
print("창 1:1:",verse(0,1,1))
print("대상 1:1:",verse(12,1,1))
print("요 1:1:",verse(42,1,1))
