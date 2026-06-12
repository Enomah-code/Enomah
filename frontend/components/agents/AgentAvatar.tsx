'use client';
import { motion } from 'framer-motion';
import type { Agent } from '@/lib/types';
import AgentAvatarSVG from './AgentAvatarSVG';

interface Props {
  agent: Agent;
  size?: number;
  animate?: boolean;
  showGlow?: boolean;
  showBadge?: boolean;
}

export default function AgentAvatar({ agent, size = 64, animate = true, showGlow = true, showBadge = true }: Props) {
  const Wrapper = animate ? motion.div : 'div';
  const wrapperProps = animate
    ? { animate: { y: [0, -6, 0] }, transition: { duration: 3 + Math.random() * 2, repeat: Infinity, ease: 'easeInOut' } }
    : {};

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      {showGlow && (
        <div
          className="absolute rounded-full blur-xl opacity-30"
          style={{ inset: '8%', background: `radial-gradient(circle, ${agent.color}55, transparent 70%)` }}
        />
      )}
      <Wrapper {...wrapperProps} className="relative z-10" style={{ width: size, height: size }}>
        <AgentAvatarSVG agent={agent} size={size} showBadge={showBadge} />
      </Wrapper>
    </div>
  );
}
