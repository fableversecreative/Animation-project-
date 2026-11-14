// Napoleon vs Bunnies world: sky + camera-relative sun (bridge light rig), four sets in their own x slots
// (field + camp, war-map tent, treaty tent, farm), dynamic props (cage door, carriage, war map) and the cast as
// lit flat cards (v5 Option B toons, bunnies) with contact shadows. update(id, f, cam) poses everything per frame.
import * as THREE from "three";
import { Batch, boxGeo, V, lam } from "../bridge/build";
import { ctex, rep, grassHD, planksHD, beamHD, stoneHD, roofHD, cloudHD, rng } from "../bridge/paint";
import { LIGHTS, LOOK, LightPreset } from "../bridge/lights";
import { TONE, CHAR, untone } from "../bridge/shade";
import { NOINK } from "../bridge/ink";
import { Pool, Actor, Fx, SU } from "../bridge/cast";
import { fxContact } from "../bridge/toon";
import { FPS, SHOTS, SLOT, camAt, lt, ShotDef } from "./story";
import { stage, Item, MAP_REG, CONQ } from "./stage";

export const loadKit = () => Promise.resolve({});
const M = SLOT.map, T = SLOT.tent, R = SLOT.farm;
const BUNNY = (() => { const g = new THREE.PlaneGeometry(0.62, 0.62); g.translate(0, 0.31 - 0.031, 0); return g; })();

const discTex = () => ctex("sunDisc", 128, 128, (g) => {
  const gr = g.createRadialGradient(64, 64, 58, 64, 64, 64); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
});
const stripes = (key: string, a: string, b: string) => ctex(key, 512, 512, (g) => {
  for (let i = 0; i < 8; i++) { g.fillStyle = i % 2 ? a : b; g.fillRect(i * 64, 0, 64, 512); }
  g.fillStyle = "rgba(60,40,30,0.12)"; for (let y = 0; y < 512; y += 6) g.fillRect(0, y, 512, 1);
});
const parchTex = () => ctex("parch", 512, 512, (g, r) => {
  g.fillStyle = "#ecdcb4"; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 260; i++) { g.fillStyle = `rgba(${150 + r() * 40},${110 + r() * 30},${60 + r() * 20},${0.05 + r() * 0.06})`; g.beginPath(); g.arc(r() * 512, r() * 512, 10 + r() * 50, 0, 7); g.fill(); }
});
const rugTex = () => ctex("rug", 512, 512, (g) => {
  g.fillStyle = "#9a2b2b"; g.fillRect(0, 0, 512, 512); g.strokeStyle = "#e3b84a"; g.lineWidth = 14; g.strokeRect(30, 30, 452, 452);
  g.lineWidth = 6; g.strokeRect(70, 70, 372, 372); g.fillStyle = "#e3b84a"; g.beginPath(); g.arc(256, 256, 60, 0, 7); g.fill();
});
const barnTex = () => ctex("barn", 512, 512, (g, r) => {
  for (let i = 0; i < 16; i++) { g.fillStyle = ["#a8352c", "#b23c32", "#9c3027"][i % 3]; g.fillRect(i * 32, 0, 31, 512); }
  g.fillStyle = "rgba(0,0,0,0.25)"; for (let i = 0; i < 16; i++) g.fillRect(i * 32 + 30, 0, 2, 512);
});

