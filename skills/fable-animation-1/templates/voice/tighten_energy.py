"""Cut pauses by the real silence in the waveform (whisper's word edges are too loose to cut on), then remap words.json.
usage: python -I voice/tighten_energy.py <voice.wav> <words.json> <out voice.wav> <out words.json> [max gap s] [word index:gap s,...]
A silence longer than the max gap loses its middle. "word index:gap" keeps a longer (dramatic) pause right before that word."""
import json, sys
import numpy as np
sys.path.insert(0, "audio")
from dsp import read_wav, write_wav, SR

src, wfile, out_wav, out_words = sys.argv[1:5]
G = float(sys.argv[5]) if len(sys.argv) > 5 else 0.14
SPECIAL = {int(a): float(b) for a, b in (p.split(":") for p in sys.argv[6].split(","))} if len(sys.argv) > 6 else {}
x, sr = read_wav(src); assert sr == SR
m = x.mean(0)
W = json.load(open(wfile, encoding="utf-8"))
hop = int(0.005 * SR)
n = len(m) // hop
rms = np.sqrt((m[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9
db = 20 * np.log10(rms)
gate = db.max() - 42                                        # below this is room tone
loud = db > gate
# close tiny holes inside words (stops, short gaps under 60 ms are speech)
i = 0
while i < n:
    if not loud[i]:
        j = i
        while j < n and not loud[j]: j += 1
        if (j - i) * 0.005 < 0.06 and i > 0: loud[i:j] = True
        i = j
    else: i += 1
sil, i = [], 0
while i < n:
    if not loud[i]:
        j = i
        while j < n and not loud[j]: j += 1
        sil.append((i * 0.005, j * 0.005)); i = j
    else: i += 1
def want(a, b):
    for k, g in SPECIAL.items():                            # the silence that ends at (or just before) word k's start
        if a - 0.25 <= W[k]["s"] <= b + 0.25: return g
    return G
cuts = []
for a, b in sil:
    g = want(a, b) if a > 0 else 0.03
    if b - a > g:
        pre = min(g * 0.6, 0.09) if a > 0 else 0.03          # keep the breath tail after the word, the rest before the next
        cuts.append((a + pre, b - (g - pre)))
F = int(0.012 * SR)
pieces, p0 = [], 0
for c0, c1 in cuts:
    s0, s1 = int(c0 * SR), int(c1 * SR)
    seg = m[p0:s0].copy()
    if len(seg) > F: seg[-F:] *= np.linspace(1, 0, F)
    if p0 and len(seg) > F: seg[:F] *= np.linspace(0, 1, F)
    pieces.append(seg); p0 = s1
tail = m[p0:].copy(); tail[:F] *= np.linspace(0, 1, F); pieces.append(tail)
y = np.concatenate(pieces)
def remap(t):
    d = 0.0
    for c0, c1 in cuts:
        if t >= c1: d += c1 - c0
        elif t > c0: return c0 - d
    return t - d
out = [{**w, "s": round(remap(w["s"]), 3), "e": round(remap(w["e"]), 3)} for w in W]
write_wav(out_wav, np.stack([y, y]))
json.dump(out, open(out_words, "w", encoding="utf-8"), indent=0)
print(f"gate {gate:.1f} dB; {len(sil)} silences, {len(cuts)} cut; voice {len(m) / SR:.2f} s -> {len(y) / SR:.2f} s")
