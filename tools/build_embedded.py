#!/usr/bin/env python3
"""
KoreanBible Reader GitHub Pages builder.

Input:
  - repository root index.html (source template)
  - KRV 1961 JSON source

Output:
  - dist/index.html with all 31,102 verses embedded
  - dist/build-info.json
  - dist/.nojekyll

The build FAILS unless the source validates to exactly:
  66 books / 1,189 chapters / 31,102 non-empty verses.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import urllib.request

EXPECTED = {"books": 66, "chapters": 1189, "verses": 31102}
APP_VERSION = "0.3.5"
FALLBACK_URL = (
    "https://raw.githubusercontent.com/"
    "bluesaurel/Korean-Bible-1961-KRV/main/bible_1961_krv.json"
)

def acquire_source(path: pathlib.Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[source] {path} not found.")
    print(f"[source] fallback download: {FALLBACK_URL}")
    req = urllib.request.Request(
        FALLBACK_URL,
        headers={"User-Agent": "KoreanBibleReader-GitHubActions/0.3.5"},
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        path.write_bytes(response.read())

def normalize(raw):
    if isinstance(raw, dict) and isinstance(raw.get("chapters"), list):
        books = [raw]
    elif isinstance(raw, list):
        books = raw
    elif isinstance(raw, dict):
        books = raw.get("books") or raw.get("bible") or raw.get("data") or []
    else:
        books = []

    if not isinstance(books, list):
        return []

    result = []
    for bi, book in enumerate(books):
        if not isinstance(book, dict):
            continue

        chapters = []
        raw_chapters = book.get("chapters") or []
        if not isinstance(raw_chapters, list):
            raw_chapters = []

        for ci, chapter in enumerate(raw_chapters):
            if not isinstance(chapter, dict):
                continue

            verses = []
            raw_verses = chapter.get("verses") or []
            if not isinstance(raw_verses, list):
                raw_verses = []

            for vi, verse in enumerate(raw_verses):
                if not isinstance(verse, dict):
                    continue

                text = str(
                    verse.get(
                        "text",
                        verse.get("hangulText", verse.get("content", "")),
                    )
                ).strip()

                verses.append(
                    {
                        "verse": int(verse.get("verse", verse.get("number", vi + 1))),
                        "text": text,
                    }
                )

            chapters.append(
                {
                    "chapter": int(
                        chapter.get("chapter", chapter.get("number", ci + 1))
                    ),
                    "verses": verses,
                }
            )

        title = (
            book.get("koreanTitle")
            or book.get("korean_title")
            or book.get("nameKo")
            or book.get("name_ko")
            or str(book.get("name", book.get("book", f"Book {bi + 1}")))
        )

        result.append({"koreanTitle": str(title), "chapters": chapters})

    return result

def stats(books):
    chapters = sum(len(book["chapters"]) for book in books)
    verses = sum(
        1
        for book in books
        for chapter in book["chapters"]
        for verse in chapter["verses"]
        if verse["text"] and verse["text"] != "(없음)"
    )
    return {
        "books": len(books),
        "chapters": chapters,
        "verses": verses,
    }

def require_expected(actual):
    if actual != EXPECTED:
        raise SystemExit(
            "[ERROR] Bible validation failed.\n"
            f"Expected: {EXPECTED}\n"
            f"Actual:   {actual}"
        )

def embed(template_text: str, books) -> str:
    compact = json.dumps(
        books,
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</script>", "<\\/script>")

    pattern = re.compile(
        r'(<script id="embeddedBible" type="application/json">).*?(</script>)',
        re.S,
    )

    if not pattern.search(template_text):
        raise SystemExit(
            '[ERROR] <script id="embeddedBible" type="application/json"> not found.'
        )

    built = pattern.sub(
        lambda m: m.group(1) + compact + m.group(2),
        template_text,
        count=1,
    )

    built = built.replace(
        '<meta name="krv-build-mode" content="source-template">',
        '<meta name="krv-build-mode" content="complete-embedded">',
        1,
    )
    return built

def verify_output(output: pathlib.Path):
    text = output.read_text(encoding="utf-8")
    m = re.search(
        r'<script id="embeddedBible" type="application/json">(.*?)</script>',
        text,
        re.S,
    )
    if not m:
        raise SystemExit("[ERROR] embeddedBible missing from generated index.html")

    books = json.loads(m.group(1))
    actual = stats(books)
    require_expected(actual)

    if 'content="complete-embedded"' not in text:
        raise SystemExit("[ERROR] build marker was not changed to complete-embedded")

    return actual

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", default="index.html")
    parser.add_argument(
        "--source",
        default="_krv_source/bible_1961_krv.json",
    )
    parser.add_argument("--output", default="dist/index.html")
    args = parser.parse_args()

    template = pathlib.Path(args.template)
    source = pathlib.Path(args.source)
    output = pathlib.Path(args.output)

    if not template.exists():
        raise SystemExit(f"[ERROR] Template not found: {template}")

    acquire_source(source)

    print(f"[source] reading: {source}")
    raw = json.loads(source.read_text(encoding="utf-8"))
    books = normalize(raw)
    actual = stats(books)

    print(
        "[validate] "
        f"{actual['books']} books / "
        f"{actual['chapters']} chapters / "
        f"{actual['verses']} verses"
    )
    require_expected(actual)

    template_text = template.read_text(encoding="utf-8")
    built_text = embed(template_text, books)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(built_text, encoding="utf-8")
    (output.parent / ".nojekyll").write_text("", encoding="utf-8")

    verified = verify_output(output)
    sha256 = hashlib.sha256(output.read_bytes()).hexdigest()

    info = {
        "appVersion": APP_VERSION,
        "buildMode": "complete-embedded",
        "books": verified["books"],
        "chapters": verified["chapters"],
        "verses": verified["verses"],
        "source": str(source),
        "indexSha256": sha256,
        "builtAtUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    (output.parent / "build-info.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    size_mb = output.stat().st_size / 1024 / 1024
    print(f"[verify] generated output validated again: {verified}")
    print(f"[verify] SHA-256: {sha256}")
    print(f"[done] {output} ({size_mb:.2f} MB)")
    print("[done] dist/build-info.json created")

if __name__ == "__main__":
    main()
