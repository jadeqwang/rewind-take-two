#!/usr/bin/env python3
"""Build media/reviews/v3/A/index.html (a local before/after page) from docs/revisions/review_A.json.
v2 "before" clips are cut from the v2 preview into media/reviews/v3/A/before/ when missing.

    python3 tools/streams/review_page_A.py
"""
import html, json, os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR = os.path.join(ROOT, "media", "reviews", "v3", "A")
V2 = os.path.join(ROOT, "deliverables", "wip", "rewind_roughcut_v2_preview.mp4")
FF = os.environ.get("FFMPEG", os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg"))
OPEN = [  # (title, text): decisions still open for Jade; edit as they are answered
]
CSS = """
:root{--bg:#f4f1ea;--fg:#1b1a17;--mut:#6b665c;--card:#fffdf8;--line:#ddd6c8;--acc:#c46a12}
@media (prefers-color-scheme: dark){:root{--bg:#141311;--fg:#ece7dc;--mut:#a39d91;--card:#1e1c19;--line:#34302a;--acc:#f08a24}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}
main{max-width:1240px;margin:0 auto;padding:24px 16px 80px}
h1{font-size:24px;margin:0 0 4px} h2{font-size:18px;margin:36px 0 10px;border-bottom:1px solid var(--line);padding-bottom:6px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:10px}
@media (max-width:760px){.pair{grid-template-columns:1fr}}
figure{margin:0} figcaption{font-size:12px;color:var(--mut);margin-bottom:4px}
video{width:100%;border-radius:6px;background:#000}
.note{font-style:italic} .meta{font-size:13px;color:var(--mut)}
.st{display:inline-block;font-size:12px;font-weight:600;padding:1px 8px;border-radius:99px;border:1px solid var(--line)}
.done{color:#2f7d43} .partial,.pending{color:var(--acc)} .q{border-left:3px solid var(--acc);padding-left:10px;margin-top:8px}
"""


def vid(p, label):
    return f'<figure><figcaption>{label}</figcaption><video src="{p}" controls preload="metadata" playsinline></video></figure>'


def main():
    R = json.load(open(os.path.join(ROOT, "docs", "revisions", "review_A.json")))
    os.makedirs(os.path.join(DIR, "before"), exist_ok=True)
    out = [f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>Rewind v3 review (A)</title><style>{CSS}</style></head><body><main>',
           '<h1>Rewind v3: instance A, before / after</h1><p class="meta">Left is the v2 cut, right is v3, each with its audio. '
           'All 540p previews. Instance B (1:34–2:21) has its own page.</p>']
    if OPEN:
        out.append('<h2>Open</h2>')
        out += [f'<div class="card"><b>{html.escape(t)}</b><p>{html.escape(q)}</p></div>' for t, q in OPEN]
    out.append('<h2>Every note</h2>')
    for e in R:
        name = (e.get("after") or "").split("/")[-1]
        a, b = e.get("before_range") or [0, 0]
        before = os.path.join(DIR, "before", name)
        if name and b > a and not os.path.exists(before):
            subprocess.run([FF, "-v", "error", "-y", "-ss", str(a), "-t", f"{b - a:.2f}", "-i", V2, "-c:v", "libx264", "-preset", "veryfast",
                            "-crf", "26", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", before], check=True)
        head = f"{e.get('v2_time') or '—'} · {', '.join(e.get('shots') or [])}"
        out.append(f'<div class="card"><div class="meta">{html.escape(head)} <span class="st {e["status"]}">{e["status"]}</span></div>'
                   f'<p class="note">“{html.escape(e["note"])}”</p><p>{html.escape(e.get("what_changed", ""))}</p>'
                   + (f'<p class="q"><b>Question:</b> {html.escape(e["question"])}</p>' if e.get("question") else "")
                   + ('<div class="pair">' + (vid("before/" + name, "v2 before") if os.path.exists(before) else "<div></div>")
                      + vid(name, "v3 after") + "</div>" if name else "") + "</div>")
    out.append("</main></body></html>")
    open(os.path.join(DIR, "index.html"), "w").write("\n".join(out))
    print("wrote", os.path.relpath(os.path.join(DIR, "index.html"), ROOT))


if __name__ == "__main__":
    main()
