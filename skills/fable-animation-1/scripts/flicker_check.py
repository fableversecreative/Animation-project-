"""Find flicker frames in a finished short: a frame (or a patch of it) that differs from BOTH neighbours while the
neighbours agree with each other (A-B-A), at 160x284 grey in 16x16 tiles.
usage: python -I flicker_check.py video.mp4 [out_dir]   (writes a strip of the worst flicker frames if out_dir is given)"""
import subprocess, sys, json, os
import numpy as np

W, H, TS = 160, 284, 16
path = sys.argv[1]
out_dir = sys.argv[2] if len(sys.argv) > 2 else None
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
f = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
th, tw = H // TS, W // TS
tiles = f[:, : th * TS, : tw * TS].reshape(len(f), th, TS, tw, TS).mean(axis=(2, 4))
hits = []
for i in range(1, len(f) - 1):
    a, b, c = tiles[i - 1], tiles[i], tiles[i + 1]
    d_ab, d_bc, d_ac = np.abs(b - a), np.abs(c - b), np.abs(c - a)
    # flicker tile: frame i jumps away from both neighbours, which stay close to each other
    m = (d_ab > 10) & (d_bc > 10) & (d_ac < 0.4 * np.minimum(d_ab, d_bc))
    n = int(m.sum())
    if n:
        ys, xs = np.nonzero(m)
        hits.append({"frame": i, "t": round(i / 30, 2), "tiles": n, "where_y%": round(float(ys.mean()) / th * 100), "where_x%": round(float(xs.mean()) / tw * 100),
                     "jump": round(float(d_ab[m].mean()), 1)})
hits.sort(key=lambda h: -h["tiles"])
print(json.dumps({"frames": len(f), "flicker_frames": len(hits), "worst": hits[:25]}, indent=1))
if out_dir and hits:
    os.makedirs(out_dir, exist_ok=True)
    for h in hits[:8]:
        i = h["frame"]
        strip = np.concatenate([f[i - 1], f[i], f[i + 1]], axis=1).astype(np.uint8)
        pgm = os.path.join(out_dir, f"flicker_{i}.pgm")
        with open(pgm, "wb") as fh:
            fh.write(f"P5 {strip.shape[1]} {strip.shape[0]} 255\n".encode()); fh.write(strip.tobytes())
