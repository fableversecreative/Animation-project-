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
// project light presets: bridge rig, golden shadows lifted (the ground read navy), fog pushed back
const NL: Record<"day" | "golden", LightPreset> = {
  day: { ...LIGHTS.day, el: 42, fogNear: 60, fogFar: 520, lit: [1.5, 1.44, 1.3], shade: [0.42, 0.4, 0.5], lift: [0.08, 0.09, 0.14] },
  golden: { ...LIGHTS.golden, el: 13, fogNear: 70, fogFar: 520, lit: [1.45, 0.86, 0.5], shade: [0.42, 0.33, 0.44], lift: [0.12, 0.09, 0.15], charTint: [1.0, 0.86, 0.72] },
};
const tuftTex = () => ctex("tuft", 256, 256, (g, r) => {
  for (let i = 0; i < 34; i++) {
    const x = 128 + (r() - 0.5) * 190, h = 60 + r() * 110, w = 6 + r() * 6, lean = (r() - 0.5) * 70;
    g.beginPath(); g.moveTo(x - w, 256); g.quadraticCurveTo(x - w * 0.3 + lean * 0.4, 256 - h * 0.6, x + lean, 256 - h); g.quadraticCurveTo(x + w * 0.3 + lean * 0.4, 256 - h * 0.6, x + w, 256); g.closePath();
    g.fillStyle = ["#6fae3e", "#7cba48", "#62a238", "#88c652"][i % 4]; g.fill(); g.lineWidth = 1.5; g.strokeStyle = "rgba(50,80,30,0.55)"; g.stroke();
  }
});
const flowerTex = () => ctex("flowers", 256, 256, (g, r) => {
  for (let i = 0; i < 9; i++) {
    const x = 50 + r() * 156, y = 120 + r() * 90, c = ["#f7f3e8", "#f4d24a", "#f3a9bb", "#c9a6f0"][i % 4];
    g.strokeStyle = "#4f8a2c"; g.lineWidth = 4; g.beginPath(); g.moveTo(x, 256); g.lineTo(x + (r() - 0.5) * 20, y); g.stroke();
    for (let k = 0; k < 5; k++) { const a = (k / 5) * Math.PI * 2; g.beginPath(); g.arc(x + Math.cos(a) * 9, y + Math.sin(a) * 9, 7, 0, 7); g.fillStyle = c; g.fill(); g.lineWidth = 2; g.strokeStyle = "rgba(60,40,40,0.7)"; g.stroke(); }
    g.beginPath(); g.arc(x, y, 5, 0, 7); g.fillStyle = "#e8a020"; g.fill();
  }
});
const patchTex = () => ctex("patches", 1024, 1024, (g, r) => {
  g.clearRect(0, 0, 1024, 1024);
  for (let i = 0; i < 70; i++) { const x = r() * 1024, y = r() * 1024, rr = 40 + r() * 130, dk = r() < 0.55;
    const gr = g.createRadialGradient(x, y, 0, x, y, rr); gr.addColorStop(0, dk ? "rgba(40,90,30,0.42)" : "rgba(170,210,90,0.38)"); gr.addColorStop(1, "rgba(0,0,0,0)"); g.fillStyle = gr; g.fillRect(x - rr, y - rr, rr * 2, rr * 2); }
  for (let i = 0; i < 900; i++) { g.fillStyle = ["rgba(250,245,230,0.9)", "rgba(245,210,80,0.9)", "rgba(240,170,190,0.85)"][i % 3]; g.beginPath(); g.arc(r() * 1024, r() * 1024, 1.6 + r() * 1.6, 0, 7); g.fill(); }
});
const smokeTex = () => ctex("smoke", 256, 256, (g) => {
  const gr = g.createRadialGradient(128, 128, 10, 128, 128, 124); gr.addColorStop(0, "rgba(170,165,175,0.6)"); gr.addColorStop(0.6, "rgba(170,165,175,0.25)"); gr.addColorStop(1, "rgba(170,165,175,0)"); g.fillStyle = gr; g.fillRect(0, 0, 256, 256);
});
const flameTex = () => ctex("flame", 128, 256, (g) => {
  g.beginPath(); g.moveTo(64, 10); g.quadraticCurveTo(120, 150, 64, 250); g.quadraticCurveTo(8, 150, 64, 10); g.fillStyle = "#ffb43a"; g.fill();
  g.beginPath(); g.moveTo(64, 80); g.quadraticCurveTo(96, 170, 64, 240); g.quadraticCurveTo(32, 170, 64, 80); g.fillStyle = "#fff0a0"; g.fill();
});
const eagleTex = () => ctex("eagle", 256, 256, (g) => {
  g.fillStyle = "#e3b84a"; g.strokeStyle = "#5a3a10"; g.lineWidth = 6;
  g.beginPath(); g.moveTo(128, 60); g.lineTo(150, 100); g.lineTo(230, 70); g.lineTo(170, 150); g.lineTo(150, 200); g.lineTo(106, 200); g.lineTo(86, 150); g.lineTo(26, 70); g.lineTo(106, 100); g.closePath(); g.fill(); g.stroke();
  g.fillRect(70, 205, 116, 20); g.strokeRect(70, 205, 116, 20);
});
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
  private fires: { x: number; z: number; fl: THREE.Mesh; puffs: THREE.Mesh[] }[] = [];
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
      m.position.set(Math.cos(a) * d, 250 + (i % 4) * 45, Math.sin(a) * d); m.scale.set(w, w / 2, 1); m.layers.set(NOINK);
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
    const hill = ["#4f7344", "#5a7d4e", "#6f8f72"].map((c, i) => lam("nHill" + i, () => ({ color: c })));
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
    const leafM = ["#3f6e30", "#4a7d36", "#56893a", "#36602a"].map((c, i) => lam("nLeafS" + i, () => ({ color: c })));
    const pineM = ["#24482c", "#2b5232", "#21432a"].map((c, i) => lam("nPineS" + i, () => ({ color: c })));
    const SPH = new THREE.SphereGeometry(1, 16, 12), CONE = new THREE.ConeGeometry(1, 1, 16);
    const tree = (x: number, z: number, s: number) => {
      b.add(new THREE.CylinderGeometry(0.2 * s, 0.32 * s, 3.2 * s, 10), bark, mtx(x, 1.6 * s, z));
      if (r() < 0.45) for (let k = 0; k < 4; k++) b.add(CONE, pineM[(((k + Math.floor(x)) % 3) + 3) % 3], mtx(x, (2.3 + k * 1.35) * s, z, (2.5 - k * 0.55) * s, (3.2 - k * 0.45) * s, (2.5 - k * 0.55) * s));
      else {
        const n = 5 + Math.floor(r() * 3);
        for (let k = 0; k < n; k++) { const a = (k / n) * Math.PI * 2, rr = k === 0 ? 0 : 1.3 * s, sz = (1.5 + r() * 0.7) * s;
          b.add(SPH, leafM[(((k + Math.floor(z)) % 4) + 4) % 4], mtx(x + Math.cos(a) * rr, (4.6 + (k === 0 ? 1.0 : r() * 0.8)) * s, z + Math.sin(a) * rr * 0.7, sz, sz * 0.86, sz)); }
      }
    };
    for (let i = 0; i < 150; i++) tree(-90 + r() * 240, -62 - r() * 40, 0.9 + r() * 0.8);
    for (let i = 0; i < 26; i++) tree(-40 + r() * 140, -48 - r() * 8, 0.7 + r() * 0.5);
    for (let i = 0; i < 6; i++) { const g = new THREE.SphereGeometry(1, 32, 12, 0, Math.PI * 2, 0, Math.PI / 2); b.add(g, hill[i % 3], mtx(-260 + i * 120, -2, -260 - (i % 2) * 60, 140, 18 + (i % 3) * 8, 60)); }
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
      else for (let k = 0; k < 3; k++) { const sz = 0.45 + r() * 0.3; b.add(SPH, leafM[k % 4], mtx(x + k * 0.5 - 0.5, 0.3, z + (k % 2) * 0.3, sz, sz * 0.8, sz)); }
    }
    const gold = lam("nGold", () => ({ color: "#e3b84a" }));
    // camp life: cannons, barrels, stacked muskets, crates, campfire, eagle standards
    const bronze = lam("nBronze", () => ({ color: "#b0823a" })), dark = lam("nDark", () => ({ color: "#3a3a42" }));
    const cannon = (x: number, z: number, ry: number) => {
      const m = mtx(x, 0, z, 1, 1, 1, ry);
      const bar = new THREE.CylinderGeometry(0.11, 0.17, 1.9, 14); bar.rotateZ(Math.PI / 2 - 0.12); bar.translate(0.2, 0.62, 0); b.add(bar, bronze, m);
      b.add(boxGeo(V(-0.9, 0.3, -0.18), V(0.5, 0.5, 0.18)), wood, m);
      for (const zz of [-0.32, 0.32]) { const w = new THREE.CylinderGeometry(0.42, 0.42, 0.07, 16); w.rotateX(Math.PI / 2); w.translate(0, 0.42, zz); b.add(w, wood, m); }
      for (let k = 0; k < 4; k++) b.add(new THREE.SphereGeometry(0.075, 10, 8), dark, mtx(x + 0.8 + (k % 2) * 0.16, 0.075 + Math.floor(k / 2) * 0.12, z + 0.5 + (k % 2) * 0.08));
    };
    [[-6, -22, 0.4], [9, -24, -0.3], [22, -21, 0.2], [48, -16, -0.5]].forEach(([x, z, ry]) => cannon(x, z, ry));
    const barrel = (x: number, z: number) => { b.add(new THREE.CylinderGeometry(0.3, 0.3, 0.85, 16), wood, mtx(x, 0.425, z)); for (const y of [0.15, 0.7]) b.add(new THREE.CylinderGeometry(0.31, 0.31, 0.05, 16), dark, mtx(x, y, z)); };
    for (let i = 0; i < 18; i++) barrel(-14 + r() * 70, -18 - r() * 12);
    const stack = (x: number, z: number) => { for (let k = 0; k < 4; k++) { const a = (k / 4) * Math.PI * 2, g = new THREE.CylinderGeometry(0.02, 0.02, 1.7, 5); g.rotateX(0.32); g.rotateY(a); b.add(g, pole, mtx(x + Math.sin(a) * 0.18, 0.8, z + Math.cos(a) * 0.18)); } };
    for (let i = 0; i < 10; i++) stack(-10 + i * 6 + r() * 2, -14 - r() * 4);
    for (let i = 0; i < 6; i++) { const x = -8 + i * 11, z = -27; b.add(new THREE.CylinderGeometry(0.03, 0.03, 3.4, 6), pole, mtx(x, 1.7, z));
      const e = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 0.6), new THREE.MeshLambertMaterial({ map: eagleTex(), transparent: true, alphaTest: 0.5, side: THREE.DoubleSide })); e.position.set(x, 3.6, z); Rt.add(e); }
    this.fires = [[3, -17], [27, -19], [56, -15]].map(([x, z]) => {
      for (let k = 0; k < 4; k++) { const g = new THREE.CylinderGeometry(0.06, 0.06, 0.9, 6); g.rotateZ(Math.PI / 2); g.rotateY(k * 0.8); b.add(g, bark, mtx(x, 0.08, z)); }
      const fl = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 1.0), new THREE.MeshBasicMaterial({ map: flameTex(), transparent: true, depthWrite: false, color: new THREE.Color(2.2, 1.6, 1.0) }));
      fl.position.set(x, 0.55, z); fl.layers.set(NOINK); Rt.add(fl);
      const puffs = [0, 1, 2, 3, 4].map(() => { const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: smokeTex(), transparent: true, depthWrite: false, opacity: 0.6 })); m.layers.set(NOINK); Rt.add(m); return m; });
      return { x, z, fl, puffs };
    });
    // ground: broad light/dark patches + flower dabs (overlay, no ink), grass tufts + flower clumps as crossed cards
    const pm = new THREE.Mesh(new THREE.PlaneGeometry(220, 120), new THREE.MeshLambertMaterial({ map: rep(patchTex(), 4, 2), transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2 }));
    pm.rotation.x = -Math.PI / 2; pm.position.set(40, 0.02, -30); pm.layers.set(NOINK); pm.receiveShadow = true; Rt.add(pm);
    const pf = pm.clone(); pf.position.set(R, 0.02, -15); Rt.add(pf);
    const tuftM = lam("nTuft", () => ({ map: tuftTex(), alphaTest: 0.5, side: THREE.DoubleSide })), flowM = lam("nFlow", () => ({ map: flowerTex(), alphaTest: 0.5, side: THREE.DoubleSide }));
    const cross = (x: number, z: number, h: number, m: THREE.Material) => { for (const a of [0, Math.PI / 2]) { const g = new THREE.PlaneGeometry(h, h); g.translate(0, h / 2, 0); g.rotateY(a + r()); b.add(g, m, mtx(x, 0, z)); } };
    const near = [[-4, 12, -6, 10], [4, 18, -4, 7], [20, 40, -3, 9], [26, 40, -1, 7], [38, 82, -1, 11], [-24, -16, -60, -55], [R - 8, R + 12, -3, 12]];
    for (const [x0, x1, z0, z1] of near) {
      const n = Math.round((x1 - x0) * (z1 - z0) * 3.2);
      for (let i = 0; i < n; i++) { const x = x0 + r() * (x1 - x0), z = z0 + r() * (z1 - z0); cross(x, z, 0.1 + r() * 0.12, r() < 0.88 ? tuftM : flowM); }
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
    const coach = lam("nCoach", () => ({ color: "#2a5a40" })), wheel = lam("nWheel", () => ({ color: "#3a2a20" }));
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
    // tent dressing: lanterns (warm glow), chairs, chests, banners
    const glowM = new THREE.MeshBasicMaterial({ color: new THREE.Color(2.4, 1.7, 0.8) });
    for (const x0 of [M, T]) {
      for (const lx of [-3.2, 3.2]) { b.add(new THREE.CylinderGeometry(0.01, 0.01, 1.2, 4), dark, mtx(x0 + lx, 3.7, -1.2)); const lg = new THREE.Mesh(new THREE.SphereGeometry(0.13, 12, 10), glowM); lg.position.set(x0 + lx, 3.0, -1.2); Rt.add(lg);
        const pl = new THREE.PointLight("#ffc070", 6, 7, 1.6); pl.position.set(x0 + lx, 2.9, -1.0); Rt.add(pl); }
      for (const cx2 of [-2.4, 2.4]) { b.add(boxGeo(V(x0 + cx2 - 0.25, 0.42, -1.2), V(x0 + cx2 + 0.25, 0.48, -0.7)), wood); b.add(boxGeo(V(x0 + cx2 - 0.25, 0.48, -1.22), V(x0 + cx2 + 0.25, 1.1, -1.16)), wood);
        for (const [dx, dz] of [[-0.22, -1.18], [0.22, -1.18], [-0.22, -0.72], [0.22, -0.72]]) b.add(boxGeo(V(x0 + cx2 + dx - 0.025, 0, dz - 0.025), V(x0 + cx2 + dx + 0.025, 0.42, dz + 0.025)), wood); }
      b.add(boxGeo(V(x0 - 4.4, 0, -1.9), V(x0 - 3.4, 0.6, -1.3)), lam("nChest", () => ({ color: "#6a3a22" }))); b.add(boxGeo(V(x0 - 4.42, 0.25, -1.92), V(x0 - 3.38, 0.32, -1.28)), gold);
      for (const bx of [-1.6, 1.6]) { const bn = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 1.6), lam("nBan", () => ({ color: "#2b4aa8", side: THREE.DoubleSide }))); bn.position.set(x0 + bx, 3.0, -1.95); Rt.add(bn);
        const ea = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 0.6), new THREE.MeshLambertMaterial({ map: eagleTex(), transparent: true, alphaTest: 0.5 })); ea.position.set(x0 + bx, 3.1, -1.93); Rt.add(ea); }
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
    b.add(boxGeo(V(R + 2.2, 0, -2.6), V(R + 4.2, 0.45, -2.0)), wood); b.add(boxGeo(V(R + 2.3, 0.38, -2.5), V(R + 4.1, 0.42, -2.1)), lam("nWater", () => ({ color: "#5aa0c8" })));
    for (const [x, z] of [[R - 2.2, -0.4], [R + 1.9, -1.0], [R + 4.6, 0.6]]) { b.add(new THREE.CylinderGeometry(0.16, 0.13, 0.3, 14), lam("nBucket", () => ({ color: "#9a9a9e" })), mtx(x, 0.15, z)); }
    for (let i = 0; i < 6; i++) b.add(new THREE.SphereGeometry(0.55, 14, 10), straw, mtx(R + 9 + i * 1.2, 0.3, -2.4 + (i % 2) * 0.6, 1, 0.55, 1));
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
    const SUN_AZ: Record<number, number> = { 22: 120, 23: 140, 24: 140 };
    const az = THREE.MathUtils.degToRad(SUN_AZ[id] ?? L.az), el = THREE.MathUtils.degToRad(L.el);
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
    for (const fr of this.fires) {
      fr.fl.quaternion.copy(cam.quaternion); fr.fl.scale.set(1 + 0.12 * Math.sin(t * 13), 1 + 0.18 * Math.sin(t * 17 + 1), 1);
      fr.puffs.forEach((m, k) => { const uu = (t * 0.3 + k / 5) % 1, sz = 0.35 + uu * 1.1; m.position.set(fr.x - uu * 0.8, 0.9 + uu * 2.6, fr.z); m.scale.set(sz, sz, 1); m.quaternion.copy(cam.quaternion); (m.material as THREE.MeshBasicMaterial).opacity = 0.32 * (1 - uu); });
    }
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
