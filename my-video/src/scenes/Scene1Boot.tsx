import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { THEME } from '../theme';

export const Scene1Boot: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Spring entrance for hologram plate
  const plateScale = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 100 },
  });

  const plateOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Ticker typing effect
  const fullText = "SYSTEM NOTIFICATION: HUNTER AWAKENING INITIALIZED";
  const charsShown = Math.floor(
    interpolate(frame, [20, 60], [0, fullText.length], {
      extrapolateRight: 'clamp',
    })
  );

  // Status line fade-ins
  const line1Opacity = interpolate(frame, [50, 70], [0, 1], { extrapolateRight: 'clamp' });
  const line2Opacity = interpolate(frame, [70, 90], [0, 1], { extrapolateRight: 'clamp' });
  const line3Opacity = interpolate(frame, [90, 110], [0, 1], { extrapolateRight: 'clamp' });

  // Floating bob animation
  const floatY = Math.sin(frame * 0.08) * 8;

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transform: `translateY(${floatY}px)`,
      }}
    >
      {/* Authentic Sung Jin-woo System Hologram Window */}
      <div
        style={{
          width: 860,
          background: 'rgba(13, 0, 24, 0.78)',
          border: '1px solid rgba(0, 229, 255, 0.45)',
          borderRadius: 8,
          boxShadow: '0 0 35px rgba(0, 229, 255, 0.35), inset 0 0 30px rgba(0, 229, 255, 0.08)',
          backdropFilter: 'blur(16px)',
          padding: '28px 36px',
          opacity: plateOpacity,
          transform: `scale(${plateScale})`,
          position: 'relative',
        }}
      >
        {/* Hologram Bracket Rails */}
        <div
          style={{
            position: 'absolute',
            top: -2,
            left: '20%',
            right: '20%',
            height: 3,
            background: `linear-gradient(90deg, transparent, ${THEME.cyan}, transparent)`,
            boxShadow: THEME.cyanGlow,
          }}
        />
        <div
          style={{
            position: 'absolute',
            bottom: -2,
            left: '20%',
            right: '20%',
            height: 3,
            background: `linear-gradient(90deg, transparent, ${THEME.cyan}, transparent)`,
            boxShadow: THEME.cyanGlow,
          }}
        />

        {/* Top Header Bar */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid rgba(0, 229, 255, 0.25)',
            paddingBottom: 12,
            marginBottom: 20,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ color: THEME.cyan, fontSize: 20 }}>◈</span>
            <span
              style={{
                fontFamily: THEME.fontHead,
                fontSize: 14,
                letterSpacing: 3,
                color: THEME.cyan,
                textShadow: THEME.cyanGlow,
              }}
            >
              [SYSTEM] [OVERLORD PROTOCOL]
            </span>
          </div>
          <span
            style={{
              fontFamily: THEME.fontMono,
              fontSize: 12,
              color: 'rgba(0, 229, 255, 0.7)',
              letterSpacing: 2,
            }}
          >
            LOCAL AIR-GAPPED // VER 2.45
          </span>
        </div>

        {/* Primary Notification Text */}
        <div
          style={{
            fontFamily: THEME.fontHead,
            fontSize: 26,
            color: '#ffffff',
            letterSpacing: 2,
            marginBottom: 24,
            minHeight: 36,
            textShadow: '0 0 16px rgba(255, 255, 255, 0.6)',
          }}
        >
          {fullText.slice(0, charsShown)}
          <span
            style={{
              display: 'inline-block',
              width: 10,
              height: 24,
              backgroundColor: THEME.cyan,
              marginLeft: 8,
              opacity: (frame % 16 < 8) ? 1 : 0,
            }}
          />
        </div>

        {/* Diagnostic Telemetry Lines */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              fontFamily: THEME.fontMono,
              fontSize: 15,
              color: 'rgba(232, 200, 255, 0.9)',
              opacity: line1Opacity,
            }}
          >
            <span>› CANDIDATE IDENTIFICATION:</span>
            <span style={{ color: THEME.gold, fontWeight: 'bold' }}>HUNTER (APEX CLASS)</span>
          </div>

          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              fontFamily: THEME.fontMono,
              fontSize: 15,
              color: 'rgba(232, 200, 255, 0.9)',
              opacity: line2Opacity,
            }}
          >
            <span>› NEURAL TELEMETRY LINK:</span>
            <span style={{ color: THEME.green, fontWeight: 'bold' }}>SYNCHRONIZED (0.0ms LATENCY)</span>
          </div>

          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              fontFamily: THEME.fontMono,
              fontSize: 15,
              color: 'rgba(232, 200, 255, 0.9)',
              opacity: line3Opacity,
            }}
          >
            <span>› RESTRICTED AIR-GAP STATUS:</span>
            <span style={{ color: THEME.cyan, fontWeight: 'bold' }}>100% OFFLINE // ZERO CLOUD LEAK</span>
          </div>
        </div>

        {/* Bottom Accent */}
        <div
          style={{
            marginTop: 26,
            paddingTop: 14,
            borderTop: '1px solid rgba(157, 51, 255, 0.25)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span style={{ fontFamily: THEME.fontBody, fontSize: 13, color: '#9d33ff', letterSpacing: 2 }}>
            PRESS ANY KEY TO ACCEPT ASSIGNMENT
          </span>
          <span style={{ fontFamily: THEME.fontMono, fontSize: 13, color: THEME.cyan }}>
            HEX: 0x7F_AWAKEN
          </span>
        </div>
      </div>
    </div>
  );
};
