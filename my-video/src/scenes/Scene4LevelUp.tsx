import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { THEME } from '../theme';

export const Scene4LevelUp: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Shockwave expansion
  const shockwaveScale = interpolate(frame, [0, 40], [0.2, 3], { extrapolateRight: 'clamp' });
  const shockwaveOpacity = interpolate(frame, [0, 35], [0.8, 0], { extrapolateRight: 'clamp' });

  // Banner spring
  const bannerScale = spring({ frame: frame - 10, fps, config: { damping: 12, stiffness: 120 } });
  const bannerOpacity = interpolate(frame, [10, 25], [0, 1], { extrapolateRight: 'clamp' });

  // Title card delay
  const titleY = spring({ frame: frame - 60, fps, config: { damping: 14 } });
  const titleOpacity = interpolate(frame, [60, 80], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Golden Expanding Shockwave Ring */}
      <div
        style={{
          position: 'absolute',
          width: 600,
          height: 600,
          borderRadius: '50%',
          border: '4px solid #ffd700',
          boxShadow: THEME.goldGlow,
          transform: `scale(${shockwaveScale})`,
          opacity: shockwaveOpacity,
          pointerEvents: 'none',
        }}
      />

      {/* Main Level-Up Announcement Box */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
          transform: `scale(${bannerScale})`,
          opacity: bannerOpacity,
          marginBottom: 40,
        }}
      >
        <div
          style={{
            fontFamily: THEME.fontHead,
            fontSize: 22,
            letterSpacing: 8,
            color: THEME.cyan,
            textShadow: THEME.cyanGlow,
            marginBottom: 10,
          }}
        >
          [SYSTEM ALERT]
        </div>

        <div
          style={{
            fontFamily: THEME.fontHead,
            fontSize: 54,
            fontWeight: 900,
            color: '#ffd700',
            letterSpacing: 4,
            textShadow: '0 0 25px rgba(255, 215, 0, 0.8), 0 0 50px rgba(255, 170, 0, 0.5)',
            marginBottom: 12,
          }}
        >
          ★ LEVEL UP: RANK AWAKENED ★
        </div>

        <div
          style={{
            fontFamily: THEME.fontMono,
            fontSize: 18,
            color: '#ffffff',
            letterSpacing: 3,
            backgroundColor: 'rgba(255, 215, 0, 0.15)',
            border: '1px solid #ffd700',
            padding: '6px 28px',
            borderRadius: 30,
            boxShadow: '0 0 20px rgba(255, 215, 0, 0.3)',
          }}
        >
          SHADOW MONARCH DOMAIN UNLOCKED
        </div>
      </div>

      {/* Final Branding & Call to Action */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
          opacity: titleOpacity,
          transform: `translateY(${interpolate(titleY, [0, 1], [40, 0])}px)`,
        }}
      >
        <div
          style={{
            fontFamily: THEME.fontTitle,
            fontSize: 42,
            color: '#ffffff',
            letterSpacing: 6,
            textShadow: '0 0 30px rgba(157, 51, 255, 0.8)',
            marginBottom: 8,
          }}
        >
          APEX GHOST PROTOCOL
        </div>

        <div
          style={{
            fontFamily: THEME.fontHead,
            fontSize: 16,
            color: THEME.cyan,
            letterSpacing: 5,
            textShadow: THEME.cyanGlow,
          }}
        >
          AIR-GAPPED · AUTONOMOUS · ZERO EXCUSES
        </div>
      </div>
    </div>
  );
};
