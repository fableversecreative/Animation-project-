// Who stands where, doing what, in every shot (pure function of shot id + frame). Acting without lip sync:
// expressions + snappy poses change on the voice words; blinks every 0.5-2.3 s.
import { SLOT } from "./story";
import { drawToon, drawBunny, drawBubble, drawHatCard, drawQuill, drawSignature, musket, stick, clipboard, carrotProp, Who, Emo, Pose, BunnyOpts, Bunny } from "./chars";

export type Item = {
  kind: "toon" | "bunny" | "fx"; key: string; draw: (g: CanvasRenderingContext2D) => void; x: number; y: number; z: number;
  mirror?: boolean; scale?: number; roll?: number; noShadow?: boolean; cw?: number; ch?: number; w?: number; h?: number; flat?: boolean; rot?: number; soft?: boolean;
};
export const MAP_REG: Record<string, [number, number][]> = {
  britain: [[300, 560], [350, 520], [380, 600], [370, 700], [330, 760], [290, 740], [310, 660]], ireland: [[230, 620], [270, 600], [280, 660], [240, 690]],
  spain: [[150, 1000], [330, 960], [380, 1000], [360, 1120], [280, 1200], [170, 1190], [120, 1100]],
  france: [[330, 960], [300, 880], [330, 800], [420, 780], [480, 800], [500, 880], [470, 960], [400, 990], [380, 1000]],
  low: [[420, 780], [440, 730], [500, 720], [510, 790], [480, 800]], germany: [[500, 720], [600, 690], [640, 740], [640, 850], [560, 880], [500, 880], [510, 790]],
  italy: [[500, 880], [560, 880], [600, 920], [640, 1010], [700, 1090], [680, 1120], [630, 1060], [570, 990], [520, 960]],
  austria: [[560, 880], [640, 850], [740, 860], [760, 920], [660, 930], [600, 920]], poland: [[640, 740], [760, 720], [800, 800], [740, 860], [640, 850]],
  russia: [[760, 720], [800, 560], [1000, 500], [1060, 520], [1060, 1000], [900, 960], [800, 900], [740, 860], [800, 800]],
  scandi: [[560, 560], [620, 420], [720, 380], [760, 460], [700, 560], [660, 640], [620, 600]],
  balkans: [[660, 930], [760, 920], [800, 900], [900, 960], [860, 1060], [780, 1100], [720, 1040]], denmark: [[560, 640], [590, 610], [600, 690], [570, 690]],
};
/** [country, seconds into shot 2 when it turns red] - on the words "conquered … half … of Europe" */
export const CONQ: [string, number][] = [["france", 0.15], ["low", 0.35], ["italy", 0.55], ["germany", 0.75], ["austria", 0.95], ["spain", 1.12], ["poland", 1.3]];

const q = (v: number, n = 20) => Math.round(v * n) / n;
const hh = (i: number, s = 0) => { const v = Math.sin(i * 127.1 + s * 311.7) * 43758.5453; return v - Math.floor(v); };
const back = (x: number, s = 1.7) => { const u = Math.min(1, Math.max(0, x)) - 1; return u * u * ((s + 1) * u + s) + 1; };
const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const blinkAt = (u: number, seed: number) => { const p = 1.1 + hh(seed) * 1.2, x = ((u + hh(seed, 3) * p) % p); return x < 0.11; };
type PoseK = { aL?: [number, number]; aR?: [number, number]; elL?: number; elR?: number; lean?: number; tilt?: number; bob?: number; step?: number; prop?: string };
const PROPS: Record<string, Pose["prop"]> = { musket, clip: clipboard, carrot: carrotProp, stickA: stick(-0.5), stickB: stick(-1.6), stickC: stick(0.4) };
const qp = (p: PoseK) => JSON.stringify(p, (_k, v) => (typeof v === "number" ? q(v, 4) : v));
const toon = (who: Who, emo: Emo, x: number, z: number, p: PoseK = {}, o: { blink?: boolean; mirror?: boolean; y?: number; look?: [number, number]; noShadow?: boolean; scale?: number } = {}): Item => {
  const pose: Pose = { ...p, prop: p.prop ? PROPS[p.prop] : undefined } as Pose;
  return { kind: "toon", key: `T|${who}|${emo}|${qp(p)}|${o.blink ? 1 : 0}|${o.look ? o.look.map((v) => q(v)).join(",") : ""}`,
    draw: (g) => drawToon(g, who, emo, pose, !!o.blink, 1, o.look), x, y: o.y ?? 0, z, mirror: o.mirror, noShadow: o.noShadow, scale: o.scale };
};
const bunny = (b: BunnyOpts, x: number, z: number, o: { mirror?: boolean; y?: number; scale?: number; noShadow?: boolean } = {}): Item => {
  const bb = { ...b, hop: q(b.hop ?? 0), stretch: q(b.stretch ?? 0), ear: q(b.ear ?? 0, 10), tilt: q(b.tilt ?? 0, 10) };
  return { kind: "bunny", key: `B|${JSON.stringify(bb)}`, draw: (g) => drawBunny(g, bb), x, y: o.y ?? 0, z, mirror: o.mirror, scale: o.scale, noShadow: o.noShadow };
};
const COLS: Bunny[] = ["white", "brown", "grey", "cream", "spot", "black"];
const hopPh = (u: number, rate: number, ph: number) => Math.abs(Math.sin((u * rate + ph) * Math.PI));
const R = SLOT.farm, T = SLOT.tent, M = SLOT.map;

