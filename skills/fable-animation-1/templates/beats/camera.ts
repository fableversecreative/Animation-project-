// Beat camera engine, SLOW edition (2026-11-04). Drop-in replacement for the camera section of story.ts
// (the block from `export type Cam` to `runBeats`, plus `VAR` / `auto`) in a short copied from src/videos/jang or edo.
// Why: the Jang short measured 2x too fast against the reference (scripts/cam_speed.py: p90 32.6 px/f vs ~17,
// 9 % of frames >= 40 px/f vs ~0) because swoops took 7-14 f, holds pushed 12-35 %/s and orbited 0.3-0.5 rad/s,
// and a new move started every ~1.1 s. Reference numbers: references/reports/motion.md.
// The governor below enforces the reference limits whatever a shot's beats ask for, so a hand-written beat can't
// come out too fast. Pacing (a visual event every <= 1.5 s) comes from cuts, inserts and character actions, not from
// faster camera moves: the hit channels cut more, they do not swing harder.
import { FPS, V3, clamp01 } from "./story";

/** reference limits (motion.md 2.1, 720p px). Edit here, not in the beats. */
export const CAMLIM = {
  swoopDur: 24,      // default ease-in-out move length, frames (reference ~23 f: 10 in / 10 out)
  swoopMin: 18,      // never shorter than this; a bigger change than fits in 18-40 f is a CUT
  gapMin: 45,        // frames between the starts of two non-cut moves (reference ~6 moves per 10 s)
  orbitMax: 0.12,    // rad/s drift around the subject during a hold
  pushDef: 0.045,    // 1/s push-in during a hold (~0.15 %/f, the reference quiet-frame median 0.14 %/f)
  pushMax: 0.09,     // 1/s cap for ordinary beats (~0.3 %/f, reference p75 0.34 %/f)
  pushPunch: 0.18,   // 1/s on beats flagged punch (~0.6 %/f for ~35 f on punch words)
  liftMax: 0.4,      // m/s crane during a hold
  rollMax: 0.08,     // rad (4.6 deg) on calm beats; punch beats may roll 0.14 (8 deg)
};

export type Cam = { pos: V3; look: V3; fov: number; roll: number };
/** a framing in orbit space around `look`; holds keep moving gently: orbit (rad/s), push (1/s), lift (m/s) */
export type Frame = { look: V3 | ((f: number) => V3); d: number; az: number; dy: number; fov?: number; roll?: number; orbit?: number; push?: number; lift?: number };
export type Beat = Frame & { f: number; dur?: number; cut?: boolean; dof?: number; punch?: boolean };
export const glide = (u: number) => { const x = clamp01(u); return x * x * x * (x * (6 * x - 15) + 10); };
type P = { look: V3; d: number; az: number; dy: number; fov: number; roll: number };
const cl = (v: number, m: number) => Math.max(-m, Math.min(m, v));
const evalB = (b: Beat, f: number): P => {
  const t = Math.max(0, f - b.f) / FPS, look = typeof b.look === "function" ? b.look(f) : b.look;
  const push = b.push === undefined ? CAMLIM.pushDef : Math.min(b.push, b.punch ? CAMLIM.pushPunch : CAMLIM.pushMax);
  return { look, d: b.d * Math.exp(-push * t), az: b.az + cl(b.orbit ?? 0, CAMLIM.orbitMax) * t, dy: b.dy + cl(b.lift ?? 0, CAMLIM.liftMax) * t,
    fov: b.fov ?? 40, roll: cl(b.roll ?? 0, b.punch ? 0.14 : CAMLIM.rollMax) };
};
const mixP = (a: P, b: P, k: number): P => {
  let da = b.az - a.az; while (da > Math.PI) da -= 2 * Math.PI; while (da < -Math.PI) da += 2 * Math.PI;
  return { look: a.look.map((v, i) => v + (b.look[i] - v) * k) as V3, d: a.d * Math.pow(b.d / a.d, k), az: a.az + da * k, dy: a.dy + (b.dy - a.dy) * k,
    fov: a.fov + (b.fov - a.fov) * k, roll: a.roll + (b.roll - a.roll) * k };
};
const toCam = (p: P): Cam => ({ pos: [p.look[0] + p.d * Math.sin(p.az), p.look[1] + p.dy, p.look[2] + p.d * Math.cos(p.az)], look: p.look, fov: p.fov, roll: p.roll });
/** governor: moves at least swoopMin long, non-cut moves at least gapMin apart (a too-early move is dropped) */
export const govern = (beats: Beat[]): Beat[] => {
  const out: Beat[] = [];
  let last = -1e9;
  for (const b of [...beats].sort((x, y) => x.f - y.f)) {
    if (!b.cut && out.length && b.f - last < CAMLIM.gapMin) continue;
    out.push({ ...b, dur: Math.max(CAMLIM.swoopMin, b.dur ?? CAMLIM.swoopDur) });
    last = b.f;
  }
  return out;
};
/** start each move half its length early so its fastest frame lands on the cue word */
export const runBeats = (beats: Beat[], f: number): Cam => {
  let cur = evalB(beats[0], f);
  for (let i = 1; i < beats.length; i++) {
    const b = beats[i], d = b.dur ?? CAMLIM.swoopDur, s = b.cut ? b.f : b.f - d / 2;
    if (f < s) break;
    cur = b.cut ? evalB(b, f) : mixP(cur, evalB(b, f), glide((f - s) / d));
  }
  return toCam(cur);
};
/** variations for auto(): gentle swing, crane, push-in, dutch (sizes keep a 24 f move near the ~14 px/f reference peak) */
const VAR = [
  { daz: 0, dk: 1, ddy: 0, dfov: 0, roll: 0.0 },
  { daz: 0.3, dk: 0.85, ddy: -0.2, dfov: -1, roll: 0.04 },
  { daz: -0.25, dk: 1.08, ddy: 0.5, dfov: 1, roll: -0.03 },
  { daz: 0.12, dk: 0.75, ddy: 0.05, dfov: -2, roll: 0.05 },
  { daz: -0.4, dk: 0.95, ddy: -0.3, dfov: 0, roll: -0.04 },
];
/** fill [f0, f1) with gentle beats every `step` frames (default 54 f = 1.8 s) around a base framing */
export const auto = (f0: number, f1: number, base: Frame, o: { step?: number; start?: number; dof?: number; cutFirst?: boolean } = {}): Beat[] => {
  const step = Math.max(CAMLIM.gapMin, o.step ?? 54), out: Beat[] = [];
  let k = o.start ?? 0;
  for (let f = f0; f < f1 - 12; f += step, k++) {
    const v = VAR[k % VAR.length], sgn = k % 2 ? -1 : 1;
    out.push({ ...base, f, cut: f === f0 && o.cutFirst !== false, dur: CAMLIM.swoopDur, az: base.az + v.daz, d: base.d * v.dk, dy: base.dy + v.ddy,
      fov: (base.fov ?? 40) + v.dfov, roll: (base.roll ?? 0) + v.roll, orbit: (base.orbit ?? 0.08) * sgn, push: base.push, dof: o.dof });
  }
  return out;
};
// In story.ts: `const def = (sc, beats) => { CAMS[sc] = govern(beats); }` so every shot goes through the governor.
