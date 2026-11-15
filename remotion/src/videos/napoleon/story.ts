// Napoleon vs Bunnies: 24 shots timed to the recorded voice (words.json, untouched), eye-level camera grammar
// (smootherstep glides, slow push-ins, close-ups on punch lines), per-shot set + light + depth of field.
import WORDS from "./words.json";
export const FPS = 30;
export const TOTAL = 1338; // 44.6 s
export type V3 = [number, number, number];
export type Light = "day" | "golden";
export type SetName = "field" | "map" | "tent" | "farm";
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const glide = (u: number) => { const x = clamp01(u); return x * x * x * (x * (6 * x - 15) + 10); };
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const back = (x: number, s = 1.7) => { const u = clamp01(x) - 1; return u * u * ((s + 1) * u + s) + 1; };
export const lerp3 = (a: V3, b: V3, t: number): V3 => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];

/** words: [start s, end s, word] */
export const W = WORDS as [number, number, string][];
/** frame where word k starts, minus 2 frames lead */
export const C = (k: number) => Math.max(0, Math.round(W[k][0] * FPS) - 2);

// world x slots per set (skill rule: each location in its own slot)
export const SLOT: Record<SetName, number> = { field: 0, map: 400, tent: 800, farm: 1200 };

export type Cam = { pos: V3; look: V3; fov: number; roll: number };
export type ShotDef = { id: number; a: number; b: number; set: SetName; light: Light; cInf: number; cam: (f: number) => Cam; focus?: V3 };
const F = (s: number) => Math.round(s * FPS);
/** hold-shot drift (v4: push x1.5, arc 3 % of the subject distance / s; v5 raised for pacing_check MAD) */
const HOLD_PUSH = 3.0, HOLD_ARC = 0.12;
/** a held shot that pushes in toward its look point at `rate` per second (skill: ~4.5 %/s, punch <= 18 %/s) */
const hold = (a: number, pos: V3, look: V3, rate = 0.045, fov = 40, roll = 0) => (f: number): Cam => {
  // push-in (x1.5 after the v3 pacing check: median MAD 7.2 < 15) + a slow sideways arc so held shots never freeze
  const t = Math.max(0, (f - a) / FPS), k = Math.min(0.6, rate * HOLD_PUSH * t);
  const d = Math.hypot(look[0] - pos[0], look[2] - pos[2]), side = Math.sin(a * 12.9898) > 0 ? 1 : -1;
  const arc = side * d * HOLD_ARC * smooth(t / 2.2) * 2.2;
  const p = lerp3(pos, look, k * 0.5);
  return { pos: [p[0] + arc, p[1], p[2]], look, fov, roll };
};
/** a glide from one framing to another over [g0, g0+dur] frames (smootherstep), with a slow push after */
const move = (a: number, p0: V3, l0: V3, p1: V3, l1: V3, g0: number, dur = 26, fov = 40) => (f: number): Cam => {
  const u = glide((f - g0) / dur);
  return { pos: lerp3(p0, p1, u), look: lerp3(l0, l1, u), fov, roll: 0 };
};
const track = (a: number, b: number, p0: V3, l0: V3, p1: V3, l1: V3, fov = 40) => (f: number): Cam => {
  const u = smooth((f - a) / (b - a)) * 0.15 + ((f - a) / (b - a)) * 0.85;
  return { pos: lerp3(p0, p1, u), look: lerp3(l0, l1, u), fov, roll: 0 };
};
const M = SLOT.map, T = SLOT.tent, R = SLOT.farm;
/** shot 19 opens on the wheels spinning in place (insert) before the carriage moves */
export const WHEEL_F = 20;
// shot boundaries (frames) = the phrase/word starts of the recorded voice (same cut points as preview v1)
const B = [0, 35, 87, 143, 198, 246, 300, 378, 429, 489, 533, 593, 654, 716, 762, 810, 876, 915, 996, 1068, 1097, 1148, 1203, 1275, TOTAL];
const S = (i: number, set: SetName, light: Light, cInf: number, cam: (a: number, b: number) => (f: number) => Cam, focus?: V3): ShotDef =>
  ({ id: i + 1, a: B[i], b: B[i + 1], set, light, cInf, cam: cam(B[i], B[i + 1]), focus });