/** war map: parchment + countries + the conquered ones in red (n of CONQ), drawn once per n */
const mapTex = (n: number) => ctex("warmap" + n, 1024, 1400, (g, r) => {
  g.fillStyle = "#ead9ae"; g.fillRect(0, 0, 1024, 1400);
  for (let i = 0; i < 300; i++) { g.fillStyle = `rgba(150,110,60,${0.04 + r() * 0.05})`; g.beginPath(); g.arc(r() * 1024, r() * 1400, 20 + r() * 80, 0, 7); g.fill(); }
  const vg = g.createRadialGradient(512, 700, 400, 512, 700, 900); vg.addColorStop(0, "rgba(0,0,0,0)"); vg.addColorStop(1, "rgba(110,70,30,0.45)");
  g.fillStyle = vg; g.fillRect(0, 0, 1024, 1400);
  g.fillStyle = "rgba(120,160,170,0.35)"; g.fillRect(40, 40, 944, 1320);
  const P = (p: [number, number]) => [(p[0] - 120) * 0.92 + 70, (p[1] - 330) * 1.38 + 120];
  const conq = new Set(CONQ.slice(0, n).map((c) => c[0]));
  for (const [nm, pts] of Object.entries(MAP_REG)) {
    g.beginPath(); pts.forEach((p, i) => { const [x, y] = P(p); if (i) g.lineTo(x, y); else g.moveTo(x, y); }); g.closePath();
    g.fillStyle = conq.has(nm) ? "#b8352a" : "#e2cfa2"; g.fill(); g.lineWidth = 5; g.strokeStyle = "#4a2e1a"; g.stroke();
  }
  g.fillStyle = "#4a2e1a"; g.font = "900 84px Poppins, sans-serif"; g.textAlign = "center"; g.fillText("EUROPE", 512, 130);
  g.strokeStyle = "#5a3a22"; g.lineWidth = 16; g.strokeRect(20, 20, 984, 1360);
});

export class World {
  root = new THREE.Group();
  private pool = new Pool();
  private toons: Actor[] = []; private buns: Actor[] = []; private fxs: Fx[] = [];
  private hemi: THREE.HemisphereLight; private sun: THREE.DirectionalLight;
  private sky: THREE.Mesh; private skyMat: THREE.ShaderMaterial;
  private fog = new THREE.Fog("#bccbec", 25, 420);
  private sunDisc: THREE.Sprite;
  private clouds: THREE.Mesh[] = []; private cloudMaps: Record<"day" | "golden", THREE.Texture[]>;
  private door = new THREE.Group(); private carriage = new THREE.Group(); private wheels: THREE.Mesh[] = [];
  private map: THREE.Mesh; private mapN = -1;
  private flags: THREE.Mesh[] = [];
  private sunCache = new Map<number, THREE.Vector3>();

