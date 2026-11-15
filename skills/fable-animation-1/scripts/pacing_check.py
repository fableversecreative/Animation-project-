"""Visual pacing check for a finished short (same maths as references/reports/pacing.md).

usage: python pacing_check.py final.mp4   (exit code 1 if any target fails)

Samples 10 frames/s at 54x96 grey, skips the caption band (58-80 % of the height), and prints:
median MAD/s, hard changes, longest quiet run, last-10-s MAD vs median, and a PASS/FAIL per target.
Needs ffmpeg on PATH and numpy.
"""
import argparse, json, subprocess, sys
import numpy as np

W, H, FPS = 54, 96, 10
Y0, Y1 = int(H * 0.58), int(H * 0.80)


def frames(path):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={FPS},scale={W}:{H},format=gray", "-f", "rawvideo", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
    keep = np.r_[0:Y0, Y1:H]  # drop the caption band
    return a[:, keep, :]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    a = ap.parse_args()
    f = frames(a.video)
    n = len(f)
    dur = n / FPS
    mad = np.abs(f[1:] - f[:-1]).mean(axis=(1, 2))
    hist = np.stack([np.histogram(x, bins=16, range=(0, 256))[0] for x in f]).astype(np.float32)
    hd = np.abs(hist[1:] - hist[:-1]).sum(1) / (2 * hist[0].sum())
    t = np.arange(1, n) / FPS

    sec = int(np.ceil(dur))
    per = [float(mad[(t >= s) & (t < s + 1)].mean()) if ((t >= s) & (t < s + 1)).any() else 0.0 for s in range(sec)]
    med = float(np.median(per))
    hard = t[hd > 0.25]

    best, start, run = 0.0, 0.0, None
    for ti, m in zip(t, mad):
        if m < 1.5:
            run = ti if run is None else run
        else:
            if run is not None and ti - run > best:
                best, start = ti - run, run
            run = None
    if run is not None and t[-1] - run > best:
        best, start = t[-1] - run, run

    tail = float(np.mean(per[-10:])) if sec >= 10 else med
    checks = {
        "median MAD/s >= 15": med >= 15,
        "longest quiet <= 0.9 s": best <= 0.9,
        "last 10 s MAD >= median": tail >= med,
        "length 35-60 s": 35 <= dur <= 60,  # fable-animation-1: ~125-word scripts
    }
    out = {
        "duration_s": round(dur, 1),
        "median_mad": round(med, 1),
        "hard_changes": int(len(hard)),
        "hard_changes_per_10s": round(len(hard) / dur * 10, 1),
        "longest_quiet_s": round(best, 1),
        "longest_quiet_at": round(start, 1),
        "last10_mad": round(tail, 1),
        "mad_per_sec": [round(x, 1) for x in per],
        "checks": {k: "PASS" if v else "FAIL" for k, v in checks.items()},
    }
    print(json.dumps(out, indent=1))
    sys.exit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()
