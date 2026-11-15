// Dump a short's timeline from its story.ts (bundled with esbuild): shots, total, camera moves, and any extra exports.
// usage: node scripts/dump_story.mjs <video folder name> [out.json]   e.g. node scripts/dump_story.mjs edo out/edo/story.json
import { build } from "esbuild";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
const [name, outFile] = process.argv.slice(2);
const tmp = path.resolve("out", `.story_${name}.mjs`);
await build({ entryPoints: [path.resolve("src/videos", name, "story.ts")], bundle: true, format: "esm", platform: "node", outfile: tmp, logLevel: "error" });
const S = await import(pathToFileURL(tmp).href + `?t=${Date.now()}`);
const data = {
  TOTAL: S.TOTAL, FPS: S.FPS, FLASH_AT: S.FLASH_AT,
  SHOTS: S.SHOTS.map((s) => ({ id: s.id, scene: s.scene, set: s.set, light: s.light, a: s.a, b: s.b })),
  XFADE: S.XFADE,
  CAM_MOVES: S.CAM_MOVES ? S.CAM_MOVES() : [],
  BELL_HITS: S.BELL_HITS ? S.BELL_HITS() : [],
  THROW_T: S.THROW_T ? S.THROW_T() : null,
  GRAB_T: S.GRAB_T ? S.GRAB_T() : null, FLIGHT: S.FLIGHT ?? null,
};
const json = JSON.stringify(data, null, 1);
if (outFile) fs.writeFileSync(outFile, json); else console.log(json);
fs.rmSync(tmp, { force: true });
