import React from "react";
import { Composition } from "remotion";
import { Main } from "./Main";
import timeline from "./data/timeline.json";

export const Root: React.FC = () => (
  <Composition
    id="PubMeta"
    component={Main}
    width={1080}
    height={1920}
    fps={timeline.fps}
    durationInFrames={Math.round(timeline.duration * timeline.fps)}
  />
);
