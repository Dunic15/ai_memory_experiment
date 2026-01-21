#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


INPUT_PDF = Path(__file__).with_name("Tesi edo Cina copia.pdf")
INPUT_TXT = Path(__file__).with_name("edo_extracted.txt")
OUTPUT_TEX = Path(__file__).with_name("edo_converted.tex")
OUTPUT_FRONTMATTER = Path(__file__).with_name("edo_frontmatter.tex")
OUTPUT_BODY = Path(__file__).with_name("edo_body.tex")


CJK_RE = re.compile(r"[\u4e00-\u9fff]")
PAGE_NUM_RE = re.compile(r"^(?:[IVXLC]+|\d+)\s*$")
DOC_NOISE_RE = re.compile(
    r"^(?:TABLE OF CONTENTS|LIST OF FIGURES(?: AND TABLES)?|LIST OF TABLES)\s*$",
    re.IGNORECASE,
)


def latex_escape(text: str) -> str:
    text = text.replace("\\", r"\textbackslash{}")
    text = text.replace("&", r"\&")
    text = text.replace("%", r"\%")
    text = text.replace("$", r"\$")
    text = text.replace("#", r"\#")
    text = text.replace("_", r"\_")
    text = text.replace("{", r"\{")
    text = text.replace("}", r"\}")
    text = text.replace("~", r"\textasciitilde{}")
    text = text.replace("^", r"\textasciicircum{}")
    return text


def is_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text))


def normalize_lines(raw: str) -> list[str]:
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    raw = raw.replace("\f", "\n")
    lines = [ln.rstrip() for ln in raw.split("\n")]
    return lines


def strip_toc_lines(lines: list[str]) -> list[str]:
    out: list[str] = []
    toc_line = re.compile(r"\.{5,}\s*\w+\s*$")
    for ln in lines:
        if toc_line.search(ln):
            continue
        out.append(ln)
    return out


def reflow_paragraph(lines: list[str]) -> str:
    joined = "\n".join(lines).strip()
    if not joined:
        return ""
    if is_cjk(joined):
        return "".join(ln.strip() for ln in lines).strip()
    return " ".join(ln.strip() for ln in lines).strip()


def paragraphs_from_lines(lines: list[str]) -> list[str]:
    paras: list[str] = []
    buf: list[str] = []
    for ln in lines:
        s = ln.strip()
        if PAGE_NUM_RE.fullmatch(s) or DOC_NOISE_RE.fullmatch(s):
            continue
        if not s:
            p = reflow_paragraph(buf)
            if p:
                paras.append(p)
            buf = []
            continue
        buf.append(s)
    p = reflow_paragraph(buf)
    if p:
        paras.append(p)
    return paras


def find_first_index(lines: list[str], pattern: re.Pattern[str], start: int = 0) -> int | None:
    for i in range(start, len(lines)):
        if pattern.search(lines[i]):
            return i
    return None


def extract_abstracts(lines: list[str]) -> tuple[list[str], list[str], int]:
    cn_start = find_first_index(lines, re.compile(r"^\s*摘\s*要\s*$"))
    if cn_start is None:
        cn_start = find_first_index(lines, re.compile(r"^\s*摘要\s*$"))
    en_start = find_first_index(lines, re.compile(r"^\s*ABSTRACT\s*$"), start=(cn_start or 0) + 1)

    if cn_start is None or en_start is None:
        return [], [], 0

    # Chinese abstract often repeats heading; keep content after the last heading inside the block.
    cn_block = lines[cn_start:en_start]
    last_cn_heading = None
    for i, ln in enumerate(cn_block):
        if re.match(r"^\s*摘要\s*$", ln):
            last_cn_heading = i
    if last_cn_heading is not None:
        cn_block = cn_block[last_cn_heading + 1 :]

    # English abstract until first real chapter (not ToC).
    chap_re = re.compile(r"^\s*CHAPTER\s+1\b")
    en_end = find_first_index(lines, chap_re, start=en_start + 1)
    if en_end is None:
        en_end = len(lines)

    en_block = lines[en_start + 1 : en_end]
    cn_paras = paragraphs_from_lines(cn_block)
    en_paras = paragraphs_from_lines(en_block)
    if en_paras and en_paras[0].strip().upper() == "ABSTRACT":
        en_paras = en_paras[1:]
    # Stop at the start of lists of figures/tables (often follows the abstracts in PDFs).
    trimmed: list[str] = []
    for p in en_paras:
        if re.match(r"^(Figure|Table)\b", p.strip()):
            break
        trimmed.append(p)
    en_paras = trimmed
    return cn_paras, en_paras, en_end


