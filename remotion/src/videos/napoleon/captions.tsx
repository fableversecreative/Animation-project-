// one-word pop captions from words.json (pop style: bold white, dark outline + soft shadow, key words yellow, y ~ 69 %)
import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import "@fontsource/poppins/900.css";
import { W, FPS } from "./story";
const KEY = new Set(["napoleon", "europe", "battle", "bunnies", "1807", "treaty", "hunt", "hundreds", "opened", "guns", "didn't", "straight", "swarmed", "legs",
  "whips", "nothing", "carriage", "too", "why", "wild", "tame", "man", "dinner"]);
const ENDS = [2.31, 4.32, 5.97, 9.8, 12.5, 16.1, 17.57, 19.54, 21.62, 23.74, 26.92, 29.12, 30.27, 33.04, 35.45, 36.3, 38.15, 39.92, 42.35, 44.02];
export const Captions: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  let i = -1;
  for (let k = 0; k < W.length; k++) if (t >= W[k][0] - 0.02) i = k;
  if (i < 0) return null;
  const [a, b, w] = W[i], next = i + 1 < W.length ? W[i + 1][0] : 99;
  const phraseEnd = ENDS.find((e) => Math.abs(e - b) < 0.03);
  const until = Math.min(next, phraseEnd !== undefined ? b + 0.2 : next, a + 1.1);
  if (t >= until) return null;
  const word = w.toLowerCase().replace(/[.,…]+$/g, "").replace(/\.\.\./g, "");
  const key = KEY.has(word.replace(/[!?]/g, ""));
  const u = (t - a) / 0.16, s = u < 1 ? 0.72 + 0.28 * (1 + 2.2 * (u - 1) ** 3 + 1.2 * (u - 1) ** 2) * (key ? 1.08 : 1) : key ? 1.08 : 1;
  return (
    <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center" }}>
      <div style={{ position: "absolute", top: 1325 - 70, width: "100%", textAlign: "center", fontFamily: "Poppins", fontWeight: 900, fontSize: 108,
        color: key ? "#ffd640" : "#ffffff", WebkitTextStroke: "14px #23142a", paintOrder: "stroke fill", textShadow: "0 8px 18px rgba(0,0,0,0.55)",
        transform: `scale(${s})`, letterSpacing: 1 }}>{word}</div>
    </AbsoluteFill>
  );
};