  constructor() {
    const Rt = this.root;
    this.skyMat = new THREE.ShaderMaterial({
      uniforms: { c0: { value: new THREE.Color() }, c1: { value: new THREE.Color() }, c2: { value: new THREE.Color() }, c3: { value: new THREE.Color() }, c4: { value: new THREE.Color() }, e: { value: new THREE.Vector4() } },
      vertexShader: "varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
      fragmentShader: `uniform vec3 c0, c1, c2, c3, c4; uniform vec4 e; varying vec3 vP;
        void main(){ float el = asin(clamp(normalize(vP).y, -1.0, 1.0));
          vec3 c = mix(c0, c1, smoothstep(0.0, e.x, el)); c = mix(c, c2, smoothstep(e.x, e.y, el));
          c = mix(c, c3, smoothstep(e.y, e.z, el)); c = mix(c, c4, smoothstep(e.z, e.w, el)); gl_FragColor = vec4(c, 1.0); }`,
      side: THREE.BackSide, depthWrite: false, fog: false,
    });
    this.sky = new THREE.Mesh(new THREE.SphereGeometry(1100, 48, 24), this.skyMat);
    this.sky.renderOrder = -1; this.sky.frustumCulled = false; this.sky.layers.set(NOINK); Rt.add(this.sky);
    this.sunDisc = new THREE.Sprite(new THREE.SpriteMaterial({ map: discTex(), color: new THREE.Color(6.0, 4.4, 2.4), fog: false, depthWrite: false }));
    this.sunDisc.frustumCulled = false; this.sunDisc.layers.set(NOINK); Rt.add(this.sunDisc);
    this.hemi = new THREE.HemisphereLight("#cfe6ff", "#6c5c8c", 1.1);
    this.sun = new THREE.DirectionalLight("#fff0d6", 2.6); this.sun.castShadow = true; this.sun.shadow.mapSize.set(2048, 2048);
    Rt.add(this.hemi, this.sun, this.sun.target);
    this.cloudMaps = { day: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.day.cloud)), golden: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.golden.cloud)) };
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * Math.PI * 2 + 0.3, d = 620 + (i % 3) * 60, w = 130 + (i % 4) * 30;
      const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: this.cloudMaps.day[i % 4], color: new THREE.Color(1.1, 1.1, 1.1), transparent: true, depthWrite: false, fog: false }));
      m.position.set(Math.cos(a) * d, 110 + (i % 4) * 34, Math.sin(a) * d); m.scale.set(w, w / 2, 1); m.layers.set(NOINK);
      this.clouds.push(m); Rt.add(m);
    }
    const r = rng(7), b = new Batch();
    const grass = lam("nGrass", () => ({ map: rep(grassHD(), 1, 1) }));
    const dirt = lam("nDirt", () => ({ color: "#b89a6a" }));
    const canvas = lam("nCanvas", () => ({ color: "#efe6d4" }));
    const wood = lam("nWood", () => ({ map: beamHD() }));
    const plank = lam("nPlank", () => ({ map: planksHD() }));
    const pole = lam("nPole", () => ({ color: "#5a3a22" }));
    const leafs = ["#4f7a36", "#5f8a3e", "#6a9440", "#3f6a30"].map((c, i) => lam("nLeaf" + i, () => ({ color: c })));
    const pine = ["#2f5a32", "#35603a", "#2b5230"].map((c, i) => lam("nPine" + i, () => ({ color: c })));
    const bark = lam("nBark", () => ({ color: "#6a4a30" }));
    const rock = lam("nRock", () => ({ color: "#a39a8e" }));
    const hill = ["#7f9a72", "#94ac90", "#a9bcb4"].map((c, i) => lam("nHill" + i, () => ({ color: c })));
    const iron = lam("nIron", () => ({ color: "#5a5e66" }));
    const straw = lam("nStraw", () => ({ color: "#e0bf62" }));
    const tri = (c: string) => lam("nFlag" + c, () => ({ color: c, side: THREE.DoubleSide }));
    const mtx = (x: number, y: number, z: number, sx = 1, sy = 1, sz = 1, ry = 0) => new THREE.Matrix4().compose(V(x, y, z), new THREE.Quaternion().setFromEuler(new THREE.Euler(0, ry, 0)), V(sx, sy, sz));
    // ---------- FIELD (x 0 .. 120) ----------
    const gplane = (x0: number, x1: number, z0: number, z1: number, mat: THREE.Material, y = 0, tile = 6) => {
      const g = new THREE.PlaneGeometry(x1 - x0, z1 - z0); g.rotateX(-Math.PI / 2);
      const uv = g.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * (x1 - x0) / tile, uv.getY(i) * (z1 - z0) / tile);
      b.add(g, mat, mtx((x0 + x1) / 2, y, (z0 + z1) / 2));
    };
    gplane(-300, 400, -420, 80, grass);
    gplane(38, 130, -0.8, 3.2, dirt, 0.01, 4);
    const tree = (x: number, z: number, s: number) => {
      b.add(new THREE.CylinderGeometry(0.22 * s, 0.3 * s, 3 * s, 8), bark, mtx(x, 1.5 * s, z));
      if (r() < 0.55) for (let k = 0; k < 3; k++) b.add(new THREE.ConeGeometry((2.4 - k * 0.6) * s, (3.6 - k * 0.6) * s, 10), pine[(k + Math.floor(x)) % 3], mtx(x, (2.6 + k * 1.6) * s, z));
      else for (let k = 0; k < 4; k++) b.add(new THREE.IcosahedronGeometry((1.7 + r() * 0.6) * s, 1), leafs[(k + Math.floor(z)) % 4], mtx(x + (r() - 0.5) * 2.4 * s, (4 + r() * 1.4) * s, z + (r() - 0.5) * 2 * s));
    };
    for (let i = 0; i < 150; i++) tree(-90 + r() * 240, -62 - r() * 40, 0.9 + r() * 0.8);
    for (let i = 0; i < 26; i++) tree(-40 + r() * 140, -48 - r() * 8, 0.7 + r() * 0.5);
    for (let i = 0; i < 6; i++) { const g = new THREE.SphereGeometry(1, 32, 12, 0, Math.PI * 2, 0, Math.PI / 2); b.add(g, hill[i % 3], mtx(-260 + i * 120, -2, -230 - (i % 2) * 70, 130, 30 + (i % 3) * 14, 60)); }
    // camp: tents + tricolour flags
    for (let i = 0; i < 12; i++) {
      const x = -26 + i * 5 + r() * 2, z = -32 - (i % 3) * 4;
      b.add(new THREE.ConeGeometry(2, 3, 12), canvas, mtx(x, 1.5, z));
      if (i % 3 === 0) {
        b.add(new THREE.CylinderGeometry(0.04, 0.04, 5.5, 6), pole, mtx(x, 2.75, z));
        ["#2a4fa8", "#f6f1e6", "#d23a34"].forEach((c, k) => { const q = new THREE.Mesh(new THREE.PlaneGeometry(0.42, 0.85), tri(c)); q.position.set(x + 0.23 + k * 0.42, 5.0, z); q.castShadow = true; Rt.add(q); this.flags.push(q); });
      }
    }
    // the hero's flag by the camp (shot 1)
    b.add(new THREE.CylinderGeometry(0.035, 0.035, 3.0, 8), pole, mtx(0.75, 1.5, -1.6));
    ["#2a4fa8", "#f6f1e6", "#d23a34"].forEach((c, k) => { const q = new THREE.Mesh(new THREE.PlaneGeometry(0.33, 0.7), tri(c)); q.position.set(0.75 + 0.18 + k * 0.33, 2.55, -1.6); q.castShadow = true; Rt.add(q); this.flags.push(q); });
    // rocks + bushes
    for (let i = 0; i < 70; i++) {
      const x = -30 + r() * 140, z = -25 + r() * 20;
      if (r() < 0.35) b.add(new THREE.IcosahedronGeometry(0.25 + r() * 0.35, 0), rock, mtx(x, 0.08, z, 1.4, 0.6, 1));
      else for (let k = 0; k < 3; k++) b.add(new THREE.IcosahedronGeometry(0.45 + r() * 0.3, 1), leafs[k % 4], mtx(x + k * 0.5 - 0.5, 0.35, z + (k % 2) * 0.3));
    }
    // crates of rabbits (shot 9): 3 rows x 6, open fronts with iron bars
    const crate = (x: number, z: number, bars = true) => {
      b.add(boxGeo(V(x - 0.55, 0, z - 0.4), V(x + 0.55, 0.06, z + 0.4)), wood);
      b.add(boxGeo(V(x - 0.55, 0.62, z - 0.4), V(x + 0.55, 0.68, z + 0.4)), wood);
      b.add(boxGeo(V(x - 0.55, 0.06, z - 0.4), V(x + 0.55, 0.62, z - 0.34)), plank);
      for (const sx of [-1, 1]) b.add(boxGeo(V(x + sx * 0.55 - 0.03, 0.06, z - 0.4), V(x + sx * 0.55 + 0.03, 0.62, z + 0.4)), wood);
      b.add(boxGeo(V(x - 0.5, 0.06, z - 0.34), V(x + 0.5, 0.1, z + 0.38)), straw);
      if (bars) for (let k = -4; k <= 4; k++) b.add(new THREE.CylinderGeometry(0.012, 0.012, 0.56, 5), iron, mtx(x + k * 0.11, 0.34, z + 0.39));
    };
    for (let row = 0; row < 3; row++) for (let i = 0; i < 7; i++) crate(36 + i * 1.25 + (row % 2) * 0.6, -2 - row * 1.0);
    // hero crate with the opening door (shot 10)
    crate(40, -0.4, false);
    this.door.position.set(40 - 0.5, 0.06, -0.4 + 0.4);
    for (let k = 0; k <= 8; k++) { const m = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.56, 5), iron); m.position.set(0.05 + k * 0.112, 0.28, 0); m.castShadow = true; this.door.add(m); }
    const fr = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.04, 0.04), wood); fr.position.set(0.5, 0.56, 0); this.door.add(fr);
    const fr2 = fr.clone(); fr2.position.set(0.5, 0.02, 0); this.door.add(fr2);
    Rt.add(this.door);
    // ---------- open carriage (shots 18-19) ----------
    const coach = lam("nCoach", () => ({ color: "#1f4a3a" })), gold = lam("nGold", () => ({ color: "#e3b84a" })), wheel = lam("nWheel", () => ({ color: "#3a2a20" }));
    const body = new THREE.Mesh(boxGeo(V(-1.3, 0.75, -0.75), V(1.3, 1.55, 0.75), 0, true), coach); body.castShadow = true; this.carriage.add(body);
    const trim = new THREE.Mesh(boxGeo(V(-1.32, 1.5, -0.77), V(1.32, 1.6, 0.77)), gold); this.carriage.add(trim);
    const seat = new THREE.Mesh(boxGeo(V(1.3, 1.2, -0.6), V(1.9, 1.75, 0.6)), coach); this.carriage.add(seat);
    for (const [x, rr] of [[-0.9, 0.62], [1.0, 0.5]] as const) for (const z of [-0.8, 0.8]) {
      const w = new THREE.Mesh(new THREE.TorusGeometry(rr, 0.06, 6, 20), wheel); w.position.set(x, rr, z); w.castShadow = true; this.carriage.add(w); this.wheels.push(w);
      for (let s = 0; s < 6; s++) { const sp = new THREE.Mesh(new THREE.BoxGeometry(0.04, rr * 2, 0.04), gold); sp.rotation.z = (s * Math.PI) / 6; w.add(sp); }
    }
    const shaft = new THREE.Mesh(boxGeo(V(1.9, 0.7, -0.05), V(4.5, 0.8, 0.05)), wood); this.carriage.add(shaft);
    this.carriage.position.set(64, 0, 0.6); Rt.add(this.carriage);
    // ---------- WAR MAP TENT (x = 400) ----------
    const stripe = lam("nStripe", () => ({ map: rep(stripes("tentS", "#2f4f9a", "#efe6d4"), 3, 1) }));
    const red = lam("nStripeR", () => ({ map: rep(stripes("tentR", "#b8352a", "#efe6d4"), 3, 1) }));
    const rug = lam("nRug", () => ({ map: rugTex() }));
    for (const [x0, mat] of [[M, stripe], [T, red]] as const) {
      gplane(x0 - 6, x0 + 6, -4, 6, plank, 0.0, 2);
      b.add(boxGeo(V(x0 - 6, 0, -2.2), V(x0 + 6, 4.5, -2.0), 3), mat);
      b.add(boxGeo(V(x0 - 6, 0, -2.2), V(x0 - 5.8, 4.5, 6), 3), mat);
      b.add(boxGeo(V(x0 + 5.8, 0, -2.2), V(x0 + 6, 4.5, 6), 3), mat);
      gplane(x0 - 2.5, x0 + 2.5, -1.8, 2.2, rug, 0.012, 5);
      for (const x of [x0 - 4.5, x0 + 4.5]) b.add(new THREE.CylinderGeometry(0.06, 0.06, 4.5, 8), pole, mtx(x, 2.25, -1.9));
    }
    // easel + map
    for (const sx of [-0.62, 0.62]) b.add(boxGeo(V(M + sx - 0.04, 0, -0.6), V(M + sx + 0.04, 2.15, -0.52)), wood);
    b.add(boxGeo(V(M - 0.75, 0.5, -0.55), V(M + 0.75, 0.56, -0.4)), wood);
    this.map = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 1.64), new THREE.MeshBasicMaterial({ map: mapTex(0), color: new THREE.Color(0.92, 0.9, 0.86) }));
    this.map.position.set(M, 1.36, -0.5); this.map.receiveShadow = true; Rt.add(this.map);
    // candle table beside the easel
    b.add(boxGeo(V(M + 1.2, 0, -0.9), V(M + 1.9, 0.8, -0.3)), wood);
    // treaty table (x = 800)
    b.add(boxGeo(V(T - 0.9, 0.78, -0.45), V(T + 0.9, 0.85, 0.45)), plank);
    for (const sx of [-0.8, 0.8]) for (const sz of [-0.35, 0.35]) b.add(boxGeo(V(T + sx - 0.04, 0, sz - 0.04), V(T + sx + 0.04, 0.78, sz + 0.04)), wood);
    const paper = lam("nPaper", () => ({ map: parchTex() }));
    b.add(boxGeo(V(T - 0.24, 0.85, -0.17), V(T + 0.24, 0.853, 0.19)), paper);
    b.add(new THREE.CylinderGeometry(0.035, 0.035, 0.008, 20), lam("nSeal", () => ({ color: "#9a1e22" })), mtx(T + 0.16, 0.857, 0.13));
    b.add(new THREE.CylinderGeometry(0.04, 0.045, 0.07, 16), lam("nInk", () => ({ color: "#1a1620" })), mtx(T + 0.42, 0.885, -0.15));
    // ---------- FARM (x = 1200) ----------
    gplane(R - 60, R + 60, -60, 30, grass);
    const barn = lam("nBarn", () => ({ map: rep(barnTex(), 2, 1) })), roof = lam("nRoof", () => ({ map: rep(roofHD("#6a3a2e"), 3, 2) }));
    b.add(boxGeo(V(R - 9, 0, -14), V(R - 1, 5, -8), 4), barn);
    const rf = new THREE.CylinderGeometry(4.6, 4.6, 6.2, 3, 1); rf.rotateZ(Math.PI / 2); rf.rotateX(Math.PI / 6); b.add(rf, roof, mtx(R - 5, 6.0, -11, 1, 0.55, 1.05));
    for (let i = -20; i < 24; i++) { b.add(boxGeo(V(R + i * 1.4 - 0.06, 0, -4.06), V(R + i * 1.4 + 0.06, 1.0, -3.94)), wood); }
    for (const y of [0.45, 0.85]) b.add(boxGeo(V(R - 28, y, -4.03), V(R + 33.6, y + 0.08, -3.97)), wood);
    // hutch (shot 22)
    b.add(boxGeo(V(R - 1.4, 0, -1.6), V(R + 1.4, 0.06, -0.6)), wood);
    b.add(boxGeo(V(R - 1.4, 0.06, -1.6), V(R + 1.4, 0.9, -1.5)), plank);
    b.add(boxGeo(V(R - 1.45, 0.9, -1.65), V(R + 1.45, 0.98, -0.55)), wood);
    for (const sx of [-1.4, 1.4]) b.add(boxGeo(V(R + sx - 0.05, 0.06, -1.6), V(R + sx + 0.05, 0.9, -0.6)), wood);
    b.add(boxGeo(V(R - 1.35, 0.06, -1.5), V(R + 1.35, 0.12, -0.62)), straw);
    for (let i = 0; i < 8; i++) b.add(boxGeo(V(R + 8 + i * 1.3, 0, -7), V(R + 9.1 + i * 1.3, 0.7, -6.2)), straw);
    for (let i = 0; i < 40; i++) tree(R - 50 + r() * 100, -30 - r() * 25, 0.9 + r() * 0.7);
    b.build(Rt, true);
  }

  private actor(list: Actor[], i: number, geo?: THREE.BufferGeometry) { while (list.length <= i) list.push(geo ? new Actor(this.root, geo) : new Actor(this.root)); return list[i]; }
  private fx(i: number) { while (this.fxs.length <= i) this.fxs.push(new Fx(this.root)); return this.fxs[i]; }

  private shotSun(id: number, s: ShotDef, L: LightPreset) {
    let v = this.sunCache.get(id);
    if (v) return v;
    let fx = 0, fz = 0;
    for (let f = s.a; f < s.b; f += 3) { const c = camAt(id, f), x = c.look[0] - c.pos[0], z = c.look[2] - c.pos[2], n = Math.hypot(x, z) || 1; fx += x / n; fz += z / n; }
    const n = Math.hypot(fx, fz) || 1; fx /= n; fz /= n;
    const az = THREE.MathUtils.degToRad(L.az), el = THREE.MathUtils.degToRad(L.el);
    const hx = fx * Math.cos(az) - fz * Math.sin(az), hz = fz * Math.cos(az) + fx * Math.sin(az);
    v = new THREE.Vector3(hx * Math.cos(el), Math.sin(el), hz * Math.cos(el)).normalize();
    this.sunCache.set(id, v); return v;
  }

  update(id: number, f: number, cam: THREE.PerspectiveCamera, scene: THREE.Scene) {
    const t = f / FPS, s = SHOTS[id - 1], L = LIGHTS[s.light], K = LOOK[s.light], u = lt(id, f);
    const c = camAt(id, f);
    cam.position.set(...c.pos); cam.up.set(0, 1, 0); cam.lookAt(...c.look); cam.rotateZ(c.roll);
    cam.fov = c.fov; cam.near = 0.05; cam.far = 1500; cam.updateProjectionMatrix(); cam.updateMatrixWorld();
    const focus = V(...c.look), dist = cam.position.distanceTo(focus);
    cam.layers.enable(NOINK);
    const sunDir = this.shotSun(id, s, L);
    this.hemi.color.set(L.sky); this.hemi.groundColor.set(L.ground); this.hemi.intensity = L.hemiI;
    this.sun.color.set(L.sunCol); this.sun.intensity = L.sunI;
    const Rr = THREE.MathUtils.clamp(dist * 1.3 + 6, 8, 60);
    this.sun.position.copy(focus).addScaledVector(sunDir, 220); this.sun.target.position.copy(focus);
    const sc = this.sun.shadow.camera; sc.left = -Rr; sc.right = Rr; sc.top = Rr; sc.bottom = -Rr; sc.near = 20; sc.far = 480; sc.updateProjectionMatrix();
    this.sun.shadow.bias = L.bias; this.sun.shadow.normalBias = L.normalBias * (Rr / 12);
    TONE.uLitCol.value.set(...L.lit); TONE.uShadeCol.value.set(...L.shade); TONE.uShadeLift.value.set(...L.lift);
    TONE.uLambert.value = L.lambert; TONE.uSideK.value = L.sideK; TONE.uTerm.value = L.term; TONE.uBounce.value.set(...K.bounce); TONE.uSat.value = K.sat;
    CHAR.uCharTint.value.set(...L.charTint); CHAR.uCharShade.value = L.charShade; CHAR.uGrad.value = L.charGrad; CHAR.uBodyGrad.value = L.bodyGrad; CHAR.uSideTint.value.set(...L.sideTint);
    const su = this.skyMat.uniforms;
    K.sky.c.forEach((h, i) => untone(h, su["c" + i].value));
    const e = K.sky.e.map((deg) => THREE.MathUtils.degToRad(deg)); su.e.value.set(e[1], e[2], e[3], e[4]);
    this.sky.position.copy(cam.position);
    untone(L.fog, this.fog.color); this.fog.near = L.fogNear; this.fog.far = L.fogFar; scene.fog = this.fog; scene.background = null;
    this.sunDisc.visible = s.light === "golden";
    if (this.sunDisc.visible) { this.sunDisc.position.copy(cam.position).addScaledVector(sunDir, 900); this.sunDisc.scale.setScalar(2 * 900 * Math.tan(THREE.MathUtils.degToRad(1.7))); }
    for (let i = 0; i < this.clouds.length; i++) { const m = this.clouds[i]; m.lookAt(cam.position.x, m.position.y, cam.position.z); (m.material as THREE.MeshBasicMaterial).map = this.cloudMaps[s.light][i % 4]; }
    for (let i = 0; i < this.flags.length; i++) { const q = this.flags[i]; q.rotation.y = 0.18 * Math.sin(t * 4 + i * 0.7); }
    // ---- dynamic props ----
    const open = id === 10 ? Math.min(1, Math.max(0, (u - 0.28) / 0.25)) : id > 10 && id < 18 ? 1 : 0;
    this.door.rotation.y = -1.7 * (open < 1 ? open * open * (3 - 2 * open) : 1) - (id === 10 && u > 0.53 ? 0.08 * Math.sin((u - 0.53) * 20) * Math.exp(-(u - 0.53) * 6) : 0);
    let cx = 64, bounce = 0;
    if (id === 19) { cx = 64 + 16 * Math.min(1, u / 2.4) ** 1.2; bounce = Math.abs(Math.sin(u * 12)) * 0.05; }
    this.carriage.position.set(cx, bounce, 0.6);
    for (const w of this.wheels) w.rotation.z = -(cx - 64) / 0.55;
    const nConq = id === 2 ? CONQ.filter(([, t0]) => u >= t0).length : id > 2 ? CONQ.length : 0;
    if (nConq !== this.mapN) { (this.map.material as THREE.MeshBasicMaterial).map = mapTex(nConq); (this.map.material as THREE.MeshBasicMaterial).needsUpdate = true; this.mapN = nConq; }
    // ---- cast ----
    const items: Item[] = stage(id, f, u, { carriageX: cx, carriageY: bounce });
    let ti = 0, bi = 0, fi = 0;
    const used: (Actor | Fx)[] = [];
    for (const it of items) {
      if (it.kind === "fx") {
        const e2 = this.fx(fi++); e2.r = this.pool.req(it.key, it.cw ?? 512, it.ch ?? 512, 1, (p) => it.draw(p.g));
        e2.use(!!it.soft); e2.mesh.visible = true; e2.mesh.position.set(it.x, it.y, it.z);
        if (it.flat) e2.mesh.rotation.set(-Math.PI / 2, 0, it.rot ?? 0); else { e2.mesh.quaternion.copy(cam.quaternion); e2.mesh.rotateZ(it.rot ?? 0); }
        e2.mesh.scale.set(it.w ?? 1, it.h ?? 1, 1); used.push(e2); continue;
      }
      const bun = it.kind === "bunny";
      const a = bun ? this.actor(this.buns, bi++, BUNNY) : this.actor(this.toons, ti++);
      const d = cam.position.distanceTo(this.root.position.clone().set(it.x, it.y + 0.6, it.z)) / (it.scale ?? 1);
      const k = bun ? (d < 1.6 ? 2 : d < 5 ? 1 : 0.5) : (d < 2.5 ? 1.6 : d < 7 ? 1 : 0.5);
      const [w, h] = bun ? [400, 400] : [600, 1000];
      a.r = this.pool.req(it.key + "|" + k, Math.round(w * k), Math.round(h * k), k, (p) => it.draw(p.g));
      a.mesh.visible = true; a.mesh.position.set(it.x, it.y, it.z);
      a.mesh.rotation.set(0, Math.atan2(cam.position.x - it.x, cam.position.z - it.z), it.roll ?? 0);
      const sc2 = it.scale ?? 1; a.mesh.scale.set(it.mirror ? -sc2 : sc2, sc2, sc2);
      a.mesh.castShadow = L.actorShadow; used.push(a);
      if (!it.noShadow) {
        const ee = this.fx(fi++); const cc = s.light === "golden" ? "#c9a9b8" : "#a9a3c0";
        ee.r = this.pool.req(`blob|contact|${cc}`, 128, 128, 1, (p) => fxContact(p, cc));
        ee.use(false); ee.mesh.visible = true; ee.mesh.position.set(it.x, it.y + 0.012, it.z); ee.mesh.rotation.set(-Math.PI / 2, 0, 0);
        const wsz = (bun ? 0.42 : 0.62) * sc2; ee.mesh.scale.set(wsz, wsz * 0.75, 1); used.push(ee);
      }
    }
    for (let i = ti; i < this.toons.length; i++) this.toons[i].mesh.visible = false;
    for (let i = bi; i < this.buns.length; i++) this.buns[i].mesh.visible = false;
    for (let i = fi; i < this.fxs.length; i++) this.fxs[i].mesh.visible = false;
    this.pool.flush();
    for (const x of used) x.bind();
    return focus;
  }
}
