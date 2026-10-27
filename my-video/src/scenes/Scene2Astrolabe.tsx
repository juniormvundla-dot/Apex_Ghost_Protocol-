import React from 'react';
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { THEME } from '../theme';

export const Scene2Astrolabe: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Astrolabe rotation angles
  const ring1Rot = frame * 0.75;
  const ring2Rot = -frame * 0.45;
  const ring3Rot = frame * 1.2;

  // Stats interpolation
  const strVal = Math.floor(interpolate(frame, [0, 80], [45, 96], { extrapolateRight: 'clamp' }));
  const agiVal = Math.floor(interpolate(frame, [0, 80], [50, 112], { extrapolateRight: 'clamp' }));
  const intVal = Math.floor(interpolate(frame, [0, 80], [60, 135], { extrapolateRight: 'clamp' }));
  const focVal = Math.floor(interpolate(frame, [0, 80], [55, 120], { extrapolateRight: 'clamp' }));

  // Entrance spring
  const scale = spring({ frame, fps, config: { damping: 15 } });

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 100px',
        boxSizing: 'border-box',
      }}
    >
      {/* LEFT: Orbital Biometric Avatar Core */}
      <div
        style={{
          position: 'relative',
          width: 440,
          height: 440,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transform: `scale(${scale})`,
        }}
      >
        {/* Outer Astrolabe Ring with Runic Ticks */}
        <div
          style={{
            position: 'absolute',
            width: 420,
            height: 420,
            borderRadius: '50%',
            border: '2px dashed rgba(0, 229, 255, 0.4)',
            boxShadow: '0 0 25px rgba(0, 229, 255, 0.2)',
            transform: `rotate(${ring1Rot}deg)`,
          }}
        />

        {/* Counter-Rotating Mid Ring */}
        <div
          style={{
            position: 'absolute',
            width: 360,
            height: 360,
            borderRadius: '50%',
            border: '1px solid rgba(157, 51, 255, 0.5)',
            borderTop: '3px solid #00e5ff',
            borderBottom: '3px solid #ffd700',
            transform: `rotate(${ring2Rot}deg)`,
          }}
        />

        {/* High Frequency Inner Ring */}
        <div
          style={{
            position: 'absolute',
            width: 310,
            height: 310,
            borderRadius: '50%',
            border: '1px dotted rgba(255, 215, 0, 0.5)',
            transform: `rotate(${ring3Rot}deg)`,
          }}
        />

        {/* Center Avatar Container */}
        <div
          style={{
            width: 250,
            height: 250,
            borderRadius: '50%',
            overflow: 'hidden',
            border: '3px solid rgba(0, 229, 255, 0.8)',
            boxShadow: '0 0 35px rgba(0, 229, 255, 0.6), inset 0 0 25px rgba(157, 51, 255, 0.5)',
            position: 'relative',
          }}
        >
          <Img
            src={staticFile('jinwoo.jpg')}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
            }}
          />
          {/* Bio-reactive luminescence overlay */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              background: 'radial-gradient(circle, transparent 40%, rgba(0, 229, 255, 0.3) 100%)',
              mixBlendMode: 'screen',
            }}
          />
        </div>

        {/* Badge: S-RANK HUNTER */}
        <div
          style={{
            position: 'absolute',
            bottom: 15,
            backgroundColor: 'rgba(7, 0, 16, 0.92)',
            border: '1px solid #ffd700',
            boxShadow: THEME.goldGlow,
            borderRadius: 20,
            padding: '6px 20px',
            fontFamily: THEME.fontHead,
            fontSize: 13,
            color: '#ffd700',
            letterSpacing: 2,
            zIndex: 10,
          }}
        >
          RANK: S-CLASS HUNTER
        </div>
      </div>

      {/* RIGHT: Live Attribute Telemetry HUD Panel */}
      <div
        style={{
          width: 580,
          background: 'rgba(13, 0, 24, 0.8)',
          border: '1px solid rgba(157, 51, 255, 0.45)',
          borderRadius: 10,
          padding: '30px 36px',
          boxShadow: '0 0 30px rgba(123, 0, 204, 0.25)',
          backdropFilter: 'blur(16px)',
          display: 'flex',
          flexDirection: 'column',
          gap: 20,
          transform: `scale(${scale})`,
        }}
      >
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            borderBottom: '1px solid rgba(0, 229, 255, 0.3)',
            paddingBottom: 12,
          }}
        >
          <span
            style={{
              fontFamily: THEME.fontHead,
              fontSize: 18,
              color: THEME.cyan,
              letterSpacing: 2,
              textShadow: THEME.cyanGlow,
            }}
          >
            ◆ NEURAL CORE TELEMETRY
          </span>
          <span
            style={{
              fontFamily: THEME.fontMono,
              fontSize: 13,
              color: THEME.green,
              border: '1px solid #00ff88',
              padding: '2px 10px',
              borderRadius: 4,
            }}
          >
            FATIGUE: 0.0% [OPTIMAL]
          </span>
        </div>

        {/* Attribute Progress Bars */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {/* STRENGTH */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: THEME.fontMono, fontSize: 13, color: '#ff6b6b', marginBottom: 4 }}>
              <span>STRENGTH [STR]</span>
              <span>{strVal} / 150</span>
            </div>
            <div style={{ width: '100%', height: 7, background: 'rgba(255, 107, 107, 0.15)', borderRadius: 4, overflow: 'hidden' }}>
              <div style={{ width: `${(strVal / 150) * 100}%`, height: '100%', background: '#ff6b6b', boxShadow: '0 0 10px #ff6b6b' }} />
            </div>
          </div>

          {/* AGILITY */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: THEME.fontMono, fontSize: 13, color: '#44ff99', marginBottom: 4 }}>
              <span>AGILITY [AGI]</span>
              <span>{agiVal} / 150</span>
            </div>
            <div style={{ width: '100%', height: 7, background: 'rgba(68, 255, 153, 0.15)', borderRadius: 4, overflow: 'hidden' }}>
              <div style={{ width: `${(agiVal / 150) * 100}%`, height: '100%', background: '#44ff99', boxShadow: '0 0 10px #44ff99' }} />
            </div>
          </div>

          {/* INTELLIGENCE */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: THEME.fontMono, fontSize: 13, color: '#44ddff', marginBottom: 4 }}>
              <span>INTELLIGENCE [INT]</span>
              <span>{intVal} / 150</span>
            </div>
            <div style={{ width: '100%', height: 7, background: 'rgba(68, 221, 255, 0.15)', borderRadius: 4, overflow: 'hidden' }}>
              <div style={{ width: `${(intVal / 150) * 100}%`, height: '100%', background: '#44ddff', boxShadow: '0 0 10px #44ddff' }} />
            </div>
          </div>

          {/* FOCUS */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: THEME.fontMono, fontSize: 13, color: '#ffd700', marginBottom: 4 }}>
              <span>NEURAL FOCUS [FOC]</span>
              <span>{focVal} / 150</span>
            </div>
            <div style={{ width: '100%', height: 7, background: 'rgba(255, 215, 0, 0.15)', borderRadius: 4, overflow: 'hidden' }}>
              <div style={{ width: `${(focVal / 150) * 100}%`, height: '100%', background: '#ffd700', boxShadow: '0 0 10px #ffd700' }} />
            </div>
          </div>
        </div>

        {/* Bottom Operational Mode Banner */}
        <div
          style={{
            marginTop: 8,
            padding: '12px 16px',
            backgroundColor: 'rgba(157, 51, 255, 0.15)',
            border: '1px solid rgba(157, 51, 255, 0.4)',
            borderRadius: 6,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span style={{ fontFamily: THEME.fontHead, fontSize: 12, letterSpacing: 2, color: THEME.purple }}>
            OPERATIONAL STATE:
          </span>
          <span
            style={{
              fontFamily: THEME.fontHead,
              fontSize: 13,
              letterSpacing: 2,
              color: '#ffd700',
              fontWeight: 'bold',
              textShadow: THEME.goldGlow,
            }}
          >
            ⚡ HYPER-FOCUS OVERDRIVE
          </span>
        </div>
      </div>
    </div>
  );
};
