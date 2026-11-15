"""Camera speed of a finished short: frame-to-frame global shift in 720p pixels per frame.
usage: python -I cam_speed.py video.mp4 [t0 dur]
Each frame is shrunk to 90x160 grey (caption band 58-80 % of the height skipped); the best shift within +-10 px
(= +-80 px at 720p) is the camera speed. Frames whose best match is still poor are cuts / flashes and are dropped.
Reference (references/reports/motion.md, 20 reference shorts): move peaks ~14 px/f median, p90 ~17 px/f overall,
moves ease in and out over ~23 f, the camera is almost never dead still, whips (45-93 px/f) are rare and blurred."""
import subprocess, sys, json
import numpy as np

W, H, R = 90, 160, 10
Y0, Y1 = int(H * 0.58), int(H * 0.8)
path = sys.argv[1]
t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
dur = float(sys.argv[3]) if len(sys.argv) > 3 else 1e9
cmd = ["ffmpeg", "-v", "error", "-ss", str(t0), "-i", path, "-t", str(min(dur, 3600)), "-vf", f"fps=30,scale={W}:{H},format=gray", "-f", "rawvideo", "-"]
f = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.uint8).reshape(-1, H, W).astype(np.float32)
rows = np.array([y for y in range(R, H - R, 2) if not (Y0 - R <= y < Y1 + R)])
cols = np.arange(R, W - R, 2)
speeds, res = [], []
for a, b in zip(f[:-1], f[1:]):
    A = a[np.ix_(rows, cols)]
    best = (1e9, 0, 0)
    for dy in range(-R, R + 1):
        for dx in range(-R, R + 1):
            s = np.abs(A - b[np.ix_(rows + dy, cols + dx)]).mean()
            if s < best[0]: best = (s, dx, dy)
    speeds.append(np.hypot(best[1], best[2]) * 8); res.append(best[0])
s, r = np.array(speeds), np.array(res)
ok = s[r < 18]
q = lambda p: round(float(np.percentile(ok, p)), 1)
print(json.dumps({"frames": len(s), "cuts_or_flashes": int((r >= 18).sum()), "median": q(50), "p75": q(75), "p90": q(90), "p97": q(97),
                  "still_lt1": round(float((ok < 1).mean()), 2), "ge16": round(float((ok >= 16).mean()), 2), "ge40": round(float((ok >= 40).mean()), 2)}))
