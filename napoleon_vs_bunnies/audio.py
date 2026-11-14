import numpy as np, wave, math, json
from sfxlib import *
import render as R
sfx = np.zeros((N, 2)); amb = np.zeros((N, 2)); mus = np.zeros((N, 2))
P = place
def squeak(f=1900, d=0.09):
    t = tt(d); return np.sin(2 * np.pi * np.cumsum(f + 900 * t / d) / SR) * np.sin(np.pi * t / d) * 0.45
def chirp(f=3200):
    t = tt(0.12); return np.sin(2 * np.pi * np.cumsum(f + 1400 * np.sin(np.pi * t / 0.12)) / SR) * np.sin(np.pi * t / 0.12) * 0.25
def cricket(d):
    t = tt(d); x = np.sin(2 * np.pi * 4600 * t) * (np.sin(2 * np.pi * 28 * t) > 0.3) * (np.sin(2 * np.pi * 1.6 * t) > -0.2)
    return lp(x, 2) * 0.12 * np.minimum(1, np.minimum(t / 0.1, (d - t) / 0.1))
def tap():
    t = tt(0.09); return lp(lp(noise(0.09), 4) * np.exp(-t * 80) + np.sin(2 * np.pi * 160 * t) * np.exp(-t * 60), 3) * 0.7
def hop_thud():
    t = tt(0.12); return lp(np.sin(2 * np.pi * 120 * t) * np.exp(-t * 45) + lp(noise(0.12), 8) * np.exp(-t * 60) * 0.4, 3) * 0.5
def stamp_hit():
    t = tt(0.5); return lp(np.sin(2 * np.pi * (60 + 40 * np.exp(-t * 30)) * t) * np.exp(-t * 9) + lp(noise(0.5), 8) * np.exp(-t * 25) * 0.5, 3)
def creak():
    t = tt(0.55); f = 180 + 60 * np.sin(2 * np.pi * 2.3 * t)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (np.sin(2 * np.pi * 31 * t) > 0)
    return lp(x, 6) * np.sin(np.pi * t / 0.55) * 0.35
def cock():
    return click() * 0.8
def sparkle():
    out = np.zeros(int(SR * 0.6))
    for k in range(5):
        c = ting(2200 + k * 300)[:int(SR * 0.4)]; i = int(k * 0.05 * SR); out[i:i + len(c)] += c[:len(out) - i] * 0.5
    return out
def flutter(d):
    t = tt(d); return lp(noise(d), 3) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * t)) * 0.12
def munch(): return chomp() * 1.2
# --- whoosh on every cut
for c in R.CUTS: P(sfx, whoosh(0.35), c - 0.17, 0.45, 0.2 * math.sin(c))
# --- ambience beds
for s in R.SH:
    a, b = s['t0'], s['t1']
    if s['bg'] in ('meadow', 'farm'):
        rr = np.random.default_rng(int(a * 10))
        tt_ = a + rr.uniform(0.1, 0.6)
        while tt_ < b - 0.2:
            P(amb, chirp(rr.uniform(2800, 3800)), tt_, 0.5, rr.uniform(-0.6, 0.6)); P(amb, chirp(rr.uniform(3000, 4000)), tt_ + 0.14, 0.4, 0.3)
            tt_ += rr.uniform(0.7, 1.4)
        P(amb, lp(noise(b - a), 40) * 0.25, a, 0.5)
    elif s['bg'] == 'tent':
        P(amb, lp(noise(b - a), 80) * 0.5, a, 0.6)
P(amb, cricket(1.3), 29.2, 1.0); P(amb, cricket(1.9), 19.85, 0.6)
# --- per-shot effects
P(sfx, flutter(1.15), 0.0, 0.8)
for nm, t0 in R.CONQ: P(sfx, pop(520 + 60 * R.CONQ.index((nm, t0))), 1.15 + t0, 0.55)
P(sfx, stamp_hit(), 2.42, 1.0); P(sfx, impact(0.6, 70), 2.42, 0.5)
P(sfx, tick(), 3.65, 0.6); P(sfx, tick(), 4.1, 0.6); P(sfx, squeak(2600, 0.05) * 0.4, 3.72, 0.4)
P(sfx, boing(), 4.83, 0.7); P(sfx, sparkle(), 5.1, 0.5); P(sfx, squeak(), 5.7, 0.6)
for k in range(9): P(sfx, chalk(), 6.8 + k * 0.13, 0.7)
P(sfx, thunk(), 8.55, 0.6); P(sfx, tap(), 8.62, 0.5)
P(sfx, soft := lp(whoosh(0.3), 4), 10.3, 0.6); P(sfx, cock(), 10.6, 0.9); P(sfx, pop(700), 11.9, 0.6)
P(sfx, lp(whoosh(0.25), 3), 12.82, 0.6); P(sfx, tap(), 12.92, 0.9); P(sfx, tap(), 12.98, 0.7)
for k in range(10): P(sfx, squeak(rnd.uniform(1700, 2600), 0.07), 14.5 + k * 0.17, 0.25, rnd.uniform(-0.7, 0.7))
P(sfx, pop(620), 15.25, 0.7)
P(sfx, creak(), 16.55, 0.9); P(sfx, click(), 16.58, 0.6); P(sfx, squeak(), 17.1, 0.6)
for k in (18.1, 18.2, 18.02): P(sfx, cock(), k, 0.8, rnd.uniform(-0.5, 0.5))
P(sfx, squeak(2200, 0.06), 20.4, 0.4)
P(sfx, rumble(5.0) * 0.8, 21.85, 0.7); P(sfx, ting(1500), 22.0, 0.5)
for k in np.arange(21.9, 26.9, 0.21): P(sfx, hop_thud(), k + rnd.uniform(0, 0.05), 0.45, rnd.uniform(-0.6, 0.6))
for k in range(14): P(sfx, squeak(rnd.uniform(1800, 2800), 0.07), 22.0 + k * 0.33, 0.35, rnd.uniform(-0.7, 0.7))
P(sfx, thunk(), 23.95, 0.7); P(sfx, impact(0.5, 80), 24.65, 0.5)
for k in np.arange(24.0, 25.4, 0.2): P(sfx, lp(whoosh(0.18), 3), k, 0.3)
P(sfx, boing(), 25.45, 0.6); P(sfx, squeak(2400, 0.06), 26.3, 0.4)
for k, t0 in enumerate((27.3, 27.9, 28.5)):
    P(sfx, lp(whoosh(0.22), 2), t0 - 0.12, 0.7); P(sfx, thunk(), t0, 0.8); P(sfx, boing(), t0 + 0.05, 0.4)
