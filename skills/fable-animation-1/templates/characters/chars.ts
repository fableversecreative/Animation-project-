// FableVerse v5 "Option B" characters (locked design, original): big round shaded head, small dark eyes with heavy
// lids, thick brows, bean torso, trouser legs + chunky boots, thick sleeves with white gloves. Plus bunnies and props.
// Drawn into a 600 x 1000 card (feet at y = 975, centre x = 300); one design unit of the python sheet = K canvas px.
type P2 = [number, number];
const INK = "#2e1a23";
const OL = 7.5;
const rad = (d: number) => (d * Math.PI) / 180;
const hexRgb = (h: string) => { const n = parseInt(h.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
export const shade = (h: string, k: number) => "#" + hexRgb(h).map((v) => Math.max(0, Math.min(255, Math.round(v * k))).toString(16).padStart(2, "0")).join("");
const bez = (a: P2, b: P2, c: P2, n = 12): P2[] => Array.from({ length: n }, (_, i) => { const t = i / (n - 1); return [(1 - t) ** 2 * a[0] + 2 * (1 - t) * t * b[0] + t * t * c[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * b[1] + t * t * c[1]]; });
const circ = (cx: number, cy: number, rx: number, ry: number, n = 56): P2[] => Array.from({ length: n }, (_, i) => { const a = (i / n) * Math.PI * 2; return [cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]; });

/** affine drawer (python rig.D equivalent): design coords -> canvas */
export class Dw {
  constructor(public g: CanvasRenderingContext2D, public m: number[] = [1, 0, 0, 1, 0, 0]) {}
  sub(tx: number, ty: number, s = 1, rot = 0, fx = 1) {
    const c = Math.cos(rot), sn = Math.sin(rot), [a, b, cc, d, e, f] = this.m;
    const A = [c * s * fx, sn * s * fx, -sn * s, c * s, tx, ty]; // column-major 2x3 like canvas
    return new Dw(this.g, [a * A[0] + cc * A[1], b * A[0] + d * A[1], a * A[2] + cc * A[3], b * A[2] + d * A[3], a * A[4] + cc * A[5] + e, b * A[4] + d * A[5] + f]);
  }
  get k() { return Math.sqrt(Math.abs(this.m[0] * this.m[3] - this.m[1] * this.m[2])); }
  tp([x, y]: P2): P2 { const [a, b, c, d, e, f] = this.m; return [a * x + c * y + e, b * x + d * y + f]; }
  private path(pts: P2[], close: boolean) {
    const g = this.g; g.beginPath();
    pts.forEach((p, i) => { const [x, y] = this.tp(p); if (i) g.lineTo(x, y); else g.moveTo(x, y); });
    if (close) g.closePath();
  }
  poly(pts: P2[], fill: string | null, ol: number = OL) {
    const g = this.g; this.path(pts, true);
    if (fill) { g.fillStyle = fill; g.fill(); }
    if (ol > 0) { g.lineWidth = ol * this.k; g.strokeStyle = INK; g.lineJoin = "round"; g.stroke(); }
  }
  ell(cx: number, cy: number, rx: number, ry: number, fill: string | null, ol: number = OL, ang = 0) {
    const pts: P2[] = Array.from({ length: 40 }, (_, i) => { const t = (i / 40) * Math.PI * 2, x = Math.cos(t) * rx, y = Math.sin(t) * ry; return [cx + x * Math.cos(ang) - y * Math.sin(ang), cy + x * Math.sin(ang) + y * Math.cos(ang)]; });
    this.poly(pts, fill, ol);
  }
  line(pts: P2[], col: string, w: number) {
    const g = this.g; g.lineCap = "round"; g.lineJoin = "round"; this.path(pts, false); g.strokeStyle = col; g.lineWidth = w * this.k; g.stroke();
  }
  dot(x: number, y: number, r: number, col: string) { const [X, Y] = this.tp([x, y]); const g = this.g; g.beginPath(); g.arc(X, Y, r * this.k, 0, Math.PI * 2); g.fillStyle = col; g.fill(); }
  /** linear gradient fill: c0 at the light side (angle ang from +x), c1 opposite */
  grad(pts: P2[], c0: string, c1: string, ang = 1.3, ol: number | null = null) {
    const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
    const cx = (Math.min(...xs) + Math.max(...xs)) / 2, cy = (Math.min(...ys) + Math.max(...ys)) / 2, L = Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) / 2;
    const p0 = this.tp([cx - Math.cos(ang) * L, cy - Math.sin(ang) * L]), p1 = this.tp([cx + Math.cos(ang) * L, cy + Math.sin(ang) * L]);
    const gr = this.g.createLinearGradient(p0[0], p0[1], p1[0], p1[1]); gr.addColorStop(0, c0); gr.addColorStop(1, c1);
    this.path(pts, true); this.g.fillStyle = gr; this.g.fill();
    if (ol) this.poly(pts, null, ol);
  }
}

// ---------------- the cast ----------------
export type Who = "napoleon" | "berthier" | "tsar" | "hunter" | "hunter2" | "farmer" | "soldier" | "soldier2" | "drummer";
type Look = { coat: string; front: string; pants: string; boot: string; hat: string; epaul?: boolean; forelock?: boolean; tache?: string; sash?: string;
  sideburns?: string; beard?: string; strap?: string; stubble?: boolean; straw?: boolean; overall?: boolean; skin?: string };
export const WHO: Record<Who, Look> = {
  napoleon: { coat: "#2b4a9a", front: "#f1ede3", pants: "#f2eee4", boot: "#1d1a22", hat: "bicorne", epaul: true, forelock: true },
  berthier: { coat: "#22397a", front: "#e8c25a", pants: "#f2eee4", boot: "#1d1a22", hat: "bicorne_w", epaul: true, tache: "#3a2a20", sash: "#c8323a" },
  tsar: { coat: "#eef0f4", front: "#3f6fb8", pants: "#2f4a3a", boot: "#1d1a22", hat: "plume", epaul: true, sash: "#3f78c8", sideburns: "#c9a060" },
  hunter: { coat: "#5a7a3a", front: "#c9b48a", pants: "#d8c9a2", boot: "#4a3324", hat: "tricorne", beard: "#6a4a30", strap: "#6a4a2e" },
  hunter2: { coat: "#8a3a2e", front: "#d8c9a2", pants: "#d8c9a2", boot: "#4a3324", hat: "tricorne", tache: "#4a3020", strap: "#6a4a2e" },
  farmer: { coat: "#3e6aa8", front: "#e9e2d0", pants: "#3e5f8f", boot: "#4a3324", hat: "straw", stubble: true, straw: true, overall: true },
  soldier: { coat: "#2b4a9a", front: "#f1ede3", pants: "#f2eee4", boot: "#1d1a22", hat: "shako", strap: "#f1ede3" },
  soldier2: { coat: "#2b4a9a", front: "#f1ede3", pants: "#f2eee4", boot: "#1d1a22", hat: "shako", tache: "#3a2a20", strap: "#f1ede3" },
  drummer: { coat: "#c8323a", front: "#f1ede3", pants: "#f2eee4", boot: "#1d1a22", hat: "shako" },
};
export type Emo = "sly" | "neutral" | "proud" | "smug" | "worried" | "scared" | "shocked" | "angry" | "sad" | "deadpan" | "happy" | "determined" | "confused" | "excited";
type EmoP = { lid: [number, number]; tilt: number; brow: [number, number]; bang: [number, number]; mouth: string; eye: number; look?: P2; sweat?: boolean; ring?: boolean; lines?: boolean; happy?: boolean; chin?: number };
export const EMO: Record<Emo, EmoP> = {
  sly: { lid: [0.55, 0.3], tilt: 0.35, brow: [-0.3, 0.6], bang: [0.7, -0.2], mouth: "smirk", eye: 1, look: [0.6, 0] },
  neutral: { lid: [0.45, 0.45], tilt: 0, brow: [0, 0], bang: [0.1, 0.1], mouth: "line", eye: 1 },
  proud: { lid: [0.55, 0.55], tilt: -0.2, brow: [0.35, 0.35], bang: [-0.2, -0.2], mouth: "smirk", eye: 1 },
  smug: { lid: [0.6, 0.48], tilt: 0.15, brow: [-0.05, 0.45], bang: [0.35, -0.3], mouth: "smirk", eye: 1, look: [0.5, 0] },
  worried: { lid: [0.12, 0.12], tilt: -0.5, brow: [0.5, 0.5], bang: [-0.9, -0.9], mouth: "wavy", eye: 1.1, sweat: true },
  scared: { lid: [0, 0], tilt: -0.3, brow: [0.9, 0.9], bang: [-0.7, -0.7], mouth: "open", eye: 1.3, sweat: true, ring: true },
  shocked: { lid: [0, 0], tilt: 0, brow: [1, 1], bang: [-0.1, -0.1], mouth: "o", eye: 1.35, ring: true, lines: true },
  angry: { lid: [0.4, 0.4], tilt: 0.6, brow: [-0.45, -0.45], bang: [1, 1], mouth: "grit", eye: 0.95 },
  sad: { lid: [0.45, 0.45], tilt: -0.6, brow: [0.2, 0.2], bang: [-1, -1], mouth: "frown", eye: 1, look: [0, 0.4] },
  deadpan: { lid: [0.6, 0.6], tilt: 0, brow: [-0.1, -0.1], bang: [0, 0], mouth: "line", eye: 1 },
  happy: { lid: [0.3, 0.3], tilt: -0.1, brow: [0.45, 0.45], bang: [-0.2, -0.2], mouth: "grin", eye: 1, happy: true },
  excited: { lid: [0, 0], tilt: 0, brow: [0.9, 0.9], bang: [-0.3, -0.3], mouth: "grin", eye: 1.2 },
  determined: { lid: [0.5, 0.5], tilt: 0.4, brow: [-0.3, -0.3], bang: [0.8, 0.8], mouth: "line", eye: 1 },
  confused: { lid: [0.2, 0.45], tilt: 0, brow: [0.8, -0.25], bang: [-0.4, 0.5], mouth: "squiggle", eye: 1.05, look: [0, -0.3] },
};
const HEAD_T = "#fbfaf7", HEAD_B = "#c9cfdc", GOLD = "#e3b84a", GLOVE = "#fafaf8";

const tube = (d: Dw, pts: P2[], w: number, col: string) => {
  d.line(pts, INK, w + OL * 1.5); d.line(pts, col, w);
};
const arm = (d: Dw, s: P2, ang: number, ln: number, bend: number, col: string): P2 => {
  const r = rad(ang), r2 = rad(ang + bend);
  const e: P2 = [s[0] + Math.sin(r) * ln * 0.5, s[1] + Math.cos(r) * ln * 0.5];
  const h: P2 = [e[0] + Math.sin(r2) * ln * 0.5, e[1] + Math.cos(r2) * ln * 0.5];
  tube(d, [s, e, h], 19, col);
  const a = Math.atan2(h[1] - e[1], h[0] - e[0]);
  d.ell(h[0] + Math.cos(a - 1.2) * 12, h[1] + Math.sin(a - 1.2) * 12, 7, 6, GLOVE, 3);
  d.ell(h[0], h[1], 15, 14, GLOVE, 4);
  return h;
};
const eye = (H: Dw, cx: number, side: number, E: EmoP, look: P2, blink: boolean) => {
  const sz = E.eye, rx = 10 * sz, ry = 13 * sz, ex = cx + look[0] * 6, ey = -4 + look[1] * 6;
  if (E.ring) { H.ell(ex, ey, rx + 7, ry + 7, "#ffffff", 3.5); H.ell(ex, ey, rx * 0.55, ry * 0.55, INK, 0); }
  else { H.ell(ex, ey, rx, ry, INK, 0); H.dot(ex + rx * 0.35, ey - ry * 0.4, rx * 0.28, "#ffffff"); }
  if (E.happy && !blink) {
    H.poly([[ex - rx - 3, ey + 3], [ex + rx + 3, ey + 3], [ex + rx + 3, ey + ry + 4], [ex - rx - 3, ey + ry + 4]], HEAD_T, 0);
    H.line(bez([ex - rx - 2, ey + 6], [ex, ey - 1], [ex + rx + 2, ey + 6], 8), INK, 4);
  }
  const li = blink ? 1 : E.lid[side < 0 ? 0 : 1];
  if (li > 0.02) {
    const top = ey - ry - (E.ring ? 9 : 2), yl = top + (2 * ry + 4) * li, t = E.tilt * -side * 8;
    const a: P2 = [ex - rx - 6, yl - t], b: P2 = [ex + rx + 6, yl + t];
    H.poly([[ex - rx - 7, top - 4], [ex + rx + 7, top - 4], b, a], "#f3f2f0", 0);
    H.line([a, b], INK, 6);
  }
};
const brow = (H: Dw, cx: number, side: number, E: EmoP) => {
  const r = E.brow[side < 0 ? 0 : 1], a = E.bang[side < 0 ? 0 : 1], by = -32 - r * 12;
  const i: P2 = [cx - side * 17, by + a * 8], o: P2 = [cx + side * 17, by - a * 5];
  const dx = o[0] - i[0], dy = o[1] - i[1], L = Math.hypot(dx, dy) || 1, nx = (-dy / L) * 6.5, ny = (dx / L) * 6.5;
  H.poly([[i[0] + nx, i[1] + ny], [o[0] + nx * 0.8, o[1] + ny * 0.8], [o[0] - nx * 0.8, o[1] - ny * 0.8], [i[0] - nx, i[1] - ny]], INK, 3);
};
const mouth = (H: Dw, k: string, my = 34) => {
  const M = "#3a1520", T = "#faf8f4";
  if (k === "line") H.line(bez([-11, my], [0, my + 2], [11, my], 6), INK, 4.5);
  else if (k === "smirk") H.line(bez([-10, my + 3], [4, my + 4], [15, my - 4], 8), INK, 4.5);
  else if (k === "frown") H.line(bez([-12, my + 5], [0, my - 3], [12, my + 5], 8), INK, 4.5);
  else if (k === "wavy") H.line(Array.from({ length: 12 }, (_, j) => { const x = -13 + (26 * j) / 11; return [x, my + 2 + Math.sin(x * 0.55) * 3] as P2; }), INK, 4);
  else if (k === "squiggle") H.line(Array.from({ length: 12 }, (_, j) => { const x = -12 + (24 * j) / 11; return [x, my + (Math.sin(x * 0.35 + 1) * 4 * x) / 13] as P2; }), INK, 4);
  else if (k === "o") H.ell(0, my + 4, 8, 11, M, 4);
  else if (k === "open") H.poly([...bez([-14, my - 2], [0, my - 4], [14, my - 2], 6), ...bez([14, my - 2], [0, my + 24], [-14, my - 2], 10)], M, 4);
  else if (k === "grin") { H.poly([...bez([-17, my - 3], [0, my + 1], [17, my - 3], 8), ...bez([17, my - 3], [0, my + 18], [-17, my - 3], 10)], M, 4); H.poly([[-13, my - 2], [13, my - 2], [11, my + 3], [-11, my + 3]], T, 0); }
  else if (k === "grit") { H.poly([[-16, my - 5], [16, my - 5], [14, my + 7], [-14, my + 7]], T, 4); H.line([[-15, my + 1], [15, my + 1]], INK, 2); }
};
const hat = (H: Dw, kind: string) => {
  if (kind === "bicorne" || kind === "bicorne_w" || kind === "plume") {
    const pts = [...bez([-140, -40], [-96, -168], [0, -150], 16), ...bez([0, -150], [96, -168], [140, -40], 16), ...bez([140, -40], [0, -86], [-140, -40], 18)];
    H.grad(pts, "#3a3646", "#121018", 1.2, OL);
    H.line(bez([-118, -52], [0, -92], [118, -52], 16), "#4a4658", 5);
    H.line(bez([-70, -132], [-10, -146], [40, -140], 8), "#5a5668", 4);
    if (kind === "bicorne_w") H.line(bez([-128, -46], [0, -90], [128, -46], 18), GOLD, 8);
    if (kind === "plume") for (let k = -3; k <= 3; k++) H.ell(k * 24, -150 + Math.abs(k) * 6, 19, 15, "#f4f1ea", 3);
    H.ell(80, -100, 16, 16, "#d9323a", 3); H.ell(80, -100, 10.5, 10.5, "#f4f1ea", 0); H.ell(80, -100, 5, 5, "#2b4aa8", 0); // French cockade: blue centre, white, red rim
  } else if (kind === "shako") {
    H.grad([[-56, -50], [56, -50], [50, -168], [-50, -168]], "#2e2a36", "#141218", 1.2, OL);
    H.poly([[-60, -46], [60, -46], [56, -62], [-56, -62]], "#1a1820", 3);
    H.poly([[-52, -160], [52, -160], [50, -172], [-50, -172]], "#e3b84a", 2.5);
    H.poly([[-14, -130], [14, -130], [10, -96], [-10, -96]], "#e3b84a", 2.5);
    H.ell(0, -184, 10, 18, "#d23a34", 3);
    H.line(bez([-56, -48], [0, -10], [56, -48], 10), "#e3b84a", 3);
  } else if (kind === "tricorne") {
    H.grad([[-112, -40], [-76, -116], [0, -100], [76, -116], [112, -40], [0, -62]], "#5a4632", "#2e2218", 1.2, OL);
    H.line([[-102, -44], [0, -66], [102, -44]], "#c8a04a", 5);
  } else if (kind === "straw") {
    H.grad(circ(0, -52, 128, 22), "#f2d68a", "#c99a3a", 1.4, OL);
    H.grad([[-58, -56], [58, -56], [46, -118], [-46, -118]], "#f2d68a", "#caa04a", 0.3, OL * 0.85);
    H.poly([[-58, -60], [58, -60], [55, -76], [-55, -76]], "#c8433a", 2.5);
    for (let k = -5; k <= 5; k++) H.line([[k * 10, -78], [k * 8, -114]], "#b8903a", 2);
  }
};

export type Pose = { aL?: [number, number]; aR?: [number, number]; elL?: number; elR?: number; lean?: number; tilt?: number; bob?: number; step?: number;
  prop?: (B: Dw, hL: P2, hR: P2) => void; behindProp?: (B: Dw, hL: P2, hR: P2) => void };
export const K5 = 1.45; // python design unit -> card px
/** draw one v5 character into a 600 x 1000 card: feet at (300, 975) */
export const drawToon = (g: CanvasRenderingContext2D, who: Who, emo: Emo, pose: Pose = {}, blink = false, flip = 1, lookO?: P2) => {
  const o = WHO[who], E = EMO[emo], look = lookO ?? E.look ?? [0, 0];
  const aL = pose.aL ?? [20, 120], aR = pose.aR ?? [-20, 120], elL = pose.elL ?? 10, elR = pose.elR ?? -10;
  const st = pose.step ? Math.sin(pose.step) * 26 : 0;
  const root = new Dw(g).sub(300, 975 - (pose.bob ?? 0) * K5, K5, 0, flip);
  for (const [side, ph] of [[-1, st], [1, -st]] as [number, number][]) {      // trouser legs + chunky boots
    const hx = side * 19, fx = side * 20 + ph, fy = -Math.abs(ph) * 0.3;
    tube(root, [[hx, -150], [fx, -70 + fy * 0.5], [fx, -14 + fy]], 22, o.pants);
    root.poly([[fx - 15, -60 + fy], [fx + 15, -60 + fy], [fx + 15, -12 + fy], [fx - 15, -12 + fy]], o.boot, OL * 0.7);
    root.ell(fx + 10, -8 + fy, 27, 13, o.boot, OL * 0.8);
    root.ell(fx + 4, -14 + fy, 10, 3, shade(o.boot, 1.8), 0);
  }
  const B = root.sub(0, -150, 1, pose.lean ?? 0);
  if (pose.behindProp) pose.behindProp(B, [0, 0], [0, 0]);
  const hR = arm(B, [-34, -118], aR[0], aR[1], elR, shade(o.coat, 0.8));
  const bean: P2[] = Array.from({ length: 56 }, (_, i) => { const a = (i / 56) * Math.PI * 2, s = Math.sin(a); return [Math.cos(a) * 58 * (1 + 0.08 * s), -78 + s * 86 * (s > 0 ? 1 : 0.92)]; });
  B.grad(bean, shade(o.coat, 1.12), shade(o.coat, 0.72), 0.35);
  if (o.overall) {
    B.grad([[-34, -110], [34, -110], [40, 8], [-40, 8]], o.front, shade(o.front, 0.8), 0.4, 3);
    B.poly([[-38, -70], [38, -70], [44, 8], [-44, 8]], "#6a8ac0", 3);
  } else {
    B.grad([[-16, -158], [16, -158], [22, -40], [0, -24], [-22, -40]], o.front, shade(o.front, 0.82), 0.4, 3);
    for (const yy of [-130, -104, -78, -52]) { B.dot(-26, yy, 3.6, GOLD); B.dot(26, yy, 3.6, GOLD); }
  }
  if (o.sash) B.poly([[-50, -132], [-36, -144], [56, -22], [44, -6]], o.sash, 3);
  if (o.strap) B.poly([[30, -150], [44, -144], [-40, -10], [-52, -18]], o.strap, 3);
  B.poly([[-52, -14], [52, -14], [48, 0], [-48, 0]], shade(o.pants, 0.95), 3);
  B.poly([[-8, -16], [8, -16], [8, 0], [-8, 0]], GOLD, 2);
  B.poly(bean, null, OL);
  if (o.epaul) for (const s of [-1, 1]) {
    B.ell(s * 40, -152, 22, 10, GOLD, 3);
    for (let k = 0; k < 5; k++) B.line([[s * 40 + (k - 2) * 8, -144], [s * 40 + (k - 2) * 9, -128]], "#d9a640", 3);
  }
  const hL = arm(B, [34, -118], aL[0], aL[1], elL, o.coat);
  if (pose.prop) pose.prop(B, hL, hR);
  const H = B.sub(0, -232, 1, (pose.tilt ?? 0) + (E.chin ?? 0));
  const hp = circ(0, 0, 80, 76, 60);
  H.grad(hp, HEAD_T, HEAD_B, 1.25);
  H.grad(circ(-20, -26, 42, 30), "#ffffff", HEAD_T, 1.2);
  H.poly(hp, null, OL);
  if (o.stubble) for (let i = 0; i < 70; i++) { const a = 0.25 + ((i * 0.618) % 1) * (Math.PI - 0.5), r = 34 + ((i * 0.37) % 1) * 36; H.dot(Math.cos(a) * r, Math.sin(a) * r * 0.9 + 6, 1.6, "#8a8a96"); }
  if (o.sideburns) for (const s of [-1, 1]) H.poly([[s * 70, -26], [s * 80, 6], [s * 68, 30], [s * 60, -8]], o.sideburns, 3);
  if (o.forelock) H.poly([[-46, -58], [-24, -74], [2, -76], [14, -64], [2, -60], [-6, -46], [-12, -60], [-26, -48], [-36, -58]], "#2a1e1a", 3);
  for (const side of [-1, 1]) { eye(H, side * 26, side, E, look, blink); brow(H, side * 26, side, E); }
  H.line(bez([-3, 12], [4, 20], [10, 13], 6), "#9aa0b4", 3.5);
  if (o.tache) H.poly([[-34, 30], [-18, 16], [0, 22], [18, 16], [34, 30], [26, 38], [12, 30], [0, 34], [-12, 30], [-26, 38]], o.tache, 3);
  if (o.beard) H.grad([[-66, 8], [-50, 52], [-14, 76], [14, 76], [50, 52], [66, 8], [40, 26], [16, 40], [-16, 40], [-40, 26]], o.beard, shade(o.beard, 0.7), 1.4, 3);
  if (!o.tache) mouth(H, E.mouth); else if (["o", "open", "grit", "grin"].includes(E.mouth)) mouth(H, E.mouth, 44);
  if (o.straw) { H.line([[10, 36], [60, 26], [74, 16]], "#e8c35a", 4); H.line([[64, 24], [78, 30]], "#e8c35a", 3); }
  if (E.sweat) H.poly([[76, -44], [86, -20], [76, -12], [66, -20]], "#9fd8ff", 3);
  if (E.lines) for (let k = 0; k < 3; k++) { const a = -2.3 + k * 0.45; H.line([[Math.cos(a) * 104, Math.sin(a) * 98 - 10], [Math.cos(a) * 130, Math.sin(a) * 122 - 10]], INK, 5); }
  hat(H, o.hat);
  return { H };
};

// ---------------- props held in the hands ----------------
export const musket = (B: Dw, hL: P2, hR: P2) => {
  let vx = hL[0] - hR[0], vy = hL[1] - hR[1], n = Math.hypot(vx, vy);
  if (n < 8) { vx = 1; vy = -0.3; n = Math.hypot(vx, vy); }
  const ux = vx / n, uy = vy / n;
  tube(B, [[hR[0] - ux * 50, hR[1] - uy * 50], [hR[0] + ux * 50, hR[1] + uy * 50]], 20, "#7a4a28");
  tube(B, [[hR[0] + ux * 44, hR[1] + uy * 44], [hL[0] + ux * 170, hL[1] + uy * 170]], 9, "#4a4f55");
};
export const stick = (ang: number, ln = 180, col = "#8a5a32") => (B: Dw, hL: P2) =>
  tube(B, [hL, [hL[0] + Math.cos(ang) * ln, hL[1] + Math.sin(ang) * ln]], 11, col);
export const clipboard = (B: Dw, hL: P2) => {
  const [x, y] = hL;
  B.poly([[x - 44, y - 76], [x + 30, y - 76], [x + 30, y + 22], [x - 44, y + 22]], "#a87444", 4);
  B.poly([[x - 36, y - 66], [x + 22, y - 66], [x + 22, y + 14], [x - 36, y + 14]], "#f6f1e6", 0);
  for (let k = 0; k < 4; k++) B.line([[x - 30, y - 50 + k * 15], [x + 16, y - 50 + k * 15]], "#8a7a6a", 2.5);
  B.poly([[x - 16, y - 82], [x + 6, y - 82], [x + 6, y - 70], [x - 16, y - 70]], "#8a8a86", 2);
};
export const carrotProp = (B: Dw, hL: P2) => carrotAt(B, hL[0] + 10, hL[1] - 10, 0.9, -1.2);
export const carrotAt = (d: Dw, x: number, y: number, s = 1, rot = 0) => {
  const L = d.sub(x, y, s, rot);
  for (const k of [-0.4, 0, 0.4]) L.ell(Math.sin(k) * 30, -70 - Math.cos(k) * 20, 9, 28, "#4f9a3a", 3, k);
  L.poly([[-26, -60], [26, -60], [0, 80]], "#f08a2a", 4);
  for (let k = 0; k < 3; k++) L.line([[-14 + k * 4, -30 + k * 30], [2 + k * 2, -26 + k * 30]], "#c86a1a", 3);
};

// ---------------- bunnies ----------------
export type Bunny = "white" | "brown" | "grey" | "cream" | "spot" | "black" | "wild";
const FUR: Record<Bunny, [string, string]> = { white: ["#f6f3ec", "#d9d3ca"], brown: ["#b98a5e", "#8f6640"], grey: ["#a9a39c", "#837d76"], cream: ["#ead6b6", "#c9b28c"],
  spot: ["#f6f3ec", "#d9d3ca"], black: ["#5a5054", "#3e3638"], wild: ["#8f7d68", "#665645"] };
export type BunnyOpts = { col: Bunny; view?: "side" | "front" | "back"; hop?: number; stretch?: number; face?: "open" | "wide" | "happy" | "closed" | "angry";
  ear?: number; tilt?: number; look?: P2; mouth?: "w" | "o" | "grin" | "flat"; napkin?: boolean; blink?: boolean };
/** bunny in a 400 x 400 card, feet at (200, 380), facing +x (mirror the card to face left). ~ 1 unit = 1 px at sc 1 */
export const drawBunny = (g: CanvasRenderingContext2D, o: BunnyOpts) => {
  const [c, dk] = FUR[o.col], view = o.view ?? "side", hop = o.hop ?? 0, st = o.stretch ?? 0, face = o.blink ? "closed" : o.face ?? "open";
  const L = new Dw(g).sub(200, 380 - hop * 90, 1.25);
  if (view === "back") {
    L.ell(0, -50, 56, 50, dk, OL); L.ell(0, -54, 48, 42, c, 0); L.ell(0, -30, 16, 15, "#fbfaf6", 4);
    const H = L.sub(0, -112);
    for (const s of [-1, 1]) { const E = H.sub(s * 18, -26, 1, s * (0.18 + 0.1 * (o.ear ?? 0))); E.ell(0, -46, 15, 46, c, 4.5); E.ell(0, -44, 6, 30, shade(c, 0.9), 0); }
    H.ell(0, 0, 46, 40, c, 5); H.ell(-6, -8, 36, 28, shade(c, 1.04), 0);
    return;
  }
  if (view === "front") {
    L.ell(-26, -8, 18, 11, dk, 4); L.ell(26, -8, 18, 11, dk, 4);
    L.ell(0, -50, 52, 48, dk, 5); L.ell(0, -56, 44, 40, c, 0); L.ell(0, -44, 26, 28, shade(c, 1.06), 0);
    L.ell(-16, -16, 12, 9, c, 3.5); L.ell(16, -16, 12, 9, c, 3.5);
  } else {
    L.ell(-36 - st * 20, -8 + st * 6, 40, 12, dk, 4, st * 0.3);
    L.ell(-72 - st * 10, -52, 17, 17, "#fbfaf6", 4);
    L.ell(-10, -50, 64 * (1 + st * 0.25), 50 / (1 + st * 0.25), c, 5);
    L.ell(4, -40, 34, 32, shade(c, 1.08), 0);
    if (o.col === "spot") { L.ell(-30, -66, 24, 16, "#a8794e", 0); L.ell(-50, -36, 14, 12, "#a8794e", 0); }
    L.ell(30 + st * 30, -8 - st * 10, 15, 9, shade(c, 0.95), 3.5); L.ell(14 + st * 26, -6 - st * 6, 14, 8, shade(c, 0.9), 3.5);
  }
  const H = view === "front" ? L.sub(0, -112, 1, o.tilt ?? 0) : L.sub(34 + st * 16, -104 + st * 18, 1, o.tilt ?? 0);
  const ear = o.ear ?? 0;
  const ears: [number, number][] = view === "front" ? [[-18, -0.22 - ear * 0.1], [18, 0.22 + ear * 0.1]] : [[-12, -0.22 + ear], [12, 0.18 - ear]];
  ears.forEach(([ex, a], k) => { const ax = ex + Math.sin(a) * 46, ay = -40 - Math.cos(a) * 46; H.ell(ax, ay, 15, 48, shade(c, k ? 1 : 0.95), 4, a); H.ell(ax, ay + 4, 7, 34, "#f2a0a8", 0, a); });
  H.ell(0, 0, 48, 42, c, 5);
  if (o.col === "wild") { for (let i = 0; i < 9; i++) H.line([[-40 + i * 10, -36 + (i % 2) * 6], [-44 + i * 10, -46]], dk, 3); }
  const lk = o.look ?? [0, 0], eyes: [number, number][] = view === "front" ? [[-17, -6], [17, -6]] : [[-8, -6], [20, -6]];
  for (const [ex, ey] of eyes) {
    if (face === "wide") { H.ell(ex, ey, 11, 13, "#ffffff", 3); H.ell(ex + lk[0] * 4, ey + 1 + lk[1] * 3, 6, 7, "#2a1e22", 0); H.dot(ex + lk[0] * 4 + 2, ey - 2, 2.2, "#fff"); }
    else if (face === "happy") H.line(bez([ex - 8, ey + 3], [ex, ey - 7], [ex + 8, ey + 3], 8), INK, 4);
    else if (face === "closed") H.line(bez([ex - 8, ey], [ex, ey + 5], [ex + 8, ey], 8), INK, 4);
    else { H.ell(ex + lk[0] * 4, ey + lk[1] * 4, 7, 9, "#2a1e22", 0); H.dot(ex + lk[0] * 4 + 2.5, ey + lk[1] * 4 - 3.5, 2.8, "#fff"); }
    if (face === "angry") H.line([[ex - 10, ey - 18], [ex + 10, ey - 12]], INK, 5);
  }
  const nx = view === "front" ? 0 : 34;
  H.ell(nx - 18, 16, 9, 6, "#f6b8b8", 0); H.ell(nx + 2, 16, 9, 6, "#f6b8b8", 0);
  H.poly([[nx - 6, 8], [nx + 6, 8], [nx, 16]], "#e07a8a", 2.5);
  const m = o.mouth ?? "w";
  if (m === "w") { H.line(bez([nx - 10, 20], [nx - 5, 26], [nx, 20], 5), INK, 3); H.line(bez([nx, 20], [nx + 5, 26], [nx + 10, 20], 5), INK, 3); }
  else if (m === "o") H.ell(nx, 26, 6, 7, "#6e2626", 3);
  else if (m === "grin") { H.poly(bez([nx - 12, 20], [nx, 38], [nx + 12, 20], 8), "#6e2626", 3); H.poly([[nx - 4, 20], [nx + 4, 20], [nx + 4, 27], [nx - 4, 27]], "#fff", 1.5); }
  else H.line([[nx - 8, 24], [nx + 8, 24]], INK, 3);
  for (const k of [-1, 1]) { H.line([[nx + 10, 14 + k * 3], [nx + 32, 10 + k * 9]], shade(c, 0.6), 1.8); H.line([[nx - 10, 14 + k * 3], [nx - 32, 10 + k * 9]], shade(c, 0.6), 1.8); }
  if (o.napkin) { H.poly([[nx - 34, 34], [nx + 30, 30], [nx - 2, 76]], "#fbfaf6", 3); H.line([[nx - 24, 40], [nx + 20, 37]], "#d23a34", 3); }
};

// ---------------- effects drawn on cards ----------------
export const drawBubble = (g: CanvasRenderingContext2D, inner: "rabbit" | "dinner") => {
  const d = new Dw(g).sub(256, 220, 1);
  for (const [x, y, r] of [[-150, 200, 16], [-120, 160, 24]] as const) d.ell(x, y, r, r, "#ffffff", 5);
  const pts: P2[] = Array.from({ length: 40 }, (_, i) => { const a = (i / 40) * Math.PI * 2, k = 1 + 0.07 * Math.sin(a * 9); return [Math.cos(a) * 190 * k, Math.sin(a) * 140 * k]; });
  d.poly(pts, "#ffffff", 6);
  if (inner === "dinner") { carrotAt(d, -60, 20, 1, -0.4); carrotAt(d, 50, 10, 0.9, 0.35); d.ell(0, 70, 100, 28, "#f6f1e6", 4); }
};

/** a bicorne alone (war-map pin) in a 512 x 320 card */
export const drawHatCard = (g: CanvasRenderingContext2D) => hat(new Dw(g).sub(256, 300, 1.6), "bicorne");
/** quill pen, nib at (60, 460) of a 256 x 512 card */
export const drawQuill = (g: CanvasRenderingContext2D) => {
  const L = new Dw(g).sub(60, 460, 1.6, -0.5);
  L.line([[0, 0], [0, -40]], "#2a2a2a", 5);
  L.poly([[0, -30], [26, -120], [14, -230], [-4, -160], [-14, -60]], "#fbfaf6", 4);
  L.line([[0, -30], [12, -220]], "#c9c2b2", 3);
};
/** growing ink signature on a flat 512 x 256 card, progress 0..1 */
export const drawSignature = (g: CanvasRenderingContext2D, u: number) => {
  const n = Math.max(2, Math.round(u * 40)), pts: [number, number][] = [];
  for (let i = 0; i < n; i++) pts.push([60 + i * 10, 140 + Math.sin(i * 1.7) * 26 - i * 0.6]);
  const L = new Dw(g); L.line(pts, "#241a30", 7);
};
