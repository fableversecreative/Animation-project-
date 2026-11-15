// Render look-check stills: bundles once, GPU via ANGLE, jpeg.
// usage: node scripts/stills.mjs <outPrefix> <frame,frame,...> [scale]
//   env COMP   = composition id (default BridgeShort)
//   env ENTRY  = entry file (default src/index.ts); point it at src/sandboxes/<n>/index.tsx to render a sandbox copy
//   env PROPS  = inputProps JSON
//   env REMOTION_TMP = a folder on a big drive (every bundle copies public/ into the temp folder and never deletes it)
//   env BROWSER = browser executable (default: Remotion's own headless shell, see `npx remotion browser ensure`)
import fs from "node:fs";
import path from "node:path";
if (process.env.REMOTION_TMP) { fs.mkdirSync(process.env.REMOTION_TMP, { recursive: true }); process.env.TEMP = process.env.TMP = process.env.REMOTION_TMP; }
const { bundle } = await import("@remotion/bundler");
const { renderStill, selectComposition } = await import("@remotion/renderer");
const [prefix, frames, scale = "0.5"] = process.argv.slice(2);
const browserExecutable = process.env.BROWSER || undefined;
const chromiumOptions = { gl: process.env.GL || "angle" };
const serveUrl = await bundle({ entryPoint: path.resolve(process.env.ENTRY || "src/index.ts"), publicDir: path.resolve("public") });
const inputProps = process.env.PROPS ? JSON.parse(process.env.PROPS) : {};
const composition = await selectComposition({ serveUrl, id: process.env.COMP || "BridgeShort", browserExecutable, chromiumOptions, inputProps });
const onBrowserLog = (l) => { if ((l.type === "error" || l.type === "warning") && !l.text.includes("404") && !l.text.includes("THREE.Clock")) console.log(`[${l.type}]`, l.text.slice(0, 300)); };
fs.mkdirSync(path.dirname(path.resolve(prefix + "x")), { recursive: true });
for (const f of frames.split(",").map(Number)) {
  const t0 = Date.now();
  await renderStill({ composition, serveUrl, frame: f, output: `${prefix}${f}.jpg`, imageFormat: "jpeg", jpegQuality: 88, scale: Number(scale), inputProps,
    browserExecutable, chromiumOptions, timeoutInMilliseconds: 180000, onBrowserLog });
  console.log("still", f, ((Date.now() - t0) / 1000).toFixed(1) + "s");
}
