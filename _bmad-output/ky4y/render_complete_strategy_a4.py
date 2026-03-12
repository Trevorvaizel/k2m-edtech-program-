#!/usr/bin/env python3
"""
Render the complete Kasipul Rise strategy markdown into an A4 paginated HTML file.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from markdown_it import MarkdownIt

SECTION_HEADING_RE = re.compile(r"^##\s+(.*\S)\s*$")


def slugify(text: str) -> str:
    value = text.lower()
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "section"


def clean_inline_md(text: str) -> str:
    out = re.sub(r"\[(.*?)\]\([^)]+\)", r"\1", text)
    out = re.sub(r"[*_`]+", "", out)
    return out.strip()


def extract_front_matter(md_text: str) -> dict[str, str]:
    keys = ("Version", "Date", "Status", "Frame")
    data: dict[str, str] = {}
    for key in keys:
        match = re.search(rf"^\*\*{re.escape(key)}:\*\*\s*(.+)\s*$", md_text, flags=re.MULTILINE)
        data[key.lower()] = match.group(1).strip() if match else "N/A"
    return data


def split_sections(lines: list[str]) -> list[dict[str, object]]:
    headings: list[tuple[int, str]] = []
    for line_no, line in enumerate(lines, start=1):
        match = SECTION_HEADING_RE.match(line)
        if match:
            headings.append((line_no, match.group(1).strip()))

    if not headings:
        return [
            {
                "index": 1,
                "title": "Document Body",
                "start_line": 1,
                "end_line": len(lines),
                "markdown": "\n".join(lines).rstrip() + "\n",
            }
        ]

    sections: list[dict[str, object]] = []
    first = headings[0][0]
    if first > 1:
        sections.append(
            {
                "index": 1,
                "title": "Document Opening",
                "start_line": 1,
                "end_line": first - 1,
                "markdown": "\n".join(lines[: first - 1]).rstrip() + "\n",
            }
        )

    for idx, (start, title) in enumerate(headings, start=1):
        end = headings[idx][0] - 1 if idx < len(headings) else len(lines)
        sections.append(
            {
                "index": len(sections) + 1,
                "title": title,
                "start_line": start,
                "end_line": end,
                "markdown": "\n".join(lines[start - 1 : end]).rstrip() + "\n",
            }
        )

    return sections


def add_heading_ids(fragment: str, section_index: int) -> str:
    hcount = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal hcount
        hcount += 1
        level = match.group(1)
        attrs = match.group(2) or ""
        inner = match.group(3)
        if " id=" in attrs:
            return match.group(0)
        return f'<h{level}{attrs} id="{slugify(f"s{section_index}-{hcount}-{inner}")}">{inner}</h{level}>'

    return re.sub(r"<h([1-6])([^>]*)>(.*?)</h\1>", repl, fragment, flags=re.DOTALL)


def render() -> None:
    root = Path(__file__).resolve().parent
    src = root / "kasipul-rise-complete-strategy-2026-03-05.md"
    out_html = root / "kasipul-rise-complete-strategy-2026-03-05-a4.html"
    out_index = root / "kasipul-rise-complete-strategy-2026-03-05-section-index.json"

    md_text = src.read_text(encoding="utf-8")
    lines = md_text.splitlines()
    sections = split_sections(lines)
    front = extract_front_matter(md_text)

    main_title = re.sub(r"^#\s*", "", lines[0]).strip() if lines else "Kasipul Rise Strategy"
    subtitle = clean_inline_md(str(sections[1]["title"])) if len(sections) > 1 else "Strategic Framework"
    parser = MarkdownIt("gfm-like", {"html": False, "linkify": False, "typographer": False, "breaks": False})

    section_html_chunks: list[str] = []
    section_rows: list[str] = []
    index_sections: list[dict[str, object]] = []

    for section in sections:
        idx = int(section["index"])
        title = clean_inline_md(str(section["title"]))
        start = int(section["start_line"])
        end = int(section["end_line"])
        rendered = add_heading_ids(parser.render(str(section["markdown"])), idx)

        section_html_chunks.append(
            (
                f'<section class="doc-section" data-section-index="{idx}" '
                f'data-section-title="{escape(title, quote=True)}" '
                f'data-start-line="{start}" data-end-line="{end}">\n'
                f"{rendered}\n"
                "</section>"
            )
        )

        section_rows.append(
            "<tr>"
            f"<td>{idx:02d}</td>"
            f"<td>{escape(title)}</td>"
            f"<td>{start}-{end}</td>"
            '<td><span class="status-ok">Rendered</span></td>'
            "</tr>"
        )

        index_sections.append({"index": idx, "title": title, "start_line": start, "end_line": end, "status": "rendered"})

    generated = datetime.now(timezone.utc)

    html_output = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(main_title)} - A4 UX Edition</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;800;900&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --navy-deep:#0A2342; --navy-light:#1a3a5c; --orange:#FF6B35; --gold:#D4AF37;
      --white:#fff; --ink:#2f3540; --line:#dde5f1; --muted:#6d7f97; --ok:#1a7f37;
      --font-display:'Montserrat',sans-serif; --font-body:'Inter',sans-serif;
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{
      font-family:var(--font-body); color:var(--ink);
      background:radial-gradient(circle at top left,#f7f9fd 0%,#e9eff8 45%,#dce5f1 100%);
      line-height:1.58; padding:8mm 0; -webkit-print-color-adjust:exact; print-color-adjust:exact;
    }}
    .doc {{ max-width:210mm; margin:0 auto; }}
    .page {{
      width:210mm; height:297mm; margin:0 auto 8mm; background:var(--white); position:relative;
      box-shadow:0 10px 30px rgba(0,0,0,.16); overflow:hidden; page-break-after:always;
      padding:19mm 15mm 14mm;
    }}
    .page:last-child {{ margin-bottom:0; page-break-after:auto; }}
    .river-lines {{ position:absolute; inset:0; pointer-events:none; opacity:.2; }}
    .river {{
      position:absolute; height:2px; background:linear-gradient(90deg,transparent,var(--orange),transparent);
      animation:flow 8s ease-in-out infinite;
    }}
    .river:nth-child(1) {{ top:18%; width:70%; left:-30%; }}
    .river:nth-child(2) {{ top:47%; width:55%; right:-24%; animation-delay:2s; }}
    .river:nth-child(3) {{ top:78%; width:64%; left:-18%; animation-delay:4s; }}
    @keyframes flow {{ 0%,100% {{ transform:translateX(0); opacity:.28; }} 50% {{ transform:translateX(44px); opacity:.65; }} }}
    .cover {{
      background:linear-gradient(135deg,var(--navy-deep) 0%,var(--navy-light) 100%);
      color:var(--white); text-align:center; display:flex; flex-direction:column; justify-content:center; align-items:center;
      padding:22mm 20mm;
    }}
    .cover::before {{
      content:''; position:absolute; inset:0; pointer-events:none;
      background:linear-gradient(90deg,transparent 49%,rgba(255,107,53,.04) 50%,transparent 51%),
                 linear-gradient(0deg,transparent 49%,rgba(255,107,53,.04) 50%,transparent 51%);
      background-size:100px 100px;
    }}
    .version-badge {{
      z-index:1; display:inline-block; padding:8px 24px; border-radius:999px; margin-bottom:36px;
      background:var(--orange); color:var(--white); font:700 11px var(--font-display); letter-spacing:2.3px; text-transform:uppercase;
    }}
    .cover-title {{ z-index:1; font:900 64px/0.96 var(--font-display); letter-spacing:-1px; margin-bottom:12px; }}
    .cover-title .kasipul {{ display:block; font-size:56px; color:var(--white); }}
    .cover-title .rise {{ display:block; font-size:44px; color:var(--orange); letter-spacing:11px; text-transform:uppercase; }}
    .cover-subtitle {{ z-index:1; margin-top:16px; font:400 20px/1.35 var(--font-display); color:var(--gold); }}
    .cover-tagline {{ z-index:1; margin-top:24px; max-width:122mm; font-size:14px; font-weight:300; color:rgba(255,255,255,.8); }}
    .cover-tagline .highlight {{ color:var(--orange); font-weight:600; }}
    .cover-meta {{
      z-index:1; margin-top:34px; width:100%; max-width:126mm; padding:18px 20px; border-radius:10px; text-align:left;
      background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.12);
    }}
    .cover-meta-row {{ display:flex; gap:10px; margin:9px 0; }}
    .cover-meta-label {{ min-width:72px; font:700 10px var(--font-display); letter-spacing:1.5px; text-transform:uppercase; color:rgba(255,255,255,.62); }}
    .cover-meta-value {{ font-size:13px; color:var(--white); }}
    .cover-footer {{ z-index:1; margin-top:auto; font-size:10px; color:rgba(255,255,255,.66); font-style:italic; }}
    .cover-footer strong {{ color:var(--orange); font-style:normal; font-weight:600; }}
    .tracker {{ background:linear-gradient(180deg,#fff 0%,#f8fbff 100%); }}
    .tracker h2 {{ font:700 18px var(--font-display); color:var(--navy-deep); text-transform:uppercase; letter-spacing:.8px; margin-bottom:8px; }}
    .tracker p {{ font-size:10px; color:#5b6d85; margin-bottom:8px; }}
    .tracker-table-wrap {{ margin-top:10px; border:1px solid var(--line); border-radius:8px; overflow:hidden; }}
    table {{ width:100%; border-collapse:collapse; font-size:8.7pt; }}
    th,td {{ border:1px solid #d9e1ec; padding:2mm 2.2mm; text-align:left; vertical-align:top; }}
    th {{ background:var(--navy-deep); color:var(--white); font:700 8pt var(--font-display); text-transform:uppercase; letter-spacing:.5px; }}
    .status-ok {{ color:var(--ok); font:700 8pt var(--font-display); text-transform:uppercase; letter-spacing:.4px; }}
    .tracker-stats {{ margin-top:11px; padding:10px 12px; border-radius:6px; border-left:3px solid var(--orange);
      background:linear-gradient(135deg,rgba(10,35,66,.05),rgba(255,107,53,.06)); font-size:8.8pt; color:#395174; }}
    .content-page::before {{
      content:''; position:absolute; inset:0; pointer-events:none;
      background:radial-gradient(circle at 95% 8%,rgba(255,107,53,.08),transparent 60%),
                 linear-gradient(180deg,rgba(10,35,66,.012),transparent 24%);
    }}
    .running-header {{
      position:absolute; top:8mm; left:15mm; right:15mm; z-index:2; display:flex; justify-content:space-between; align-items:center;
      border-bottom:2px solid var(--navy-deep); padding-bottom:2mm;
    }}
    .rh-left {{ font:800 13px var(--font-display); letter-spacing:1.6px; text-transform:uppercase; color:var(--navy-deep); white-space:nowrap; }}
    .rh-left .rise {{ color:var(--orange); }}
    .rh-right {{ font-size:8.7px; color:#5f6e84; text-align:right; max-width:68%; }}
    .page-content {{ position:absolute; top:24mm; left:15mm; right:15mm; bottom:19mm; overflow:hidden; font-size:10px; z-index:1; }}
    .page-footer {{
      position:absolute; bottom:8mm; left:15mm; right:15mm; z-index:2; display:flex; justify-content:space-between; align-items:center;
      border-top:1px solid var(--line); padding-top:2mm; font-size:8px; color:#8592a5;
    }}
    .page-number {{ font:700 8px var(--font-display); color:var(--navy-deep); }}
    h1 {{ font:800 22px/1.2 var(--font-display); color:var(--navy-deep); margin:0 0 10px; }}
    h2 {{ font:700 16px/1.3 var(--font-display); color:var(--navy-deep); margin:16px 0 9px; padding-bottom:5px;
      border-bottom:1.6px solid var(--orange); text-transform:uppercase; letter-spacing:.45px; page-break-after:avoid; }}
    h3 {{ font:600 12px/1.3 var(--font-display); color:var(--orange); margin:12px 0 7px; text-transform:uppercase; letter-spacing:.8px; page-break-after:avoid; }}
    h4,h5,h6 {{ font-family:var(--font-display); color:var(--navy-deep); margin:8px 0 6px; page-break-after:avoid; }}
    p {{ font-size:10px; line-height:1.6; margin:0 0 9px; color:#2f3540; }}
    ul,ol {{ margin:0 0 11px 20px; }}
    li {{ font-size:9.7px; line-height:1.5; margin-bottom:4px; color:#2f3540; }}
    strong {{ color:var(--navy-deep); font-weight:600; }} em {{ color:#526179; }}
    blockquote {{ margin:10px 0; padding:10px 12px; border-left:3px solid var(--orange); border-radius:4px;
      background:linear-gradient(135deg,rgba(10,35,66,.05),rgba(255,107,53,.05)); page-break-inside:avoid; }}
    blockquote p {{ margin:0; font-size:9px; color:#556277; font-style:italic; }}
    hr {{ border:none; border-top:1px solid #d5deeb; margin:11px 0; }}
    code {{ font:8.7px Consolas,'Courier New',monospace; background:#f2f6fc; border:1px solid #dbe4f3; border-radius:3px; padding:1px 4px; }}
    pre {{ margin:10px 0; border:1px solid #dbe4f3; border-radius:6px; background:#f2f6fc; padding:9px 10px; overflow:auto; font-size:8.4px; line-height:1.35; page-break-inside:avoid; }}
    a {{ color:#1d5db3; text-decoration:none; border-bottom:1px dotted rgba(29,93,179,.42); }}
    .info-box,.warning-box,.success-box {{ border-radius:6px; padding:9px 10px; margin:8px 0; font-size:9px; }}
    .info-box {{ background:rgba(10,35,66,.04); border:1px solid rgba(10,35,66,.12); }}
    .warning-box {{ background:rgba(255,107,53,.07); border:1px solid rgba(255,107,53,.26); }}
    .success-box {{ background:rgba(212,175,55,.11); border:1px solid rgba(212,175,55,.32); }}
    .checklist {{ list-style:none; margin-left:0; padding-left:0; }}
    .checklist li {{ position:relative; padding-left:18px; }}
    .checklist li::before {{ content:'[ ]'; position:absolute; left:0; top:0; color:var(--navy-deep); font-size:9px; font-family:Consolas,'Courier New',monospace; }}
    .task-list-item {{ list-style:none; margin-left:-16px; padding-left:16px; }}
    .task-list-item input[type=checkbox] {{ transform:scale(.85); margin-right:5px; }}
    .force-fit {{ overflow:auto; max-height:100%; padding-right:4px; border-right:2px solid rgba(155,28,28,.3); }}
    .ending-page {{ background:linear-gradient(135deg,var(--navy-deep) 0%,var(--navy-light) 100%); color:var(--white); padding-top:24mm; }}
    .ending-page::before {{ content:''; position:absolute; inset:0; pointer-events:none;
      background:radial-gradient(circle at 12% 18%,rgba(255,107,53,.16),transparent 45%),radial-gradient(circle at 84% 84%,rgba(212,175,55,.16),transparent 42%); }}
    .ending-content {{ position:relative; z-index:1; height:calc(100% - 14mm); display:flex; flex-direction:column; align-items:center; text-align:center; padding:0 8mm; }}
    .ending-badge {{ display:inline-block; padding:8px 22px; border-radius:999px; margin-bottom:28px; background:rgba(255,255,255,.09); border:1px solid rgba(255,255,255,.2); font:10px var(--font-display); letter-spacing:2px; text-transform:uppercase; color:#ffd9ba; }}
    .ending-title,.ending-rise {{ border:none; padding:0; margin:0; text-transform:uppercase; }}
    .ending-title {{ font:700 30px/1.15 var(--font-display); color:var(--white); }}
    .ending-rise {{ font:800 36px/1.1 var(--font-display); color:var(--orange); letter-spacing:1px; margin-top:6px; }}
    .ending-cta {{ margin-top:14px; font-size:16px; color:#ffdcb8; font-weight:500; }}
    .ending-meta {{ margin-top:24px; width:100%; max-width:126mm; text-align:left; border-radius:10px; padding:14px 15px;
      background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.18); }}
    .ending-meta p {{ font-size:10px; margin:5px 0; color:rgba(255,255,255,.88); }} .ending-meta strong {{ color:#ffdcb8; }}
    .ending-note {{ margin-top:20px; font-size:10px; color:rgba(255,255,255,.72); max-width:130mm; line-height:1.6; font-style:italic; }}
    .source-store {{ display:none; }}
    @media print {{
      body {{ background:#fff; padding:0; }}
      .page {{ margin:0; box-shadow:none; page-break-after:always; }}
      .page:last-child {{ page-break-after:auto; }}
      .river {{ animation:none; }}
    }}
  </style>
</head>
<body>
  <main class="doc">
    <section class="page cover">
      <div class="river-lines"><div class="river"></div><div class="river"></div><div class="river"></div></div>
      <span class="version-badge">Version 4.0 - A4 UX Edition</span>
      <h1 class="cover-title"><span class="kasipul">KASIPUL</span><span class="rise">RISE</span></h1>
      <p class="cover-subtitle">{escape(subtitle)}</p>
      <p class="cover-tagline">Infrastructure layer where <span class="highlight">grassroots execution</span> meets <span class="highlight">professional opportunity</span>.</p>
      <div class="cover-meta">
        <div class="cover-meta-row"><span class="cover-meta-label">Title</span><span class="cover-meta-value">{escape(main_title)}</span></div>
        <div class="cover-meta-row"><span class="cover-meta-label">Version</span><span class="cover-meta-value">{escape(front["version"])}</span></div>
        <div class="cover-meta-row"><span class="cover-meta-label">Date</span><span class="cover-meta-value">{escape(front["date"])}</span></div>
        <div class="cover-meta-row"><span class="cover-meta-label">Status</span><span class="cover-meta-value">{escape(front["status"])}</span></div>
        <div class="cover-meta-row"><span class="cover-meta-label">Frame</span><span class="cover-meta-value">{escape(front["frame"])}</span></div>
      </div>
      <p class="cover-footer">Designed for readability and print fidelity on A4 pages. <strong>Build WITH us, not FOR us.</strong></p>
    </section>

    <section class="page tracker">
      <h2>Section Conversion Tracker</h2>
      <p>This tracker mirrors the markdown source section-by-section so progress stays auditable.</p>
      <div class="tracker-table-wrap">
        <table>
          <thead><tr><th style="width:12%;">ID</th><th style="width:58%;">Section</th><th style="width:16%;">Lines</th><th style="width:14%;">Status</th></tr></thead>
          <tbody>{"".join(section_rows)}</tbody>
        </table>
      </div>
      <div class="tracker-stats" id="render-summary">Preparing pagination...</div>
    </section>

    <div id="paginated-pages"></div>

    <section class="page ending-page">
      <div class="river-lines"><div class="river"></div><div class="river"></div><div class="river"></div></div>
      <div class="ending-content">
        <span class="ending-badge">End of Strategy</span>
        <h2 class="ending-title">WE ARE NOT WAITING ANYMORE.</h2>
        <h2 class="ending-rise">WE ARE RISING.</h2>
        <p class="ending-cta">{escape(front["frame"])}</p>
        <div class="ending-meta">
          <p><strong>Document:</strong> {escape(main_title)}</p>
          <p><strong>Version:</strong> {escape(front["version"])}</p>
          <p><strong>Date:</strong> {escape(front["date"])}</p>
          <p><strong>Status:</strong> {escape(front["status"])}</p>
          <p><strong>Sections Rendered:</strong> {len(index_sections)}</p>
          <p><strong>Generated:</strong> {escape(generated.strftime("%Y-%m-%d %H:%M UTC"))}</p>
        </div>
        <p class="ending-note">Every page should come back marked up. If it is clean, the review was too shallow.</p>
      </div>
      <div class="page-footer"><span>Confidential Draft - For Team Review Only</span><span class="page-number" id="ending-page-number">Page ...</span></div>
    </section>
  </main>

  <div id="source-sections" class="source-store">{"".join(section_html_chunks)}</div>

  <script>
    (function () {{
      const sourceSections = Array.from(document.querySelectorAll("#source-sections .doc-section"));
      const pageRoot = document.getElementById("paginated-pages");
      const summary = document.getElementById("render-summary");
      const endingPageNumber = document.getElementById("ending-page-number");
      let pageNumber = 2;

      function classifyBlock(el) {{
        const tag = (el.tagName || "").toUpperCase();
        const text = (el.textContent || "").trim().toLowerCase();
        if (tag === "P") {{
          if (text.startsWith("decision rule:") || text.startsWith("deliverable:") || text.startsWith("expectation:")) el.classList.add("info-box");
          if (text.startsWith("risk:") || text.startsWith("constraint:") || text.startsWith("failure mode:")) el.classList.add("warning-box");
          if (text.startsWith("the question")) el.classList.add("success-box");
        }}
        if (tag === "UL" || tag === "OL") {{
          const looksLikeChecklist = Array.from(el.querySelectorAll(":scope > li")).some((li) => {{
            const t = (li.textContent || "").trim();
            return t.startsWith("[ ]") || t.startsWith("[x]") || t.startsWith("[X]");
          }});
          if (looksLikeChecklist) el.classList.add("checklist");
        }}
      }}

      function createContentPage(sectionTitle, sectionIndex, continued) {{
        pageNumber += 1;
        const page = document.createElement("section");
        page.className = "page content-page";

        const header = document.createElement("div");
        header.className = "running-header";
        const left = document.createElement("span");
        left.className = "rh-left";
        left.innerHTML = 'KASIPUL <span class="rise">RISE</span>';
        const right = document.createElement("span");
        right.className = "rh-right";
        right.textContent = "Strategic Framework v4.0 | Section " + String(sectionIndex).padStart(2, "0") + " - " + sectionTitle + (continued ? " (continued)" : "");
        header.appendChild(left);
        header.appendChild(right);

        const content = document.createElement("div");
        content.className = "page-content";

        const footer = document.createElement("div");
        footer.className = "page-footer";
        const footerLabel = document.createElement("span");
        footerLabel.textContent = "Confidential Draft - Verbatim source conversion";
        const footerPage = document.createElement("span");
        footerPage.className = "page-number";
        footerPage.textContent = "Page " + String(pageNumber);
        footer.appendChild(footerLabel);
        footer.appendChild(footerPage);

        page.appendChild(header);
        page.appendChild(content);
        page.appendChild(footer);
        pageRoot.appendChild(page);
        return content;
      }}

      function fits(contentEl) {{
        return contentEl.scrollHeight <= contentEl.clientHeight + 1;
      }}

      for (const section of sourceSections) {{
        const sectionIndex = Number(section.dataset.sectionIndex || "0");
        const sectionTitle = section.dataset.sectionTitle || "Untitled";
        const startLine = section.dataset.startLine || "?";
        const endLine = section.dataset.endLine || "?";
        const blocks = Array.from(section.children);
        if (!blocks.length) continue;

        let contentEl = createContentPage(sectionTitle, sectionIndex, false);
        let isContinued = false;

        for (const block of blocks) {{
          const clone = block.cloneNode(true);
          classifyBlock(clone);
          clone.setAttribute("data-source-lines", startLine + "-" + endLine);
          contentEl.appendChild(clone);

          if (!fits(contentEl)) {{
            contentEl.removeChild(clone);
            if (!contentEl.children.length) {{
              clone.classList.add("force-fit");
              contentEl.appendChild(clone);
              continue;
            }}
            isContinued = true;
            contentEl = createContentPage(sectionTitle, sectionIndex, isContinued);
            contentEl.appendChild(clone);
            if (!fits(contentEl)) clone.classList.add("force-fit");
          }}
        }}
      }}

      if (endingPageNumber) endingPageNumber.textContent = "Page " + String(pageNumber + 1);
      summary.textContent = sourceSections.length + " sections rendered into " + (pageNumber - 2) + " content pages (plus cover, tracker, and ending page).";
    }})();
  </script>
</body>
</html>
"""

    out_html.write_text(html_output, encoding="utf-8")

    index_payload = {
        "source_markdown": src.name,
        "output_html": out_html.name,
        "generated_utc": generated.isoformat(),
        "section_count": len(index_sections),
        "sections": index_sections,
    }
    out_index.write_text(json.dumps(index_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Rendered: {out_html}")
    print(f"Index:    {out_index}")
    print(f"Sections: {len(index_sections)}")


if __name__ == "__main__":
    render()
