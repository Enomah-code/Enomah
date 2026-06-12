'use client';
import { motion } from 'framer-motion';
import { CheckCircle, Zap, Star } from 'lucide-react';
import type { Agent } from '@/lib/types';
import AgentAvatar from './AgentAvatar';

interface Props {
  agent: Agent;
  onClick?: () => void;
  selected?: boolean;
  compact?: boolean;
}

export default function AgentCard({ agent, onClick, selected, compact }: Props) {
  const statusColors = {
    active: 'text-status-active',
    thinking: 'text-status-thinking',
    idle: 'text-text-3',
    offline: 'text-red-500',
  };

  if (compact) {
    return (
      <motion.div
        whileHover={{ scale: 1.02, y: -2 }}
        whileTap={{ scale: 0.98 }}
        onClick={onClick}
        className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
          selected
            ? 'bg-accent-purple/10 border-accent-purple/30'
            : 'bg-bg-3 border-white/5 hover:border-white/10'
        }`}
      >
        <AgentAvatar agent={agent} size={36} showGlow={false} />
        <div className="min-w-0 flex-1">
          <div className="text-sm font-semibold text-text-1 truncate">{agent.name}</div>
          <div className="text-xs text-text-3 truncate">{agent.role}</div>
        </div>
        <div className={`text-xs font-mono ${statusColors[agent.status]}`}>●</div>
      </motion.div>
    );
  }

  return (
    <motion.div
      whileHover={{ y: -6 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`relative rounded-2xl p-5 border cursor-pointer transition-all overflow-hidden group ${
        selected
          ? 'bg-accent-purple/10 border-accent-purple/40 shadow-purple'
          : 'bg-bg-2 border-white/5 hover:border-white/12 hover:bg-bg-3'
      }`}
    >
      {/* Background gradient on hover */}
      <div
        className="absolute inset-0 opacity-0 group-hover:opacity-5 transition-opacity"
        style={{ background: `radial-gradient(circle at 50% 0%, ${agent.color}, transparent)` }}
      />

      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <AgentAvatar agent={agent} size={56} />
        <div className="flex flex-col items-end gap-1">
          <div className={`flex items-center gap-1 text-xs ${statusColors[agent.status]}`}>
            <span className="w-1.5 h-1.5 rounded-full bg-current" />
            <span className="capitalize">{agent.status}</span>
          </div>
          <div className="text-xs text-text-3 font-mono">{agent.tasksCompleted} tâches</div>
        </div>
      </div>

      {/* Info */}
      <div className="mb-3">
        <div className="font-display font-bold text-text-1 text-lg leading-tight">{agent.name}</div>
        <div className="text-xs text-text-3 font-mono mt-0.5 uppercase tracking-wider">{agent.role}</div>
      </div>

      <p className="text-xs text-text-2 leading-relaxed mb-3 line-clamp-2">{agent.description}</p>

      {/* Skills */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        {agent.skills.slice(0, 3).map(s => (
          <span key={s} className="px-2 py-0.5 rounded-full text-xs bg-bg-3 text-text-3 border border-white/5">
            {s}
          </span>
        ))}
      </div>

      {/* Stats */}
      <div className="flex items-center justify-between pt-3 border-t border-white/5">
        <div className="flex items-center gap-1">
          <Star size={11} className="text-accent-gold" />
          <span className="text-xs text-text-2">{agent.successRate}% succès</span>
        </div>
        <div className="flex items-center gap-1">
          <Zap size={11} className="text-accent-purple-light" />
          <span className="text-xs text-text-2">Actif</span>
        </div>
      </div>
    </motion.div>
  );
}
