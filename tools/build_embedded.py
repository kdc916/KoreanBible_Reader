#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, re, hashlib, datetime as dt, sys

EXPECTED = {"books":66,"chapters":1189,"verses":31102}
BOOK_FILES = ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 'Joshua', 'Judges', 'Ruth', '1Samuel', '2Samuel', '1Kings', '2Kings', '1Chronicles', '2Chronicles', 'Ezra', 'Nehemiah', 'Esther', 'Job', 'Psalms', 'Proverbs', 'Ecclesiastes', 'SongofSolomon', 'Isaiah', 'Jeremiah', 'Lamentations', 'Ezekiel', 'Daniel', 'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah', 'Malachi', 'Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans', '1Corinthians', '2Corinthians', 'Galatians', 'Ephesians', 'Philippians', 'Colossians', '1Thessalonians', '2Thessalonians', '1Timothy', '2Timothy', 'Titus', 'Philemon', 'Hebrews', 'James', '1Peter', '2Peter', '1John', '2John', '3John', 'Jude', 'Revelation']
APP_VERSION = "0.3.6"

def book_from_obj(obj):
    if not isinstance(obj, dict):
        raise ValueError("book JSON is not an object")
    title = (obj.get("koreanTitle") or obj.get("korean_title") or
             obj.get("nameKo") or obj.get("name_ko") or
             obj.get("name") or obj.get("book") or "")
    chapters = obj.get("chapters") or []
    if not isinstance(chapters, list):
        raise ValueError(f"chapters is not a list: {title}")
    out_ch=[]
    for ci,c in enumerate(chapters):
        if not isinstance(c, dict): 
            continue
        verses=[]
        rv=c.get("verses") or []
        if not isinstance(rv, list):
            raise ValueError(f"verses is not a list: {title} chapter {ci+1}")
        for vi,v in enumerate(rv):
            if not isinstance(v, dict): 
                continue
            text=str(v.get("text",v.get("hangulText",v.get("content","")))).strip()
            verses.append({"verse":int(v.get("verse",v.get("number",vi+1))),"text":text})
        out_ch.append({"chapter":int(c.get("chapter",c.get("number",ci+1))),"verses":verses})
    return {"koreanTitle":str(title),"chapters":out_ch}

def load_from_dir(source_dir:pathlib.Path):
    print(f"[source] loading 66 per-book files from {source_dir}")
    books=[]
    missing=[]
    for name in BOOK_FILES:
        p=source_dir / f"{name}.json"
        if not p.exists():
            missing.append(str(p))
            continue
        raw=json.loads(p.read_text(encoding="utf-8"))
        books.append(book_from_obj(raw))
    if missing:
        print("[source] missing files:")
        for p in missing: print("  -",p)
        raise SystemExit(f"[ERROR] {len(missing)} per-book files are missing")
    return books

def load_from_integrated(path:pathlib.Path):
    print(f"[source] fallback integrated JSON: {path}")
    raw=json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw,list):
        objs=raw
    elif isinstance(raw,dict) and isinstance(raw.get("books"),list):
        objs=raw["books"]
    elif isinstance(raw,dict) and isinstance(raw.get("bible"),list):
        objs=raw["bible"]
    elif isinstance(raw,dict) and isinstance(raw.get("data"),list):
        objs=raw["data"]
    elif isinstance(raw,dict) and isinstance(raw.get("chapters"),list):
        objs=[raw]
    elif isinstance(raw,dict):
        # support a mapping of book names -> book objects
        vals=[v for v in raw.values() if isinstance(v,dict) and isinstance(v.get("chapters"),list)]
        objs=vals
    else:
        objs=[]
    return [book_from_obj(x) for x in objs]

def stats(books):
    chapters=sum(len(b.get("chapters",[])) for b in books)
    verses=sum(
        1 for b in books
        for c in b.get("chapters",[])
        for v in c.get("verses",[])
        if str(v.get("text","")).strip() and str(v.get("text","")).strip()!="(없음)"
    )
    entries=sum(
        len(c.get("verses",[]))
        for b in books for c in b.get("chapters",[])
    )
    return {"books":len(books),"chapters":chapters,"verses":verses,"entries":entries}

def validate(books):
    s=stats(books)
    print(f"[validate] books={s['books']}, chapters={s['chapters']}, nonempty verses={s['verses']}, verse entries={s['entries']}")
    actual={"books":s["books"],"chapters":s["chapters"],"verses":s["verses"]}
    if actual != EXPECTED:
        raise SystemExit(f"[ERROR] validation mismatch: expected {EXPECTED}, got {actual}; total entries={s['entries']}")
    return s

def embed(template:pathlib.Path, books, output:pathlib.Path):
    text=template.read_text(encoding="utf-8")
    compact=json.dumps(books,ensure_ascii=False,separators=(",",":")).replace("</script>","<\\/script>")
    pat=re.compile(r'(<script id="embeddedBible" type="application/json">).*?(</script>)',re.S)
    if not pat.search(text):
        raise SystemExit('[ERROR] embeddedBible script tag not found in index.html')
    built=pat.sub(lambda m:m.group(1)+compact+m.group(2),text,count=1)
    built=built.replace('content="source-template"','content="complete-embedded"',1)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(built,encoding="utf-8")
    (output.parent/".nojekyll").write_text("",encoding="utf-8")

def verify_output(output:pathlib.Path):
    text=output.read_text(encoding="utf-8")
    m=re.search(r'<script id="embeddedBible" type="application/json">(.*?)</script>',text,re.S)
    if not m:
        raise SystemExit("[ERROR] generated index missing embeddedBible")
    books=json.loads(m.group(1))
    return validate(books)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--template",default="index.html")
    ap.add_argument("--source-dir",default="_krv_source/data")
    ap.add_argument("--source-json",default="_krv_source/bible_1961_krv.json")
    ap.add_argument("--output",default="dist/index.html")
    args=ap.parse_args()

    template=pathlib.Path(args.template)
    source_dir=pathlib.Path(args.source_dir)
    source_json=pathlib.Path(args.source_json)
    output=pathlib.Path(args.output)

    print("[build] KoreanBible Reader v0.3.6")
    print("[build] template:",template.resolve())
    print("[build] source dir:",source_dir.resolve())
    print("[build] source json:",source_json.resolve())

    if not template.exists():
        raise SystemExit(f"[ERROR] template does not exist: {template}")

    if source_dir.exists():
        books=load_from_dir(source_dir)
    elif source_json.exists():
        books=load_from_integrated(source_json)
    else:
        raise SystemExit("[ERROR] neither per-book source directory nor integrated JSON exists")

    validate(books)
    embed(template,books,output)
    verified=verify_output(output)

    sha=hashlib.sha256(output.read_bytes()).hexdigest()
    info={
      "appVersion":APP_VERSION,
      "buildMode":"complete-embedded",
      "books":verified["books"],
      "chapters":verified["chapters"],
      "verses":verified["verses"],
      "verseEntries":verified["entries"],
      "indexSha256":sha,
      "builtAtUtc":dt.datetime.now(dt.timezone.utc).isoformat()
    }
    (output.parent/"build-info.json").write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding="utf-8")
    print("[done] output:",output)
    print("[done] size bytes:",output.stat().st_size)
    print("[done] sha256:",sha)

if __name__=="__main__":
    main()
