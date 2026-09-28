#!/usr/bin/env python3
"""
Build a GitHub Pages index.html with the complete KRV 1961 Bible embedded.
The runtime then needs no recovery, CORS proxy, JSONP, or network Bible fetch.

Validation gate:
- 66 books
- 1,189 chapters
- 31,102 non-empty verses
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys, urllib.request

EXPECTED = (66, 1189, 31102)
DEFAULT_URL = "https://raw.githubusercontent.com/bluesaurel/Korean-Bible-1961-KRV/main/bible_1961_krv.json"

def download_source(path: pathlib.Path) -> None:
    print(f"[build] bible source not found; downloading verified public source:\n{DEFAULT_URL}")
    req = urllib.request.Request(DEFAULT_URL, headers={"User-Agent":"KoreanBibleReader-GitHubActions"})
    with urllib.request.urlopen(req, timeout=90) as r:
        path.write_bytes(r.read())

def normalize(raw):
    if isinstance(raw, dict) and "chapters" in raw:
        books = [raw]
    elif isinstance(raw, list):
        books = raw
    elif isinstance(raw, dict):
        books = raw.get("books") or raw.get("bible") or raw.get("data") or []
    else:
        books = []
    out = []
    for bi,b in enumerate(books):
        chapters=[]
        for ci,c in enumerate(b.get("chapters",[]) or []):
            verses=[]
            for vi,v in enumerate(c.get("verses",[]) or []):
                text=str(v.get("text",v.get("hangulText",v.get("content","")))).strip()
                verses.append({"verse":int(v.get("verse",v.get("number",vi+1))),"text":text})
            chapters.append({"chapter":int(c.get("chapter",c.get("number",ci+1))),"verses":verses})
        title=b.get("koreanTitle") or b.get("korean_title") or b.get("nameKo") or b.get("name_ko") or str(b.get("name",b.get("book","")))
        out.append({"koreanTitle":title,"chapters":chapters})
    return out

def stats(books):
    chapters=sum(len(b["chapters"]) for b in books)
    verses=sum(
        1 for b in books for c in b["chapters"] for v in c["verses"]
        if v["text"] and v["text"] != "(없음)"
    )
    return len(books),chapters,verses

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--template",default="KoreanBible_Reader_v0.3.4.html")
    ap.add_argument("--source",default="bible_1961_krv.json")
    ap.add_argument("--output",default="dist/index.html")
    args=ap.parse_args()

    template=pathlib.Path(args.template)
    source=pathlib.Path(args.source)
    output=pathlib.Path(args.output)

    if not template.exists():
        raise SystemExit(f"template not found: {template}")
    if not source.exists():
        download_source(source)

    raw=json.loads(source.read_text(encoding="utf-8"))
    books=normalize(raw)
    actual=stats(books)
    print(f"[build] validation: {actual[0]} books / {actual[1]} chapters / {actual[2]} verses")
    if actual != EXPECTED:
        raise SystemExit(f"Bible validation failed: expected {EXPECTED}, got {actual}")

    compact=json.dumps(books,ensure_ascii=False,separators=(",",":")).replace("</script>","<\\/script>")
    text=template.read_text(encoding="utf-8")
    pat=re.compile(r'(<script id="embeddedBible" type="application/json">).*?(</script>)',re.S)
    if not pat.search(text):
        raise SystemExit("embeddedBible script tag not found")
    text=pat.sub(lambda m:m.group(1)+compact+m.group(2),text,count=1)

    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(text,encoding="utf-8")
    (output.parent/".nojekyll").write_text("",encoding="utf-8")
    size=output.stat().st_size/1024/1024
    print(f"[build] complete embedded Pages file: {output} ({size:.2f} MB)")

if __name__=="__main__":
    main()
