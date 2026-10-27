import React from 'react';
import { Composition } from 'remotion';
import { MainDemoVideo } from './Composition';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 16:9 Landscape (YouTube, X, Portfolio) */}
      <Composition
        id="ApexGhost-Landscape-16x9"
        component={MainDemoVideo}
        durationInFrames={900}
        fps={30}
        width={1920}
        height={1080}
      />

      {/* 9:16 Vertical (TikTok, Instagram Reels, YouTube Shorts) */}
      <Composition
        id="ApexGhost-Vertical-9x16"
        component={MainDemoVideo}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};
