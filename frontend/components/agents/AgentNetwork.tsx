'use client';
import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { AGENTS } from '@/lib/data';
import type { Agent } from '@/lib/types';
import AgentAvatarSVG from './AgentAvatarSVG';

interface Props {
  activeAgents?: string[];
  onSelect?: (agent: Agent) => void;
  selected?: Agent | null;
}

export default function AgentNetwork({ activeAgents = [], onSelect, selected }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const frameRef = useRef<number>(0);
  const timeRef = useRef(0);

  const raphael = AGENTS[0];
  const others = AGENTS.slice(1);

  // Positions in a circle
  const positions = others.map((_, i) => {
    const angle = (i / others.length) * Math.PI * 2 - Math.PI / 2;
    return { x: Math.cos(angle), y: Math.sin(angle) };
  });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d')!;

    const draw = () => {
      const { width: W, height: H } = canvas;
      ctx.clearRect(0, 0, W, H);
      timeRef.current += 0.008;
      const t = timeRef.current;
      const cx = W / 2, cy = H / 2;
      const R = Math.min(W, H) * 0.36;

      // Draw lines from center to each agent
      others.forEach((agent, i) => {
        const px = cx + positions[i].x * R;
        const py = cy + positions[i].y * R;
        const isActive = activeAgents.includes(agent.name);

        const grad = ctx.createLinearGradient(cx, cy, px, py);
        grad.addColorStop(0, `${raphael.color}${isActive ? '88' : '22'}`);
        grad.addColorStop(1, `${agent.color}${isActive ? '66' : '11'}`);

        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(px, py);
        ctx.strokeStyle = grad;
        ctx.lineWidth = isActive ? 2 : 1;
        ctx.setLineDash(isActive ? [] : [4, 8]);
        ctx.stroke();
        ctx.setLineDash([]);

        // Pulse dot traveling the line when active
        if (isActive) {
          const progress = (Math.sin(t * 2 + i) + 1) / 2;
          const dotX = cx + (px - cx) * progress;
          const dotY = cy + (py - cy) * progress;
          ctx.beginPath();
          ctx.arc(dotX, dotY, 3, 0, Math.PI * 2);
          ctx.fillStyle = agent.color + 'cc';
          ctx.fill();
        }
      });

      frameRef.current = requestAnimationFrame(draw);
    };

    const resize = () => {
      const rect = canvas.parentElement!.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = rect.height;
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(canvas.parentElement!);
    frameRef.current = requestAnimationFrame(draw);

    return () => { cancelAnimationFrame(frameRef.current); ro.disconnect(); };
  }, [activeAgents]);

  return (
    <div className="relative w-full h-full min-h-[500px]">
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full pointer-events-none" />

      {/* Center: Raphaël */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-10">
        <motion.div
          animate={{ scale: [1, 1.04, 1] }}
          transition={{ duration: 3, repeat: Infinity }}
          onClick={() => onSelect?.(raphael)}
          className={`cursor-pointer flex flex-col items-center gap-2 ${selected?.id === 'raphael' ? 'opacity-100' : 'opacity-95'}`}
        >
          <div className="relative w-20 h-20">
            <AgentAvatarSVG agent={raphael} size={80} showBadge={false} />
            <div className="absolute inset-0 rounded-full border-2 border-accent-purple/40 animate-pulse" />
          </div>
          <div className="text-center bg-bg-2/85 backdrop-blur-sm px-3 py-1 rounded-full border border-line/12 shadow-soft">
            <div className="text-sm font-bold text-text-1">{raphael.name}</div>
            <div className="text-xs text-text-3">Orchestrateur</div>
          </div>
        </motion.div>
      </div>

      {/* Orbit agents */}
      {others.map((agent, i) => {
        const angle = (i / others.length) * Math.PI * 2 - Math.PI / 2;
        const rPct = 36;
        const left = `${50 + Math.cos(angle) * rPct}%`;
        const top = `${50 + Math.sin(angle) * rPct}%`;
        const isActive = activeAgents.includes(agent.name);
        const isSelected = selected?.id === agent.id;

        return (
          <motion.div
            key={agent.id}
            style={{ position: 'absolute', left, top }}
            className="-translate-x-1/2 -translate-y-1/2 z-10"
            animate={{ y: [0, -4, 0] }}
            transition={{ duration: 3 + i * 0.3, repeat: Infinity, ease: 'easeInOut' }}
          >
            <motion.div
              whileHover={{ scale: 1.12 }}
              onClick={() => onSelect?.(agent)}
              className="cursor-pointer flex flex-col items-center gap-1.5"
            >
              <div
                className="relative w-12 h-12 rounded-full transition-all"
                style={{
                  borderRadius: '50%',
                  boxShadow: isActive
                    ? `0 0 20px ${agent.color}80, 0 0 40px ${agent.color}40`
                    : `0 0 8px ${agent.color}30`,
                  opacity: isSelected ? 1 : 0.9,
                }}
              >
                <AgentAvatarSVG agent={agent} size={48} showBadge={false} />
                {isActive && (
                  <div className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-status-active border border-bg-1 status-active" />
                )}
              </div>
              <div className="text-center">
                <div className="text-xs font-semibold text-text-1 leading-tight">{agent.name}</div>
                <div className="text-xs text-text-3 leading-tight hidden group-hover:block">{agent.role.split(' ')[0]}</div>
              </div>
            </motion.div>
          </motion.div>
        );
      })}
    </div>
  );
}
