"""Placeholder word timings (~3.7 words/s) from the numbered lines of SCRIPT.md, until a real voice is aligned.
Writes [{w, s, e, line, k}] (line 1-based, k = word index in the line), the same shape voice/align.py writes,
so the whole picture can be built and checked before the voice exists. Re-align later and every shot re-times itself.
usage: python -I voice/placeholder_words.py <SCRIPT.md> <out words.json>"""
import json, re, sys, pathlib

script, outw = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
body = script.read_text(encoding="utf-8")
body = body.split("## Script", 1)[1].split("\n## ", 1)[0] if "## Script" in body else body
lines = [m.group(2) for m in re.finditer(r"^(\d+)\. (.+)$", body, re.M)]

WPS = 0.228  # seconds per word
t, out = 0.3, []
for li, text in enumerate(lines, 1):
    for k, w in enumerate(text.split()):
        dur = WPS * (1.25 if len(w) > 8 else 1.0)
        out.append({"w": w, "s": round(t, 3), "e": round(t + dur * 0.9, 3), "line": li, "k": k})
        t += dur
        if w.endswith("..."): pass
        elif w.endswith((".", "!", "?")): t += 0.26
        elif w.endswith(":"): t += 0.25
        elif w.endswith(","): t += 0.12
    t += 0.1
outw.parent.mkdir(parents=True, exist_ok=True)
outw.write_text(json.dumps(out, indent=0), encoding="utf-8")
print(len(out), "words,", round(t, 2), "s")