export const stage = (id: number, f: number, u: number, env: { carriageX: number; carriageY: number }): Item[] => {
  const out: Item[] = [];
  const B = (i: number) => blinkAt(u, i);
  switch (id) {
    case 1: out.push(toon("napoleon", u < 0.75 ? "proud" : "smug", 0, 0, { aL: [-40, 80], elL: -62, tilt: -0.05, bob: Math.sin(u * 2.2) * 2 }, { blink: B(1) })); break;
    case 2: if (u > 1.27) {
      const k = clamp((u - 1.27) / 0.12), s = 1.8 - 0.8 * k * k;
      out.push({ kind: "fx", key: "hatpin", cw: 512, ch: 320, draw: drawHatCard, x: M - 0.216, y: 1.13 + (1 - k) * 0.25, z: -0.47, w: 0.3 * s, h: 0.19 * s });
    } break;
    case 3: {
      const e: Emo = u < 0.62 ? "smug" : "worried", look: [number, number] = u < 0.62 ? [0.5, 0] : u < 1.05 ? [-0.7, 0.1] : u < 1.45 ? [0.7, 0.1] : [0, 0.3];
      out.push(toon("napoleon", e, 6, 2, { aL: [-40, 80], elL: -62, tilt: u < 0.62 ? 0 : 0.06 }, { blink: B(3), look }));
      break;
    }
    case 4: {
      const k = back((u - 0.05) / 0.3, 2.0);
      out.push(bunny({ col: "white", view: "front", face: u > 0.5 ? "wide" : "open", ear: u > 0.3 ? 1 : 0, tilt: u > 0.7 ? 0.14 * Math.sin((u - 0.7) * 5) : 0, blink: B(4) }, 8, 4, { y: -0.42 * (1 - k), noShadow: k < 0.9 }));
      for (let i = 0; i < 8; i++) out.push(bunny({ col: COLS[i % 6], view: "front", face: "open", blink: B(i + 10) }, 6.4 + i * 0.45, 1.6 - (i % 3) * 0.5, { y: -0.4 * (1 - back((u - 0.25 - i * 0.07) / 0.3)) }));
      break;
    }
    case 5: {
      const sg = clamp((u - 0.2) / 1.1);
      out.push({ kind: "fx", key: "sig" + q(sg, 20), cw: 512, ch: 256, draw: (g) => drawSignature(g, sg), x: T - 0.02, y: 0.856, z: 0.03, w: 0.3, h: 0.15, flat: true });
      const n = Math.max(2, Math.round(sg * 40)), tx = (60 + (n - 1) * 10) / 512 - 0.5, ty = (140 + Math.sin((n - 1) * 1.7) * 26) / 256 - 0.5;
      out.push({ kind: "fx", key: "quill", cw: 256, ch: 512, draw: drawQuill, x: T - 0.02 + tx * 0.3 + 0.03, y: 0.97, z: 0.03 + ty * 0.15, w: 0.12, h: 0.24 });
      break;
    }
    case 6: {
      const sh = u > 0.3 && u < 1.3 ? Math.sin(u * 22) * 6 : 0;
      out.push(toon("napoleon", u > 0.3 ? "happy" : "smug", T - 0.48, -0.8, { aL: [84 + sh, 104], aR: [-20, 120], lean: 0.08 }, { blink: B(6) }));
      out.push(toon("tsar", "happy", T + 0.5, -0.8, { aL: [84 - sh, 104], aR: [-20, 120], lean: 0.08 }, { mirror: true, blink: B(7) }));
      break;
    }
    case 7: {
      const r = clamp(u / 0.55);
      out.push(toon("napoleon", u > 0.5 ? "excited" : "happy", 12, 0, { aL: [40 + 110 * r, 110], aR: [-20 + 140 * r, 80], elL: -10, prop: "musket", bob: hopPh(u, 4.5, 0) * 8 * r }, { blink: B(8) }));
      if (u > 1.9) {
        const p = back((u - 1.9) / 0.3);
        out.push({ kind: "fx", key: "bub|rabbit", cw: 512, ch: 512, draw: (g) => { drawBubble(g, "rabbit"); g.save(); g.translate(150, 90); g.scale(0.55, 0.55); drawBunny(g, { col: "white", face: "happy" }); g.restore(); },
          x: 12.75, y: 1.95, z: 0.1, w: 0.95 * p, h: 0.95 * p });
      }
      break;
    }
    case 8: {
      const sal = u > 0.25 && u < 1.2 ? 1 : 0;
      out.push(toon("berthier", "proud", 16, 1, { aL: [70, 110], elL: 60, prop: "clip", aR: sal ? [-160, 70] : [-20, 120], elR: sal ? -70 : -10 }, { blink: B(9) }));
      break;
    }
    case 9: {
      for (let row = 0; row < 3; row++) for (let i = 0; i < 7; i++) {
        const cx = 36 + i * 1.25 + (row % 2) * 0.6, cz = -2 - row * 1.0, k = row * 7 + i;
        for (const dx of [-0.2, 0.2]) out.push(bunny({ col: COLS[(k + (dx > 0 ? 3 : 0)) % 6], view: "front", hop: hopPh(u, 1.6, hh(k + dx)) * 0.15, ear: Math.sin(u * 6 + k) * 0.3, blink: B(k * 2 + (dx > 0 ? 1 : 0)) }, cx + dx, cz + 0.05, { y: 0.1, scale: 0.72, noShadow: true }));
      }
      break;
    }
    case 10: {
      const m = clamp((u - 0.7) / 0.35);
      out.push(bunny({ col: "brown", view: "front", face: u > 0.6 ? "wide" : "open", ear: 0.2 * Math.sin(u * 9), blink: B(30) }, 40 - 0.1, -0.45 + m * 0.55, { y: 0.1 * (1 - m), scale: 0.95 }));
      break;
    }
    case 11: {
      const r = (t0: number) => back((u - t0) / 0.22, 1.6);
      const aim = (k: number): PoseK => ({ aL: [20 + 80 * k, 100], aR: [-20 + 92 * k, 70], prop: "musket" });
      out.push(toon("hunter", "determined", 23.2, -0.9, aim(r(0.35)), { blink: B(31) }));
      out.push(toon("hunter2", "determined", 24.8, -0.9, aim(r(0.45)), { mirror: true, blink: B(32) }));
      out.push(toon("napoleon", "sly", 24, 0, aim(r(0.25)), { blink: B(33), look: [0.6, 0] }));
      break;
    }
    case 12: {
      out.push(toon("napoleon", "confused", 30, -1.5, { aL: [100, 100], aR: [72, 70], prop: "musket", tilt: u > 0.9 ? 0.12 : 0 }, { blink: B(34) }));
      for (let i = 0; i < 14; i++) {
        const x = 28.9 + hh(i, 1) * 2.2, z = 2.2 + hh(i, 2) * 3.2;
        out.push(bunny({ col: COLS[i % 6], view: i % 3 ? "side" : "front", face: "open", look: u < 0.9 ? [-1, -0.5] : [1, -0.5], ear: 0.15 * Math.sin(u * 5 + i), blink: B(40 + i) }, x, z, { mirror: hh(i, 5) > 0.5 }));
      }
      break;
    }
    case 13: {
      out.push(toon("napoleon", "shocked", 32, 0, { aL: [150, 110], aR: [-150, 110], bob: hopPh(u, 6, 0) * 6 }, { mirror: true }));
      for (let i = 0; i < 26; i++) {
        const x0 = 22 + hh(i, 7) * 6, sp = 2.4 + hh(i, 8) * 1.6, z = -0.6 + hh(i, 9) * 3.2;
        const x = Math.min(x0 + sp * u, 31.2 - hh(i, 4) * 0.8), ph = hopPh(u, 3.2, hh(i, 6));
        out.push(bunny({ col: COLS[i % 6], hop: ph * 0.55, stretch: ph * 0.6, ear: -0.15, face: i % 3 ? "open" : "happy", mouth: i % 2 ? "grin" : "w" }, x, z));
      }
      break;
    }
    case 14: {
      const fl = Math.sin(u * 16);
      out.push(toon("napoleon", "scared", 32, 0, { aL: [130 + 30 * fl, 110], aR: [-130 - 30 * fl, 110], bob: Math.abs(fl) * 8, lean: 0.06 * fl }));
      for (let i = 0; i < 18; i++) {
        const a = hh(i, 11) * Math.PI * 2, r = 0.45 + hh(i, 12) * 1.1;
        out.push(bunny({ col: COLS[i % 6], view: i % 2 ? "side" : "front", hop: hopPh(u, 3, hh(i)) * 0.35, face: "happy", mouth: "grin" }, 32 + Math.cos(a) * r, 0.1 + Math.abs(Math.sin(a)) * r, { mirror: Math.cos(a) > 0 }));
      }
      const climb = clamp(u / 1.3);
      [[-0.18, 0], [0.18, 0.25], [-0.12, 0.5]].forEach(([dx, b0], i) => {
        const k = clamp(climb * 1.6 - b0);
        out.push(bunny({ col: COLS[(i + 2) % 6], stretch: 0.6, face: "happy", mouth: "grin", tilt: dx < 0 ? -0.6 : 0.6 }, 32 + dx, 0.12, { y: k * 0.45, mirror: dx > 0, noShadow: true, scale: 0.8 }));
      });
      break;
    }
    case 15: {
      out.push(toon("napoleon", "worried", 32, 0, {}, { look: [0, -1], blink: B(50) }));
      const k = back(u / 0.25);
      out.push(bunny({ col: "cream", view: "front", face: "happy", tilt: 0.1 * Math.sin(u * 4) }, 32, 0.02, { y: 1.62 + (1 - k) * 0.4, scale: 0.85, noShadow: true }));
      out.push(bunny({ col: "grey", face: "open", ear: 0.1 * Math.sin(u * 8) }, 32.4, 0.08, { y: 0.98, scale: 0.7, mirror: true, noShadow: true }));
      break;
    }
    case 16: {
      const sw = Math.sin(u * 14);
      out.push(toon("berthier", "angry", 34.5, -0.5, { aL: [110 + 60 * sw, 105], prop: sw > 0 ? "stickA" : "stickB" }));
      out.push(toon("hunter2", "angry", 35.9, -0.5, { aL: [110 - 60 * sw, 105], prop: sw > 0 ? "stickB" : "stickC" }, { mirror: true }));
      for (let i = 0; i < 14; i++) {
        const ph = hopPh(u, 2.2, hh(i, 21));
        out.push(bunny({ col: COLS[i % 6], view: i % 2 ? "front" : "side", hop: ph * 0.8, face: ph > 0.5 ? "happy" : "open", mouth: "grin" }, 34.4 + hh(i, 22) * 1.6, 0.4 + hh(i, 23) * 1.8, { mirror: hh(i, 24) > 0.5 }));
      }
      break;
    }
    case 17: {
      out.push(toon("napoleon", "deadpan", 32, 0, {}, { blink: B(60) }));
      for (let i = 0; i < 16; i++) {
        const x = 32 + (hh(i, 31) - 0.5) * 1.3, z = 0.12 + hh(i, 32) * 0.5, y = Math.max(0, 0.55 - Math.abs(x - 32) * 0.9) * hh(i, 33);
        out.push(bunny({ col: COLS[i % 6], view: "front", face: i % 4 ? "open" : "closed", ear: 0.06 * Math.sin(u * 4 + i) }, x, z, { y, noShadow: y > 0.05 }));
      }
      break;
    }
    case 18: {
      const nx = 41 + 19 * clamp(u / 2.6);
      out.push(toon("napoleon", "scared", nx, 1, { aL: [140, 100], aR: [-140, 100], step: u * 18, bob: Math.abs(Math.sin(u * 18)) * 10, lean: 0.12 }));
      for (let i = 0; i < 16; i++) {
        const ph = hopPh(u, 3.5, hh(i, 41));
        out.push(bunny({ col: COLS[i % 6], hop: ph * 0.5, stretch: ph * 0.6, face: "happy", mouth: "grin" }, nx - 1.2 - hh(i, 42) * 6, 0.3 + hh(i, 43) * 2.2));
      }
      break;
    }
    case 19: {
      const cx = env.carriageX;
      out.push(toon("napoleon", "scared", cx - 0.4, 0.6, { aL: [150, 110], aR: [-20, 110] }, { y: 0.78 + env.carriageY, noShadow: true }));
      out.push(bunny({ col: "spot", face: "happy", mouth: "grin" }, cx - 1.1, 0.55, { y: 1.56 + env.carriageY, noShadow: true, scale: 0.8 }));
      for (let i = 0; i < 18; i++) {
        const ph = hopPh(u, 4, hh(i, 51));
        out.push(bunny({ col: COLS[i % 6], hop: ph * 0.6, stretch: ph * 0.7, face: "happy", mouth: "grin" }, cx - 2.2 - hh(i, 52) * 7, 0.6 + hh(i, 53) * 2.4));
      }
      break;
    }
    case 20: out.push(bunny({ col: "white", view: "front", face: "open", tilt: back(u / 0.15) * 0.3, look: [-0.5, -0.6], ear: 0.15 }, R + 3, 3)); break;
    case 21: out.push(bunny({ col: "wild", face: "angry", mouth: "flat", ear: 0.25, look: [0.5, 0] }, -20, -58, { scale: 1.1 })); break;
    case 22: {
      out.push(toon("farmer", "happy", R + 0.55, 0.3, { aL: [70 + 8 * Math.sin(u * 6), 100], elL: 20, prop: "carrot" }, { mirror: true, blink: B(70) }));
      for (let i = 0; i < 5; i++) out.push(bunny({ col: COLS[i], view: "front", face: "happy", hop: hopPh(u, 2, hh(i, 61)) * 0.12 }, R - 1.1 + i * 0.5, -1.05, { y: 0.12, scale: 0.75, noShadow: true }));
      for (let i = 0; i < 4; i++) out.push(bunny({ col: COLS[(i + 2) % 6], face: "happy", look: [1, -0.5] }, R - 0.7 + i * 0.32, 0.2 + (i % 2) * 0.35, { scale: 0.85 }));
      break;
    }
    case 23: {
      const z = -3 + 5 * clamp(u / 2.4);
      out.push(toon("napoleon", "smug", R + 6, z, { step: u * 7, bob: Math.abs(Math.sin(u * 7)) * 4 }, { blink: B(80) }));
      [[R + 5.45, 9.0, "brown"], [R + 6.62, 9.05, "grey"]].forEach(([x, zz, col], i) => {
        const perk = clamp((u - 0.4 - i * 0.15) / 0.2);
        out.push(bunny({ col: col as Bunny, view: "back", ear: perk, hop: perk > 0 && perk < 1 ? 0.08 : 0 }, x as number, zz as number, { scale: 0.8 }));
      });
      break;
    }
    case 24: {
      for (let i = 0; i < 5; i++) out.push(bunny({ col: COLS[i], view: "front", face: "happy", mouth: "grin", napkin: true, hop: hopPh(u, 3.5, i * 0.2) * 0.3, ear: 0.15 }, R + 5.35 + i * 0.32, 3.55 + (i % 2) * 0.3));
      if (u > 0.15) { const p = back((u - 0.15) / 0.3); out.push({ kind: "fx", key: "bub|dinner", cw: 512, ch: 512, draw: (g) => drawBubble(g, "dinner"), x: R + 6.0, y: 0.98, z: 3.4, w: 0.7 * p, h: 0.7 * p }); }
      break;
    }
  }
  return out;
};