def build_body(lines: list[str], start: int) -> list[str]:
    chapter_re = re.compile(r"^\s*CHAPTER\s+(\d+)\s+(.+?)\s*$")
    section_re = re.compile(r"^\s*(\d+)\.(\d+)\s+(.+?)\s*$")
    subsection_re = re.compile(r"^\s*(\d+)\.(\d+)\.(\d+)\s+(.+?)\s*$")

    out: list[str] = []
    paragraph_buf: list[str] = []

    current_chapter_num: str | None = None
    current_chapter_title: str | None = None
    current_section_key: str | None = None
    current_subsection_key: str | None = None

    def flush_paragraph() -> None:
        nonlocal paragraph_buf
        p = reflow_paragraph(paragraph_buf)
        paragraph_buf = []
        if not p:
            return
        out.append(latex_escape(p) + "\n")

    i = start
    while i < len(lines):
        ln_stripped = lines[i].strip()
        if not ln_stripped:
            flush_paragraph()
            i += 1
            continue

        m = chapter_re.match(ln_stripped)
        if m:
            chap_num, chap_title = m.group(1), m.group(2)
            # Merge wrapped chapter titles that continue on the next line in ALL CAPS.
            if i + 1 < len(lines):
                nxt = lines[i + 1].strip()
                if (
                    nxt
                    and not chapter_re.match(nxt)
                    and not section_re.match(nxt)
                    and not subsection_re.match(nxt)
                    and re.fullmatch(r"[A-Z0-9&'’:\- ]+", nxt)
                ):
                    chap_title = f"{chap_title} {nxt}".strip()
                    i += 1
            # Skip page headers repeating current chapter.
            if chap_num == current_chapter_num and chap_title == (current_chapter_title or ""):
                i += 1
                continue
            flush_paragraph()
            current_chapter_num = chap_num
            current_chapter_title = chap_title
            current_section_key = None
            current_subsection_key = None
            out.append(f"\\chapter{{{latex_escape(chap_title)}}}\n")
            i += 1
            continue

        m = subsection_re.match(ln_stripped)
        if m:
            key = f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
            if current_chapter_num is not None and m.group(1) != current_chapter_num:
                i += 1
                continue
            if len(m.group(2)) != 1 or len(m.group(3)) != 1:
                i += 1
                continue
            if int(m.group(2)) > 9 or int(m.group(3)) > 9:
                i += 1
                continue
            title = m.group(4)
            if key == current_subsection_key:
                i += 1
                continue
            flush_paragraph()
            current_subsection_key = key
            out.append(f"\\subsection{{{latex_escape(title)}}}\n")
            i += 1
            continue

        m = section_re.match(ln_stripped)
        if m:
            key = f"{m.group(1)}.{m.group(2)}"
            if current_chapter_num is not None and m.group(1) != current_chapter_num:
                i += 1
                continue
            if len(m.group(2)) != 1:
                i += 1
                continue
            if int(m.group(2)) > 9:
                i += 1
                continue
            title = m.group(3)
            if key == current_section_key:
                i += 1
                continue
            flush_paragraph()
            current_section_key = key
            current_subsection_key = None
            out.append(f"\\section{{{latex_escape(title)}}}\n")
            i += 1
            continue

        # Drop standalone page counters (roman/ar numeric) commonly found at footer.
        if PAGE_NUM_RE.fullmatch(ln_stripped):
            i += 1
            continue

        paragraph_buf.append(ln_stripped)
        i += 1

    flush_paragraph()
    return out


