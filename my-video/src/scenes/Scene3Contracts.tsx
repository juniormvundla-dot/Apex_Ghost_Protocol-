import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { THEME } from '../theme';

export const Scene3Contracts: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Slide-in animations for cards
  const card1X = spring({ frame: frame - 5, fps, config: { damping: 14 } });
  const card2X = spring({ frame: frame - 25, fps, config: { damping: 14 } });
  const card3X = spring({ frame: frame - 45, fps, config: { damping: 14 } });

  // Floating toast trigger
  const toastY = spring({ frame: frame - 65, fps, config: { damping: 12 } });
  const toastOpacity = interpolate(frame, [65, 80], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        padding: '0 120px',
        boxSizing: 'border-box',
        position: 'relative',
      }}
    >
      {/* Section Title */}
      <div
        style={{
          fontFamily: THEME.fontHead,
          fontSize: 22,
          color: THEME.cyan,
          letterSpacing: 4,
          marginBottom: 30,
          textShadow: THEME.cyanGlow,
          display: 'flex',
          alignItems: 'center',
          gap: 12,
        }}
      >
        <span>⚔</span> DAILY PROTOCOLS & AUTONOMOUS ENFORCEMENT
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24 }}>
        {/* CARD 1: THE IRON GAUNTLET QUEST */}
        <div
          style={{
            background: 'rgba(13, 0, 24, 0.85)',
            border: '1px solid rgba(0, 229, 255, 0.4)',
            borderRadius: 8,
            padding: '24px 20px',
            boxShadow: '0 0 25px rgba(0, 229, 255, 0.15)',
            transform: `translateY(${interpolate(card1X, [0, 1], [60, 0])}px)`,
            opacity: card1X,
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
            <span style={{ fontFamily: THEME.fontHead, fontSize: 13, color: THEME.cyan, letterSpacing: 1.5 }}>
              CONTRACT 01
            </span>
            <span style={{ fontFamily: THEME.fontMono, fontSize: 11, color: THEME.green, border: '1px solid #00ff88', padding: '1px 6px', borderRadius: 4 }}>
              CLEARED
            </span>
          </div>
          <div style={{ fontFamily: THEME.fontHead, fontSize: 18, color: '#ffffff', marginBottom: 10 }}>
            THE IRON GAUNTLET
          </div>
          <div style={{ fontFamily: THEME.fontMono, fontSize: 13, color: 'rgba(232, 200, 255, 0.8)', lineHeight: 1.5 }}>
            100 Push-ups · 100 Squats<br />
            10km Run · Zero Excuses
          </div>
          <div style={{ marginTop: 20, fontFamily: THEME.fontMono, fontSize: 14, color: THEME.gold }}>
            REWARD: +500 XP [STRENGTH +3]
          </div>
        </div>

        {/* CARD 2: FOCUS GUARD WINDOW */}
        <div
          style={{
            background: 'rgba(13, 0, 24, 0.85)',
            border: '1px solid rgba(157, 51, 255, 0.5)',
            borderRadius: 8,
            padding: '24px 20px',
            boxShadow: '0 0 25px rgba(157, 51, 255, 0.2)',
            transform: `translateY(${interpolate(card2X, [0, 1], [60, 0])}px)`,
            opacity: card2X,
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
            <span style={{ fontFamily: THEME.fontHead, fontSize: 13, color: THEME.purple, letterSpacing: 1.5 }}>
              SHADOW ENFORCER
            </span>
            <span style={{ fontFamily: THEME.fontMono, fontSize: 11, color: THEME.cyan, border: '1px solid #00e5ff', padding: '1px 6px', borderRadius: 4 }}>
              ENGAGED
            </span>
          </div>
          <div style={{ fontFamily: THEME.fontHead, fontSize: 18, color: '#ffffff', marginBottom: 10 }}>
            FOCUS GUARD PROTOCOL
          </div>
          <div style={{ fontFamily: THEME.fontMono, fontSize: 13, color: 'rgba(232, 200, 255, 0.8)', lineHeight: 1.5 }}>
            Hostile Tab Lockout Active<br />
            Deep Cognitive State Guarded
          </div>
          <div style={{ marginTop: 20, fontFamily: THEME.fontMono, fontSize: 14, color: THEME.cyan }}>
            WINDOW: 01:29:42 REMAINING
          </div>
        </div>

        {/* CARD 3: CAPITAL REACTOR */}
        <div
          style={{
            background: 'rgba(13, 0, 24, 0.85)',
            border: '1px solid rgba(255, 215, 0, 0.45)',
            borderRadius: 8,
            padding: '24px 20px',
            boxShadow: '0 0 25px rgba(255, 215, 0, 0.15)',
            transform: `translateY(${interpolate(card3X, [0, 1], [60, 0])}px)`,
            opacity: card3X,
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
            <span style={{ fontFamily: THEME.fontHead, fontSize: 13, color: THEME.gold, letterSpacing: 1.5 }}>
              TREASURY AI
            </span>
            <span style={{ fontFamily: THEME.fontMono, fontSize: 11, color: THEME.gold, border: '1px solid #ffd700', padding: '1px 6px', borderRadius: 4 }}>
              ONLINE
            </span>
          </div>
          <div style={{ fontFamily: THEME.fontHead, fontSize: 18, color: '#ffffff', marginBottom: 10 }}>
            CAPITAL REACTOR
          </div>
          <div style={{ fontFamily: THEME.fontMono, fontSize: 13, color: 'rgba(232, 200, 255, 0.8)', lineHeight: 1.5 }}>
            100% Air-Gapped Local CFO<br />
            Zero Cloud Financial Exposure
          </div>
          <div style={{ marginTop: 20, fontFamily: THEME.fontMono, fontSize: 14, color: THEME.green }}>
            NET ARBITRAGE: +$14,250 / MO
          </div>
        </div>
      </div>

      {/* FLOATING LIVE XP TOAST NOTIFICATION */}
      <div
        style={{
          position: 'absolute',
          top: 70,
          right: 120,
          background: 'rgba(10, 0, 20, 0.95)',
          borderLeft: '4px solid #ffd700',
          borderTop: '1px solid rgba(255, 215, 0, 0.4)',
          borderRight: '1px solid rgba(255, 215, 0, 0.4)',
          borderBottom: '1px solid rgba(255, 215, 0, 0.4)',
          borderRadius: 6,
          padding: '12px 20px',
          boxShadow: THEME.goldGlow,
          transform: `translateX(${interpolate(toastY, [0, 1], [100, 0])}px)`,
          opacity: toastOpacity,
          display: 'flex',
          alignItems: 'center',
          gap: 14,
        }}
      >
        <span style={{ fontSize: 24 }}>⚡</span>
        <div>
          <div style={{ fontFamily: THEME.fontHead, fontSize: 12, color: THEME.gold, letterSpacing: 2 }}>
            [XP GAINED]
          </div>
          <div style={{ fontFamily: THEME.fontMono, fontSize: 14, color: '#ffffff' }}>
            +500 XP · ASCENT PROGRESS: 94.2%
          </div>
        </div>
      </div>
    </div>
  );
};
