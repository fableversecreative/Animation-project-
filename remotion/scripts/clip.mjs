// render a frame range to mp4 (linux helper). usage: node scripts/clip.mjs out.mp4 from to scale [concurrency]
import path from "node:path";
const { bundle } = await import("@remotion/bundler");
const { renderMedia, selectComposition } = await import("@remotion/renderer");
const [out, from, to, scale = "0.3333333", conc = "1"] = process.argv.slice(2);
const browserExecutable = process.env.BROWSER || undefined;
const chromiumOptions = { gl: process.env.GL || "swangle" };
const inputProps = process.env.PROPS ? JSON.parse(process.env.PROPS) : {};
let t0 = Date.now();
const serveUrl = await bundle({ entryPoint: path.resolve(process.env.ENTRY || "src/index.ts"), publicDir: path.resolve("public") });
const composition = await selectComposition({ serveUrl, id: process.env.COMP || "BridgeShort", browserExecutable, chromiumOptions, inputProps });
console.log("bundle+select", ((Date.now() - t0) / 1000).toFixed(1), "s"); t0 = Date.now();
await renderMedia({ composition, serveUrl, codec: "h264", outputLocation: out, frameRange: [Number(from), Number(to)], scale: Number(scale),
  concurrency: Number(conc), browserExecutable, chromiumOptions, inputProps, timeoutInMilliseconds: 600000,
  onProgress: ({ renderedFrames }) => { if (renderedFrames % 10 === 0) console.log("frames", renderedFrames, ((Date.now() - t0) / 1000).toFixed(1) + "s"); } });
const n = Number(to) - Number(from) + 1;
console.log("rendered", n, "frames in", ((Date.now() - t0) / 1000).toFixed(1), "s =", ((Date.now() - t0) / 1000 / n).toFixed(2), "s/frame");
