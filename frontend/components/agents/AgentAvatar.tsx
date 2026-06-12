'use client';
import { motion } from 'framer-motion';
import type { Agent } from '@/lib/types';

interface Props {
  agent: Agent;
  size?: number;
  animate?: boolean;
  showGlow?: boolean;
}

export default function AgentAvatar({ agent, size = 64, animate = true, showGlow = true }: Props) {
  const Wrapper = animate ? motion.div : 'div';
  const wrapperProps = animate
    ? { animate: { y: [0, -6, 0] }, transition: { duration: 3 + Math.random() * 2, repeat: Infinity, ease: 'easeInOut' } }
    : {};

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      {/* Glow */}
      {showGlow && (
        <div
          className="absolute inset-0 rounded-full blur-xl opacity-40"
          style={{ background: `radial-gradient(circle, ${agent.color}66, transparent)` }}
        />
      )}
      {/* Avatar circle */}
      <Wrapper
        {...wrapperProps}
        className="relative flex items-center justify-center rounded-full z-10"
        style={{
          width: size,
          height: size,
          background: `linear-gradient(135deg, ${agent.gradient[0]}, ${agent.gradient[1]})`,
          boxShadow: `0 0 ${size * 0.4}px ${agent.color}44`,
        }}
      >
        <span style={{ fontSize: size * 0.42 }}>{agent.emoji}</span>

        {/* Status indicator */}
        <div
          className="absolute bottom-0.5 right-0.5 rounded-full border-2"
          style={{
            width: Math.max(8, size * 0.18),
            height: Math.max(8, size * 0.18),
            background: agent.status === 'active' ? '#10B981' : agent.status === 'thinking' ? '#F59E0B' : '#4A5568',
            borderColor: '#09091A',
          }}
        />
      </Wrapper>
    </div>
  );
}
