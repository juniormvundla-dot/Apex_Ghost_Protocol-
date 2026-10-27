import React from 'react';
import { useCurrentFrame } from 'remotion';
import { THEME } from '../theme';

export const Atmosphere: React.FC = () => {
  const frame = useCurrentFrame();

  // Subtle floating particles
  const particles = Array.from({ length: 28 }).map((_, i) => {
    const seed = (i * 9301 + 49297) % 233280;
    const x = (seed % 1920);
    const initialY = (seed * 7) % 1080;
    const speed = 0.5 + ((seed % 10) / 10) * 1.5;
    const y = (initialY - frame * speed + 1080 * 2) % 1080;
    const size = 1 + (seed % 4);
    const opacity = 0.2 + ((Math.sin(frame * 0.05 + i) + 1) / 2) * 0.5;

    return { x, y, size, opacity };
  });

  const gridOffset = (frame * 0.6) % 60;

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        backgroundColor: THEME.bg0,
        overflow: 'hidden',
        pointerEvents: 'none',
      }}
    >
      {/* Deep Cybernetic Radial Vignette */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(circle at 50% 50%, rgba(157, 51, 255, 0.12) 0%, rgba(7, 0, 16, 0.95) 80%)',
          zIndex: 1,
        }}
      />

      {/* Cyber Grid Lines */}
      <svg
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          opacity: 0.12,
          zIndex: 1,
        }}
      >
        <defs>
          <pattern
            id="cyber-grid"
            width="60"
            height="60"
            patternUnits="userSpaceOnUse"
            patternTransform={`translate(0, ${gridOffset})`}
          >
            <path
              d="M 60 0 L 0 0 0 60"
              fill="none"
              stroke="#00e5ff"
              strokeWidth="0.8"
            />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#cyber-grid)" />
      </svg>

      {/* Ambient Drifting Particles */}
      {particles.map((p, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: p.x,
            top: p.y,
            width: p.size,
            height: p.size,
            borderRadius: '50%',
            backgroundColor: i % 2 === 0 ? THEME.cyan : THEME.purple,
            boxShadow: i % 2 === 0 ? THEME.cyanGlow : THEME.purpleGlow,
            opacity: p.opacity,
            zIndex: 2,
          }}
        />
      ))}

      {/* Diegetic Scanlines */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(0, 229, 255, 0.02) 3px, rgba(0, 229, 255, 0.02) 6px)',
          zIndex: 5,
        }}
      />
    </div>
  );
};
