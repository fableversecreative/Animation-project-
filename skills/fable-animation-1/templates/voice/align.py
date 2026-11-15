"""Align a recorded voice to a SCRIPT.md (numbered lines "1. ..." under "## Script") and write the words.json
([{w, s, e, line, k}]) that every shot in story.ts is cued from.
Needs: pip install faster-whisper numpy   (first run downloads the 'small.en' model, ~500 MB) and ffmpeg on PATH.
usage: python -I voice/align.py <SCRIPT.md> <voice.wav> <out words.json>
Add spoken forms of numbers/years to NUM below when the script writes them as digits (e.g. "1831": "eighteen thirty one")."""
import difflib, json, re, subprocess, sys, pathlib
import numpy as np
from faster_whisper import WhisperModel

SCRIPT, VOICE, OUTW = (pathlib.Path(a) for a in sys.argv[1:4])

body = SCRIPT.read_text(encoding="utf-8")
body = body.split("## Script", 1)[1].split("\n## ", 1)[0] if "## Script" in body else body
lines = [m.group(2) for m in re.finditer(r"^(\d+)\. (.+)$", body, re.M)]
script = [(li, k, w) for li, text in enumerate(lines, 1) for k, w in enumerate(text.split())]

NUM = {"thirty-six": "thirty six"}
def norm(w):
    w = w.lower().strip(".,:;!?\"'…")
    return NUM.get(w, w).replace("'", "")

# decode with ffmpeg (16 kHz mono float): the PyAV build faster-whisper ships with can mismatch its own reader
pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(VOICE), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
audio = np.frombuffer(pcm, dtype=np.float32)
model = WhisperModel("small.en", device="cpu", compute_type="int8")
segs, _ = model.transcribe(audio, word_timestamps=True, initial_prompt=" ".join(lines))
heard = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]

a = [norm(w) for _, _, w in script]
b = [norm(w) for w, _, _ in heard]
sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
times = [None] * len(script)
for tag, i0, i1, j0, j1 in sm.get_opcodes():
    if tag == "equal":
        for d in range(i1 - i0): times[i0 + d] = (heard[j0 + d][1], heard[j0 + d][2])
    elif tag == "replace" and j1 > j0:
        s0, e1 = heard[j0][1], heard[j1 - 1][2]          # spread the heard span over the script span
        n = i1 - i0
        for d in range(n): times[i0 + d] = (s0 + (e1 - s0) * d / n, s0 + (e1 - s0) * (d + 1) / n)
for i, tm in enumerate(times):                         # fill gaps between known neighbours
    if tm is None:
        prev = next((times[j][1] for j in range(i - 1, -1, -1) if times[j]), 0.0)
        nxt = next((times[j][0] for j in range(i + 1, len(times)) if times[j]), prev + 0.3)
        times[i] = (prev, max(prev + 0.05, (prev + nxt) / 2))
out = [{"w": w, "s": round(s, 3), "e": round(e, 3), "line": li, "k": k} for (li, k, w), (s, e) in zip(script, times)]
OUTW.parent.mkdir(parents=True, exist_ok=True)
OUTW.write_text(json.dumps(out, indent=0), encoding="utf-8")
eq = sum(i1 - i0 for tag, i0, i1, _, _ in sm.get_opcodes() if tag == "equal")
print(f"{len(script)} script words, {len(heard)} heard, {eq} matched exactly; voice ends {out[-1]['e']:.2f} s")
