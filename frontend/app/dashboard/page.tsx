'use client';

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus,
  BarChart2,
  FileText,
  Megaphone,
  ShoppingBag,
  TrendingUp,
  CheckCircle2,
  Clock,
  Layers,
  Activity,
  ChevronRight,
  Wifi,
} from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import ChatWindow from '@/components/chat/ChatWindow';
import AgentCard from '@/components/agents/AgentCard';
import { AGENTS, MOCK_PROJECTS, NETWORK_STATS } from '@/lib/data';

/* ─────────────────────────── helpers ─────────────────────────── */

function statusBadge(status: string) {
  const map: Record<string, { label: string; cls: string }> = {
    active: { label: 'Actif', cls: 'text-status-active bg-status-active/10 border-status-active/20' },
    planning: { label: 'Planification', cls: 'text-status-thinking bg-status-thinking/10 border-status-thinking/20' },
    review: { label: 'Révision', cls: 'text-accent-purple-light bg-accent-purple/10 border-accent-purple/20' },
    completed: { label: 'Terminé', cls: 'text-text-3 bg-white/5 border-white/8' },
    pending: { label: 'En attente', cls: 'text-text-3 bg-white/5 border-white/8' },
  };
  const item = map[status] ?? map.pending;
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs border font-mono ${item.cls}`}>
      {item.label}
    </span>
  );
}

/* ─────────────────────────── Left panel ─────────────────────────── */

const QUICK_ACTIONS = [
  { label: 'Lancer un projet', icon: Plus, color: '#7C3AED' },
  { label: 'Analyse marché', icon: BarChart2, color: '#60A5FA' },
  { label: 'Créer contenu', icon: FileText, color: '#F87171' },
  { label: 'Campagne Ads', icon: Megaphone, color: '#FB923C' },
  { label: 'Boutique en ligne', icon: ShoppingBag, color: '#4ADE80' },
  { label: 'Rapport financier', icon: TrendingUp, color: '#FCD34D' },
];

function ActiveMissionCard() {
  const project = MOCK_PROJECTS.find((p) => p.status === 'active') ?? MOCK_PROJECTS[0];
  const activeMission = project.missions.find((m) => m.status === 'active');
  const missionAgents = AGENTS.filter((a) => project.agents.includes(a.id)).slice(0, 4);

  return (
    <div className="rounded-2xl bg-bg-3 border border-white/5 p-4 mb-4">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 mb-1">
            <span className="w-2 h-2 rounded-full bg-status-active status-active flex-shrink-0" />
            <span className="text-xs text-status-active font-mono uppercase tracking-wider">Mission active</span>
          </div>
          <h3 className="text-sm font-semibold text-text-1 leading-snug line-clamp-2">
            {project.name}
          </h3>
        </div>
        <span className="ml-2 text-xs font-bold text-text-1 font-mono flex-shrink-0">
          {project.progress}%
        </span>
      </div>

      {/* Progress bar */}
      <div className="h-1.5 rounded-full bg-bg-4 mb-3 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${project.progress}%` }}
          transition={{ duration: 1.2, ease: 'easeOut', delay: 0.3 }}
          className="h-full rounded-full"
          style={{ background: 'linear-gradient(90deg, #7C3AED, #9D5CF6)' }}
        />
      </div>

      {/* Active sub-mission */}
      {activeMission && (
        <div className="flex items-center gap-2 mb-3 px-2.5 py-1.5 rounded-lg bg-accent-purple/8 border border-accent-purple/15">
          <Activity size={11} className="text-accent-purple-light flex-shrink-0" />
          <span className="text-xs text-accent-purple-light truncate">{activeMission.title}</span>
          <span className="ml-auto text-xs font-mono text-text-3 flex-shrink-0">
            {activeMission.progress}%
          </span>
        </div>
      )}

      {/* Agents */}
      <div className="flex items-center gap-1.5">
        <div className="flex -space-x-2">
          {missionAgents.map((agent) => (
            <div
              key={agent.id}
              title={agent.name}
              className="w-6 h-6 rounded-full border-2 border-bg-3 flex items-center justify-center text-xs flex-shrink-0"
              style={{
                background: `linear-gradient(135deg, ${agent.gradient[0]}, ${agent.gradient[1]})`,
              }}
            >
              <span style={{ fontSize: 10 }}>{agent.emoji}</span>
            </div>
          ))}
        </div>
        <span className="text-xs text-text-3 ml-1">
          {project.agents.length} agent{project.agents.length > 1 ? 's' : ''} mobilisé{project.agents.length > 1 ? 's' : ''}
        </span>
      </div>
    </div>
  );
}

