"""Napoleon v5: lay SFX for the 6 insert close-ups on top of the v4 mix (voice untouched, no re-timing).
usage: python -I scripts/napoleon_inserts_sfx.py public/napoleon/mix_v4.wav public/napoleon/mix.wav
Whoosh on every new cut + a hit per insert (seal thud, musket click, wheel rattle, carrot pluck, bell dings).
Frames are the composition frames at 30 fps (story.ts INSERTS)."""
import sys, wave
import numpy as np

src, dst = sys.argv[1], sys.argv[2]
w = wave.open(src); sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
x = np.frombuffer(w.readframes(n), np.int16).reshape(-1, ch).astype(np.float64) / 32768.0
w.close()
rng = np.random.default_rng(5)
T = lambda d: np.arange(int(sr * d)) / sr
def lp(s, k):  # cheap one-pole low-pass, k passes
    for _ in range(k):
        s = np.concatenate([[s[0]], 0.5 * (s[1:] + s[:-1])])
    return s
def whoosh(d=0.32):
    t = T(d); nz = rng.standard_normal(len(t)); env = np.sin(np.pi * t / d) ** 2
    return lp(nz, 3) * env * 0.5
def thud():
    t = T(0.35); return (np.sin(2 * np.pi * (70 + 50 * np.exp(-t * 30)) * t) * np.exp(-t * 12) + lp(rng.standard_normal(len(t)), 6) * np.exp(-t * 35) * 0.4) * 0.9
def click():
    t = T(0.06); return lp(rng.standard_normal(len(t)), 1) * np.exp(-t * 120) * 0.7
def rattle(d=0.67):
    t = T(d); tick = (np.sin(2 * np.pi * 21 * t) > 0.85).astype(float)
    return (lp(rng.standard_normal(len(t)), 2) * (0.25 + 0.5 * tick) + lp(rng.standard_normal(len(t)), 8) * 0.35) * np.minimum(1, (d - t) / 0.12) * 0.55
def pluck():
    t = T(0.3); return np.sin(2 * np.pi * (420 + 260 * np.exp(-t * 18)) * t) * np.exp(-t * 14) * 0.45
def ding():
    t = T(1.2); return sum(a * np.sin(2 * np.pi * f * t) for f, a in [(1180, 1), (2950, 0.45), (4420, 0.2)]) * np.exp(-t * 3.2) * 0.32
def squeaks():
    out = np.zeros(int(sr * 0.6))
    for k in range(5):
        t = T(0.08); s = np.sin(2 * np.pi * np.cumsum(1800 + 300 * k + 900 * t / 0.08) / sr) * np.sin(np.pi * t / 0.08) * 0.22
        i = int(k * 0.1 * sr); out[i:i + len(s)] += s
    return out
sfx = np.zeros(len(x))
def put(frame, s, gain=1.0, lead=0.0):
    i = max(0, int((frame / 30 - lead) * sr)); j = min(len(sfx), i + len(s)); sfx[i:j] += s[: j - i] * gain
for f in [279, 447, 468, 575, 1016, 1174, 1301, 1318]:  # new cuts (insert in/out)
    put(f, whoosh(), 0.55, lead=0.16)
put(285, thud(), 1.0)            # seal stamp hits at 0.2 s
put(450, squeaks(), 0.8)         # crammed crate
put(577, click(), 0.9); put(581, click(), 0.7)  # muskets cock
put(996, rattle(), 0.8)          # wheels spinning in place
put(1176, pluck(), 0.8)          # carrot on a string
put(1303, ding(), 0.9); put(1311, ding(), 0.6)  # dinner bell
y = x + sfx[:, None] * 0.5
peak = np.abs(y).max(); lim = 10 ** (-1.0 / 20)
if peak > lim:  # gentle overall trim to keep the -1 dBFS ceiling (voice stays gain-only)
    y *= lim / peak
o = wave.open(dst, "wb"); o.setnchannels(ch); o.setsampwidth(2); o.setframerate(sr)
o.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()); o.close()
print(f"wrote {dst}: {len(y) / sr:.3f} s, peak in {20 * np.log10(np.abs(x).max()):.2f} dBFS -> out {20 * np.log10(np.abs(y).max()):.2f} dBFS")