P(sfx, tick(), 29.9, 0.4)
for k in np.arange(30.6, 33.1, 0.14): P(sfx, tap(), k, 0.6, 0.3 * math.sin(k * 20))
P(sfx, rumble(2.6) * 0.6, 30.5, 0.5)
P(sfx, knock(), 33.25, 0.9) if 'knock' in dir() else P(sfx, thunk(), 33.25, 0.9)
P(sfx, engine(2.4, 22) * 0.8, 33.2, 0.5); P(sfx, rumble(2.4) * 0.5, 33.2, 0.5); P(sfx, pop(680), 34.2, 0.6)
P(sfx, ting(1200), 35.75, 0.6)
P(sfx, lp(whoosh(0.15), 2), 37.3, 0.8); P(sfx, lp(whoosh(0.15), 2), 37.45, 0.8); P(sfx, stamp_hit() * 0.6, 37.46, 0.5)
P(sfx, sparkle(), 38.4, 0.4); P(sfx, munch(), 39.0, 0.6); P(sfx, munch(), 39.35, 0.6)
for k in np.arange(40.2, 42.4, 0.45): P(sfx, tap(), k, 0.7)
for k in (40.5, 40.65, 40.8): P(sfx, tick(), k, 0.5)
P(sfx, bell(880, 1.5) if 'bell' in dir() else ting(880), 42.6, 0.6); P(sfx, pop(700), 42.65, 0.6)
for k in (43.0, 43.25, 43.5, 43.75): P(sfx, munch(), k, 0.6, rnd.uniform(-0.5, 0.5))
P(sfx, sparkle(), 43.9, 0.5)
# --- music: pizzicato march, 108 bpm, C G Am F
bpm = 108; q = 60 / bpm; e = q / 2
def pizz(f, d=0.35):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + 0.45 * np.sin(4 * np.pi * f * t) + 0.2 * np.sin(6 * np.pi * f * t)) * np.exp(-t * 11) * np.minimum(1, t / 0.003)
def snare(): t = tt(0.15); return lp(noise(0.15), 2) * np.exp(-t * 30) * 0.5 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 40) * 0.3
def tamb(): t = tt(0.08); return noise(0.08) * np.exp(-t * 60) * 0.25
chords = [(130.81, [523.25, 659.26, 783.99]), (98.0, [493.88, 587.33, 783.99]), (110.0, [523.25, 659.26, 880.0]), (87.31, [523.25, 698.46, 880.0])]
mel = [0, 1, 2, 1, 0, 2, 1, 0]
def march(a, b, g=1.0, drums=True):
    k = 0; t = a
    while t < b - 0.01:
        bar = int(k // 8) % 4; root, ch = chords[bar]
        if k % 2 == 0: P(mus, pizz(root, 0.4), t, 0.7 * g, -0.2)
        if k % 2 == 1: P(mus, pizz(root * 1.5, 0.3), t, 0.45 * g, -0.2)
        P(mus, pizz(ch[mel[k % 8]] * (2 if (k // 16) % 2 and k % 4 == 3 else 1), 0.25), t, 0.42 * g, 0.25)
        if drums:
            if k % 4 == 2: P(mus, lp(snare(), 2), t, 0.35 * g)
            P(mus, tamb(), t, 0.25 * g, 0.4)
        t += e; k += 1
march(0.0, 29.2)
march(30.45, 35.55, 1.0)
march(36.5, 42.45, 0.8, drums=False)
march(42.5, 44.0, 1.0)
t = tt(0.9); P(mus, sum(pizz(f, 0.9) for f in (130.81, 523.25, 659.26, 783.99)), 44.0, 1.0)
def verb(x, dec=0.3, dl=(0.031, 0.047, 0.061, 0.083)):
    y = x.copy()
    for d in dl:
        k = int(d * SR); z = np.zeros_like(x); z[k:] = x[:-k] * dec; y += z
    return y
mus = verb(mus, 0.25); sfx = verb(sfx + amb * 0.6, 0.18)
def wr(fn, x):
    w = wave.open(fn, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    x = x / (np.abs(x).max() + 1e-9) * 0.9; w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()
wr('music.wav', mus); wr('sfx.wav', sfx); print('ok')