def main() -> None:
    if not INPUT_PDF.exists():
        raise SystemExit(f"Missing PDF: {INPUT_PDF}")
    if not INPUT_TXT.exists():
        raise SystemExit(
            f"Missing extracted text: {INPUT_TXT}\n"
            f"Run: pdftotext -layout -enc UTF-8 {INPUT_PDF.name!r} {INPUT_TXT.name!r}"
        )

    raw = INPUT_TXT.read_text(encoding="utf-8", errors="replace")
    lines = strip_toc_lines(normalize_lines(raw))

    cn_abs, en_abs, body_start = extract_abstracts(lines)
    body_lines = build_body(lines, start=body_start)

    tex: list[str] = []
    tex.append(r"\documentclass[12pt,a4paper]{book}" + "\n")
    tex.append(r"\usepackage[utf8]{inputenc}" + "\n")
    tex.append(r"\usepackage[T1]{fontenc}" + "\n")
    tex.append(r"\usepackage{parskip}" + "\n")
    tex.append(r"\usepackage{CJKutf8}" + "\n")
    tex.append(r"\newenvironment{ChineseBlock}{\begin{CJK*}{UTF8}{gbsn}}{\end{CJK*}}" + "\n")
    tex.append(r"\usepackage[colorlinks=true,linkcolor=black,citecolor=black,urlcolor=black]{hyperref}" + "\n")
    tex.append("\n\\begin{document}\n")

    tex.append("\\frontmatter\n")
    frontmatter_tex: list[str] = []
    frontmatter_tex.append("% Auto-generated from PDF text; edit as needed.\n")
    if cn_abs:
        frontmatter_tex.append("\\begin{ChineseBlock}\n")
        frontmatter_tex.append("\\chapter*{摘要}\n")
        frontmatter_tex.append("\\addcontentsline{toc}{chapter}{摘要}\n")
        for p in cn_abs:
            frontmatter_tex.append(latex_escape(p) + "\n\n")
        frontmatter_tex.append("\\end{ChineseBlock}\n\n")
        tex.append("\\begin{ChineseBlock}\n")
        tex.append("\\chapter*{摘要}\n")
        tex.append("\\addcontentsline{toc}{chapter}{摘要}\n")
        for p in cn_abs:
            tex.append(latex_escape(p) + "\n\n")
        tex.append("\\end{ChineseBlock}\n\n")
    if en_abs:
        frontmatter_tex.append("\\chapter*{Abstract}\n")
        frontmatter_tex.append("\\addcontentsline{toc}{chapter}{Abstract}\n")
        for p in en_abs:
            frontmatter_tex.append(latex_escape(p) + "\n\n")
        tex.append("\\chapter*{Abstract}\n")
        tex.append("\\addcontentsline{toc}{chapter}{Abstract}\n")
        for p in en_abs:
            tex.append(latex_escape(p) + "\n\n")

    frontmatter_tex.append("\\tableofcontents\n\\cleardoublepage\n\n")
    tex.append("\\tableofcontents\n\\cleardoublepage\n\n")

    tex.append("\\mainmatter\n")
    body_tex: list[str] = []
    body_tex.append("% Auto-generated from PDF text; edit as needed.\n")
    body_tex.extend(body_lines)
    tex.extend(body_tex)
    tex.append("\n\\end{document}\n")

    OUTPUT_TEX.write_text("".join(tex), encoding="utf-8")
    OUTPUT_FRONTMATTER.write_text("".join(frontmatter_tex), encoding="utf-8")
    OUTPUT_BODY.write_text("".join(body_tex), encoding="utf-8")


if __name__ == "__main__":
    main()
