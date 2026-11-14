import React from "react";
import { Composition } from "remotion";
import { BridgeShort, BRIDGE_FRAMES } from "./videos/bridge/Bridge";
import { NapoleonShort, NAP_FRAMES } from "./videos/napoleon/Napoleon";
import { CharTest } from "./videos/napoleon/CharTest";

// One <Composition> per short. Each short lives in src/videos/<name>/.
export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="NapoleonShort" component={NapoleonShort} durationInFrames={NAP_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="BridgeShort" component={BridgeShort} durationInFrames={BRIDGE_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="CharTest" component={CharTest} durationInFrames={1} fps={30} width={1080} height={1920} />
  </>
);