export const SHOTS: ShotDef[] = [
  // 1 "Napoleon conquered…" hero by the camp flag
  S(0, "field", "day", 4, (a) => hold(a, [0.35, 1.0, 3.1], [0, 1.02, 0], 0.06)),
  // 2 "…half of Europe" war map on its easel, red spreading
  S(1, "map", "day", 2, (a) => hold(a, [M, 1.32, 1.75], [M, 1.32, -0.5], 0.05)),
  // 3 "But he lost one battle…" close-up, smug -> worried
  S(2, "field", "day", 13, (a) => hold(a, [6.25, 1.22, 3.75], [6, 1.2, 2], 0.05)),
  // 4 "…to bunnies." one bunny pops up, eye level
  S(3, "field", "day", 13, (a) => hold(a, [8.1, 0.33, 5.05], [8, 0.22, 4], 0.08)),
  // 5 "In 1807, after signing…" treaty insert, quill + seal
  S(4, "tent", "day", 12, (a) => hold(a, [T + 0.05, 1.28, 0.62], [T, 0.86, 0.02], 0.04)),
  // 6 "…a big peace treaty" handshake with the Tsar
  S(5, "tent", "day", 7, (a) => hold(a, [T, 1.25, 3.4], [T, 1.05, -0.7], 0.05)),
  // 7 "Napoleon wanted to celebrate with a rabbit hunt" musket up, thought bubble
  S(6, "field", "day", 8, (a) => hold(a, [12.35, 1.12, 3.0], [12, 1.1, 0], 0.045)),
  // 8 "So his chief of staff…" Berthier with his list
  S(7, "field", "day", 9, (a) => hold(a, [16.25, 1.2, 3.25], [16, 1.15, 1], 0.05)),
  // 9 "…rounded up hundreds of rabbits" rows of crates, truck right
  S(8, "field", "day", 4, (a, b) => track(a, b, [36.5, 0.95, 1.4], [37.5, 0.42, -2.6], [42.5, 0.95, 1.4], [43.5, 0.42, -2.6])),
  // 10 "The cages opened." door swings open, eye level
  S(9, "field", "day", 12, (a) => hold(a, [40.05, 0.48, 1.35], [40, 0.42, 0], 0.07)),
  // 11 "The hunters raised their guns." line of three, aim
  S(10, "field", "day", 7, (a) => hold(a, [24, 1.2, 4.3], [24, 1.05, -0.3], 0.05)),
  // 12 "And the rabbits didn't run away." rabbits sit, Napoleon confused behind
  S(11, "field", "day", 6, (a) => hold(a, [30, 0.9, 7.6], [30, 0.6, 0], 0.04)),
  // 13 "They ran straight at Napoleon!" side tracking charge
  S(12, "field", "day", 4, (a, b) => track(a, b, [30.1, 0.85, 4.4], [31.15, 0.62, 0], [30.85, 0.85, 4.2], [31.75, 0.66, 0])),
  // 14 "Hundreds of them swarmed…" swarm, arms up
  S(13, "field", "day", 7, (a) => hold(a, [32, 1.1, 3.3], [32, 1.0, 0], 0.08)),
  // 15 "…climbed up his legs." close-up, bunny on the hat
  S(14, "field", "day", 13, (a) => hold(a, [32.08, 1.55, 2.0], [32, 1.52, 0], 0.06)),
  // 16 "His men swung whips and sticks." wide two-shot
  S(15, "field", "day", 7, (a) => hold(a, [35.2, 1.1, 4.4], [35.2, 0.9, -0.3], 0.04)),
  // 17 "Nothing worked." deadpan, buried
  S(16, "field", "day", 11, (a) => hold(a, [32, 1.15, 2.45], [32, 1.08, 0], 0.03)),
  // 18 "The great emperor retreated to his carriage…" run, tracking
  S(17, "field", "golden", 4, (a, b) => track(a, b, [41, 1.05, 8.5], [41, 0.9, 1], [60, 1.05, 8.5], [61, 0.9, 1])),
  // 19 "…and the rabbits chased him there too." carriage flees, tracking (starts after the wheel-spin insert, same speed)
  S(18, "field", "golden", 4, (a, b) => track(a + WHEEL_F, b + WHEEL_F, [63, 1.1, 9.5], [64, 0.9, 0], [76, 1.1, 9.5], [77, 0.9, 0])),
  // 20 "Why?" one bunny, head tilt
  S(19, "farm", "day", 13, (a) => hold(a, [R + 3.05, 0.33, 4.0], [R + 3, 0.22, 3], 0.05)),
  // 21 "They weren't wild rabbits." a scruffy wild hare at the forest edge
  S(20, "field", "day", 13, (a) => hold(a, [-20, 0.42, -56.9], [-20, 0.4, -58], 0.05)),
  // 22 "They were tame farm rabbits." farmer feeding a hutch full of bunnies
  S(21, "farm", "day", 8, (a) => hold(a, [R, 1.0, 4.2], [R, 0.8, 0], 0.045)),
  // 23 "And when they saw a man walking toward them…" bunny-eye view, Napoleon approaches
  S(22, "farm", "golden", 6, (a) => hold(a, [R + 6, 0.32, 10.2], [R + 6, 0.62, 0], 0.03)),
  // 24 "…they thought it was dinner time." napkins on, dinner bell
  S(23, "farm", "golden", 9, (a, b) => { const h = hold(a, [R + 6, 0.62, 6.6], [R + 6, 0.5, 3.6], 0.05); return (f: number) => {
    const c = h(f), k = back((f - (b - 20)) / 6) * 0.22; return { ...c, pos: lerp3(c.pos, c.look, k) }; }; }),
];
// Quick insert close-ups (< 1 s, hard cut in/out) on key words, inside their shot: same set, light and staging.
// v4 pacing_check median MAD was below 15; these add a cut + a new framing on the words the script leans on.
export type Insert = { key: string; shot: number; a: number; b: number; cInf: number; cam: (f: number) => Cam };
const ins = (key: string, shot: number, a: number, b: number, pos: V3, look: V3, cInf = 12, rate = 0.1): Insert => ({ key, shot, a, b, cInf, cam: hold(a, pos, look, rate) });
export const INSERTS: Insert[] = [
  // "treaty," wax seal stamped beside the signature (to the cut)
  ins("seal", 6, C(19), B[6], [T + 0.16, 1.1, 0.66], [T + 0.16, 0.86, 0.13], 13),
  // "hundreds" one crate, bunnies behind the bars
  ins("hundreds", 9, C(35), C(35) + 21, [38.5, 0.32, -0.7], [38.5, 0.3, -2], 12),
  // "guns." raised muskets (to the cut)
  ins("guns", 11, C(45), B[11], [24.55, 1.02, 1.6], [24.55, 0.98, -0.45], 12),
  // shot 19 opens on the near rear wheel spinning in place, dust kicking up
  ins("wheel", 19, B[18], B[18] + WHEEL_F, [63.3, 0.62, 3.6], [63.1, 0.62, 1.4], 12, 0.08),
  // "farm" a carrot dangles over a bunny (to the cut)
  ins("carrot", 22, C(98), B[22], [R - 0.33, 0.3, 1.55], [R - 0.37, 0.25, 0.55], 13),
  // "dinner" the dinner bell rings, cut back for the final punch-in
  ins("bell", 24, C(113) - 2, B[24] - 20, [R + 6.9, 1.03, 5.3], [R + 6.9, 1.0, 4.4], 13),
];
export const insertAt = (f: number) => INSERTS.find((i) => f >= i.a && f < i.b);
export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];
export const layersAt = (f: number): { id: number; alpha: number }[] => [{ id: shotAt(f).id, alpha: 1 }];
export const camAt = (id: number, f: number): Cam => { const i = insertAt(f); return i && i.shot === id ? i.cam(f) : SHOTS[id - 1].cam(f); };
export const dofAt = (f: number) => { const s = shotAt(f), i = insertAt(f); return { cInf: i ? i.cInf : s.cInf, focus: !i && s.focus ? (_f: number) => s.focus as V3 : undefined }; };
/** seconds since the shot started */
export const lt = (id: number, f: number) => (f - SHOTS[id - 1].a) / FPS;
