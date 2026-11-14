import React, { useLayoutEffect, useRef } from "react";
import { AbsoluteFill } from "remotion";
import { drawToon, drawBunny, drawBubble, musket, clipboard, stick, Who, Emo } from "./chars";
export const CharTest: React.FC = () => {
  const ref = useRef<HTMLCanvasElement>(null);
  useLayoutEffect(() => {
    const g = ref.current!.getContext("2d")!;
    g.fillStyle = "#e8dcc8"; g.fillRect(0, 0, 1080, 1920);
    const cell = (i: number, fn: (g: CanvasRenderingContext2D) => void, w = 600, h = 1000, x = 0, y = 0, s = 0.6) => {
      g.save(); g.translate(x, y); g.scale(s, s); fn(g); g.restore();
    };
    const cast: [Who, Emo, object][] = [["napoleon", "proud", {}], ["berthier", "smug", { prop: clipboard, aL: [70, 110], elL: 60 }], ["tsar", "happy", {}],
      ["hunter", "determined", { aL: [100, 100], aR: [72, 70], prop: musket }], ["hunter2", "angry", { aL: [150, 110], prop: stick(-0.5) }], ["farmer", "happy", {}]];
    cast.forEach(([w, e, p], i) => cell(i, (gg) => drawToon(gg, w, e, p as any), 600, 1000, (i % 3) * 360, Math.floor(i / 3) * 620, 0.6));
    const emos: Emo[] = ["worried", "scared", "shocked", "deadpan", "excited", "confused"];
    emos.forEach((e, i) => cell(i, (gg) => drawToon(gg, "napoleon", e, e === "scared" ? { aL: [150, 110], aR: [-150, 110] } : {}), 600, 1000, (i % 6) * 180, 1240, 0.3));
    const bun: any[] = [{ col: "white" }, { col: "brown", view: "front", face: "wide" }, { col: "grey", face: "happy", mouth: "grin", napkin: true }, { col: "spot", stretch: 0.6, hop: 0.4 }, { col: "wild", face: "angry", mouth: "flat" }, { col: "cream", view: "back" }];
    bun.forEach((b, i) => cell(i, (gg) => drawBunny(gg, b), 400, 400, (i % 6) * 180, 1560, 0.45));
    cell(0, (gg) => drawBubble(gg, "dinner"), 512, 512, 760, 1700, 0.4);
  }, []);
  return <AbsoluteFill><canvas ref={ref} width={1080} height={1920} /></AbsoluteFill>;
};