function LeftPanel() {
  return (
    <aside className="w-80 flex-shrink-0 flex flex-col border-r border-white/5 bg-bg-1 overflow-y-auto">
      {/* Header */}
      <div className="p-5 border-b border-white/5">
        <h1 className="font-display font-bold text-lg text-text-1 mb-0.5">Tableau de bord</h1>
        <p className="text-xs text-text-3 font-mono">Angeleck · 11 agents actifs</p>
      </div>

      <div className="flex-1 p-4 flex flex-col gap-5 overflow-y-auto" style={{ scrollbarWidth: 'none' }}>
        {/* Active mission */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-text-3 font-semibold uppercase tracking-wider">Mission en cours</span>
          </div>
          <ActiveMissionCard />
        </div>

        {/* Quick actions */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs text-text-3 font-semibold uppercase tracking-wider">Actions rapides</span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {QUICK_ACTIONS.map(({ label, icon: Icon, color }) => (
              <motion.button
                key={label}
                whileHover={{ scale: 1.03, y: -1 }}
                whileTap={{ scale: 0.97 }}
                className="flex flex-col items-start gap-1.5 p-3 rounded-xl bg-bg-3 border border-white/5 hover:border-white/10 hover:bg-bg-4 transition-all text-left group"
              >
                <div
                  className="w-7 h-7 rounded-lg flex items-center justify-center"
                  style={{ background: `${color}18`, color }}
                >
                  <Icon size={13} />
                </div>
                <span className="text-xs text-text-2 leading-tight group-hover:text-text-1 transition-colors">
                  {label}
                </span>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Recent projects */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs text-text-3 font-semibold uppercase tracking-wider">Projets récents</span>
            <button className="text-xs text-accent-purple-light hover:text-accent-purple transition-colors flex items-center gap-0.5">
              Voir tout <ChevronRight size={11} />
            </button>
          </div>
          <div className="flex flex-col gap-2">
            {MOCK_PROJECTS.slice(0, 3).map((project) => (
              <motion.div
                key={project.id}
                whileHover={{ x: 2 }}
                className="p-3 rounded-xl bg-bg-3 border border-white/5 hover:border-white/10 transition-all cursor-pointer"
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <span className="text-xs font-semibold text-text-1 leading-snug line-clamp-2 flex-1">
                    {project.name}
                  </span>
                  {statusBadge(project.status)}
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-1 rounded-full bg-bg-4 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-accent-purple to-accent-purple-light"
                      style={{ width: `${project.progress}%` }}
                    />
                  </div>
                  <span className="text-xs font-mono text-text-3 flex-shrink-0">
                    {project.progress}%
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </aside>
  );
}

/* ─────────────────────────── Right panel ─────────────────────────── */

const HEALTH_METRICS = [
  { label: 'CPU', value: 34, color: '#10B981' },
  { label: 'Mémoire', value: 61, color: '#7C3AED' },
  { label: 'Réseau', value: 88, color: '#60A5FA' },
  { label: 'Latence', value: 22, color: '#C9A84C' },
];

function NetworkHealth() {
  return (
    <div className="rounded-2xl bg-bg-3 border border-white/5 p-4">
      <div className="flex items-center gap-2 mb-4">
        <Wifi size={13} className="text-status-active" />
        <span className="text-xs font-semibold text-text-2 uppercase tracking-wider">Santé réseau</span>
        <span className="ml-auto text-xs font-mono text-status-active">{NETWORK_STATS.uptime}</span>
      </div>
      <div className="flex flex-col gap-3">
        {HEALTH_METRICS.map(({ label, value, color }) => (
          <div key={label}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-text-3">{label}</span>
              <span className="text-xs font-mono" style={{ color }}>
                {value}%
              </span>
            </div>
            <div className="h-1 rounded-full bg-bg-4 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                transition={{ duration: 1, ease: 'easeOut', delay: 0.5 }}
                className="h-full rounded-full"
                style={{ background: color }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Network stats */}
      <div className="mt-4 pt-4 border-t border-white/5 grid grid-cols-2 gap-3">
        <div className="text-center">
          <div className="text-lg font-bold text-text-1 font-mono">{NETWORK_STATS.totalMissions.toLocaleString()}</div>
          <div className="text-xs text-text-3">missions</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-text-1 font-mono">{NETWORK_STATS.successRate}%</div>
          <div className="text-xs text-text-3">succès</div>
        </div>
      </div>
    </div>
  );
}

interface RightPanelProps {
  activeAgentIds: string[];
}

function RightPanel({ activeAgentIds }: RightPanelProps) {
  const activeCount = activeAgentIds.length + AGENTS.filter((a) => a.status === 'active').length;

  return (
    <aside className="w-72 flex-shrink-0 flex flex-col border-l border-white/5 bg-bg-1 overflow-y-auto">
      {/* Header */}
      <div className="p-5 border-b border-white/5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-text-1 mb-0.5">Agents mobilisés</h2>
            <p className="text-xs text-text-3 font-mono">{AGENTS.length} agents · {activeCount} actifs</p>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-status-active/10 border border-status-active/20">
            <span className="w-1.5 h-1.5 rounded-full bg-status-active status-active" />
            <span className="text-xs text-status-active font-mono">{activeCount}</span>
          </div>
        </div>
      </div>

      {/* Agent list */}
      <div className="flex-1 p-4 flex flex-col gap-2 overflow-y-auto" style={{ scrollbarWidth: 'none' }}>
        <AnimatePresence>
          {AGENTS.map((agent, i) => {
            const isActive = activeAgentIds.includes(agent.name) || agent.status === 'active';
            return (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, x: 16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.04, duration: 0.4 }}
                layout
              >
                <AgentCard
                  agent={isActive ? { ...agent, status: 'active' } : agent}
                  compact
                  selected={activeAgentIds.includes(agent.name)}
                />
              </motion.div>
            );
          })}
        </AnimatePresence>

        {/* Network health */}
        <div className="mt-3">
          <NetworkHealth />
        </div>
      </div>
    </aside>
  );
}

/* ─────────────────────────── Center ─────────────────────────── */

function ChatHeader() {
  return (
    <div className="flex items-center gap-3 px-6 py-4 border-b border-white/5 flex-shrink-0">
      <div
        className="w-9 h-9 rounded-xl flex items-center justify-center text-lg shadow-purple-sm"
        style={{ background: 'linear-gradient(135deg, #8B5CF6, #4C1D95)' }}
      >
        🧠
      </div>
      <div>
        <div className="font-semibold text-text-1 text-sm">Raphaël</div>
        <div className="flex items-center gap-1.5 text-xs text-text-3">
          <span className="w-1.5 h-1.5 rounded-full bg-status-active status-active" />
          <span className="font-mono">Orchestrateur · En ligne</span>
        </div>
      </div>

      <div className="ml-auto flex items-center gap-2">
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-bg-3 border border-white/5">
          <Layers size={11} className="text-accent-purple-light" />
          <span className="text-xs font-mono text-text-2">{NETWORK_STATS.totalAgents} agents</span>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-bg-3 border border-white/5">
          <CheckCircle2 size={11} className="text-status-active" />
          <span className="text-xs font-mono text-text-2">{NETWORK_STATS.successRate}%</span>
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────── Page ─────────────────────────── */

export default function DashboardPage() {
  const [activeAgentIds, setActiveAgentIds] = useState<string[]>([]);

  const handleAgentsChange = useCallback((agents: string[]) => {
    setActiveAgentIds(agents);
  }, []);

  return (
    <AppLayout>
      <div className="flex h-full overflow-hidden">
        {/* Left panel */}
        <LeftPanel />

        {/* Center — chat */}
        <main className="flex-1 flex flex-col min-w-0 bg-bg-0">
          <ChatHeader />
          <div className="flex-1 overflow-hidden">
            <ChatWindow onAgentsChange={handleAgentsChange} />
          </div>
        </main>

        {/* Right panel */}
        <RightPanel activeAgentIds={activeAgentIds} />
      </div>
    </AppLayout>
  );
}
