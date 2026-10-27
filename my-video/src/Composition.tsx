import React from 'react';
import {
  Audio,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import { Atmosphere } from './components/Atmosphere';
import { Scene1Boot } from './scenes/Scene1Boot';
import { Scene2Astrolabe } from './scenes/Scene2Astrolabe';
import { Scene3Contracts } from './scenes/Scene3Contracts';
import { Scene4LevelUp } from './scenes/Scene4LevelUp';
import { THEME } from './theme';

export const MainDemoVideo: React.FC = () => {
  const frame = useCurrentFrame();

  // Subtitle script synced with ElevenLabs timing (at 30 fps)
  const subtitles = [
    { start: 10, end: 120, text: "System Alert. Hunter awakening sequence initiated." },
    { start: 130, end: 240, text: "Air-gapped core connected. Biometric astrolabe synchronized." },
    { start: 245, end: 360, text: "Neural fatigue: 0.0%. Focus Guard engaged." },
    { start: 370, end: 540, text: "Daily contracts active. All capital flows monitored in real time." },
    { start: 550, end: 720, text: "You are no longer bound by ordinary limits. Welcome back, Hunter." },
    { start: 730, end: 900, text: "The System has chosen you. Begin your ascent." },
  ];

  const currentSubtitle = subtitles.find(
    (s) => frame >= s.start && frame <= s.end
  );

  return (
    <div
      style={{
        flex: 1,
        backgroundColor: THEME.bg0,
        position: 'relative',
        width: '100%',
        height: '100%',
        overflow: 'hidden',
      }}
    >
      {/* Load Google Fonts */}
      <style>
        {`
          @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=Cinzel:wght@600;900&family=Rajdhani:wght@500;700&family=Share+Tech+Mono&display=swap');
          * {
            box-sizing: border-box;
          }
        `}
      </style>

      {/* Cybernetic Grid & Atmosphere */}
      <Atmosphere />

      {/* Optional ElevenLabs Voiceover Audio track */}
      {/* If public/voiceover.mp3 exists, it plays automatically */}
      <Audio
        src={staticFile('voiceover.mp3')}
        volume={(f) => interpolate(f, [0, 15, 870, 900], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })}
        onError={() => {
          // Graceful fallback if user has not yet dropped voiceover.mp3
        }}
      />

      {/* SCENE 1: SYSTEM BOOT (0s - 4.5s: Frames 0 - 135) */}
      <Sequence durationInFrames={140} name="Scene 1: System Boot">
        <Scene1Boot />
      </Sequence>

      {/* SCENE 2: BIOMETRIC ASTROLABE (4.5s - 12.5s: Frames 135 - 375) */}
      <Sequence from={135} durationInFrames={245} name="Scene 2: Biometric Astrolabe">
        <Scene2Astrolabe />
      </Sequence>

      {/* SCENE 3: CONTRACTS & CAPITAL REACTOR (12.5s - 22s: Frames 375 - 660) */}
      <Sequence from={375} durationInFrames={290} name="Scene 3: Daily Contracts">
        <Scene3Contracts />
      </Sequence>

      {/* SCENE 4: LEVEL UP AWAKENING (22s - 30s: Frames 660 - 900) */}
      <Sequence from={660} durationInFrames={240} name="Scene 4: Level Up">
        <Scene4LevelUp />
      </Sequence>

      {/* DIEGETIC CAPTION HUD BAR */}
      {currentSubtitle && (
        <div
          style={{
            position: 'absolute',
            bottom: 45,
            left: '50%',
            transform: 'translateX(-50%)',
            background: 'rgba(7, 0, 16, 0.88)',
            border: '1px solid rgba(0, 229, 255, 0.45)',
            boxShadow: '0 0 25px rgba(0, 229, 255, 0.3)',
            borderRadius: 8,
            padding: '10px 28px',
            fontFamily: THEME.fontHead,
            fontSize: 19,
            color: '#ffffff',
            letterSpacing: 2,
            textShadow: '0 0 10px rgba(0, 229, 255, 0.8)',
            zIndex: 100,
            whiteSpace: 'nowrap',
          }}
        >
          <span style={{ color: THEME.cyan, marginRight: 10 }}>[SYSTEM]</span>
          {currentSubtitle.text}
        </div>
      )}
    </div>
  );
};
