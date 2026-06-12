'use client';
import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, Zap, Star, MessageCircle, Cpu, Target, Shield,
  ChevronRight, Activity, Users, CheckCircle, Clock,
} from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import AgentNetwork from '@/components/agents/AgentNetwork';
import AgentCard from '@/components/agents/AgentCard';
import AgentAvatar from '@/components/agents/AgentAvatar';
import { AGENTS } from '@/lib/data';
import type { Agent } from '@/lib/types';

type FilterType = 'Tous' | 'Actifs' | 'Business' | 'Tech' | 'Créatif';

const FILTER_MAP: Record<FilterType, (a: Agent) => boolean> = {
  Tous: () => true,
  Actifs: (a) => a.status === 'active',
  Business: (a) => ['sofia', 'adam', 'lucas'].includes(a.id),
  Tech: (a) => ['gabriel', 'emma', 'lea'].includes(a.id),
  Créatif: (a) => ['elena', 'noah', 'nathan', 'maya'].includes(a.id),
};

export default function AgentsPage() {
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [filter, setFilter] = useState<FilterType>('Tous');
  const [search, setSearch] = useState('');

  const filteredAgents = useMemo(() => {
    return AGENTS.filter(
      (a) =>
        FILTER_MAP[filter](a) &&
        (search === '' ||
          a.name.toLowerCase().includes(search.toLowerCase()) ||
          a.role.toLowerCase().includes(search.toLowerCase())),
    );
  }, [filter, search]);

  const filters: FilterType[] = ['Tous', 'Actifs', 'Business', 'Tech', 'Créatif'];
  const activeCount = AGENTS.filter((a) => a.status === 'active').length;

  return (
    <AppLayout>
      <div className="flex flex-col h-full overflow-hidden">
        {/* Header */}
        <div className="flex-none px-8 py-6 border-b border-white/5">
          <div className="flex items-start justify-between gap-6 flex-wrap">
            <div>
              <h1 className="font-display text-3xl font-bold text-text-1 tracking-tight">
                Centre des Agents
              </h1>
              <p className="text-text-3 text-sm mt-1">
                {AGENTS.length} agents spécialisés —{' '}
                <span className="text-status-active">{activeCount} actifs</span> en ce moment
              </p>
            </div>

            {/* Search + filters */}
            <div className="flex items-center gap-3 flex-wrap">
              <div className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-3" />
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Rechercher un agent…"
                  className="pl-9 pr-4 py-2 bg-bg-2 border border-white/8 rounded-xl text-sm text-text-1 placeholder:text-text-3 focus:outline-none focus:border-accent-purple/40 w-56 transition-all"
                />
              </div>
              <div className="flex gap-1.5">
                {filters.map((f) => (
                  <button
                    key={f}
                    onClick={() => setFilter(f)}
                    className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all ${
                      filter === f
                        ? 'bg-accent-purple text-white shadow-purple'
                        : 'bg-bg-2 text-text-3 border border-white/5 hover:border-white/12 hover:text-text-2'
                    }`}
                  >
                    {f}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Main split: Network + Detail */}
        <div className="flex-1 flex overflow-hidden min-h-0">
          {/* Left: Network visualization */}
          <div className="flex-[3] relative border-r border-white/5 overflow-hidden">
            <AgentNetwork
              activeAgents={AGENTS.filter((a) => a.status === 'active').map((a) => a.name)}
              onSelect={setSelectedAgent}
              selected={selectedAgent}
            />
          </div>

          {/* Right: Detail panel */}
          <div className="flex-[2] overflow-y-auto bg-bg-1/40 backdrop-blur-sm">
            <AnimatePresence mode="wait">
              {selectedAgent ? (
                <motion.div
                  key={selectedAgent.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.25 }}
                  className="p-6 h-full"
                >
                  {/* Avatar + name */}
                  <div className="flex items-center gap-4 mb-6">
                    <AgentAvatar agent={selectedAgent} size={80} showGlow />
                    <div>
                      <h2 className="font-display text-2xl font-bold text-text-1">
                        {selectedAgent.name}
                      </h2>
                      <div className="text-xs font-mono text-text-3 uppercase tracking-widest mt-0.5">
                        {selectedAgent.role}
                      </div>
                      <div
                        className="mt-1 inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium"
                        style={{ background: selectedAgent.color + '22', color: selectedAgent.color }}
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-current" />
                        {selectedAgent.status === 'active' ? 'Actif' : 'En attente'}
                      </div>
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-sm text-text-2 leading-relaxed mb-6 bg-bg-2/60 rounded-xl p-4 border border-white/5">
                    {selectedAgent.description}
                  </p>

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-3 mb-6">
                    <div className="bg-bg-2 rounded-xl p-4 border border-white/5">
                      <div className="flex items-center gap-2 mb-1">
                        <CheckCircle size={13} className="text-status-active" />
                        <span className="text-xs text-text-3">Tâches complétées</span>
                      </div>
                      <div className="text-xl font-bold text-text-1 font-mono">
                        {selectedAgent.tasksCompleted.toLocaleString()}
                      </div>
                    </div>
                    <div className="bg-bg-2 rounded-xl p-4 border border-white/5">
                      <div className="flex items-center gap-2 mb-1">
                        <Star size={13} className="text-accent-gold" />
                        <span className="text-xs text-text-3">Taux de succès</span>
                      </div>
                      <div className="text-xl font-bold text-text-1 font-mono">
                        {selectedAgent.successRate}%
                      </div>
                    </div>
                  </div>

                  {/* Personality */}
                  <div className="mb-5">
                    <h3 className="text-xs font-mono uppercase tracking-widest text-text-3 mb-2 flex items-center gap-2">
                      <Activity size={11} /> Personnalité
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedAgent.personality.map((trait) => (
                        <span
                          key={trait}
                          className="px-3 py-1 rounded-full text-xs font-medium border"
                          style={{ borderColor: selectedAgent.color + '44', color: selectedAgent.color }}
                        >
                          {trait}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Skills */}
                  <div className="mb-5">
                    <h3 className="text-xs font-mono uppercase tracking-widest text-text-3 mb-2 flex items-center gap-2">
                      <Zap size={11} /> Compétences
                    </h3>
                    <div className="flex flex-col gap-1.5">
                      {selectedAgent.skills.map((skill) => (
                        <div key={skill} className="flex items-center gap-2">
                          <ChevronRight size={12} style={{ color: selectedAgent.color }} />
                          <span className="text-sm text-text-2">{skill}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Tools */}
                  <div className="mb-5">
                    <h3 className="text-xs font-mono uppercase tracking-widest text-text-3 mb-2 flex items-center gap-2">
                      <Cpu size={11} /> Outils
                    </h3>
                    <div className="flex flex-wrap gap-1.5">
                      {selectedAgent.tools.map((tool) => (
                        <span
                          key={tool}
                          className="px-2.5 py-1 rounded-lg text-xs bg-bg-3 text-text-2 border border-white/5"
                        >
                          {tool}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Limits */}
                  <div className="mb-6 bg-amber-500/5 border border-amber-500/15 rounded-xl p-3">
                    <div className="flex items-start gap-2">
                      <Shield size={12} className="text-amber-400 mt-0.5 flex-none" />
                      <p className="text-xs text-amber-300/80">{selectedAgent.limits}</p>
                    </div>
                  </div>

                  {/* CTA */}
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="w-full py-3 rounded-xl text-sm font-semibold text-white flex items-center justify-center gap-2 transition-all"
                    style={{ background: `linear-gradient(135deg, ${selectedAgent.gradient[0]}, ${selectedAgent.gradient[1]})` }}
                  >
                    <MessageCircle size={15} />
                    Contacter {selectedAgent.name}
                  </motion.button>
                </motion.div>
              ) : (
                <motion.div
                  key="placeholder"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex flex-col items-center justify-center h-full p-8 text-center"
                >
                  <div className="w-16 h-16 rounded-2xl bg-bg-2 border border-white/8 flex items-center justify-center mb-4">
                    <Users size={24} className="text-text-3" />
                  </div>
                  <h3 className="text-text-2 font-medium mb-2">Détails de l'agent</h3>
                  <p className="text-text-3 text-sm max-w-xs leading-relaxed">
                    Sélectionnez un agent dans le réseau ou dans la grille ci-dessous pour voir ses
                    détails, compétences et statistiques.
                  </p>
                  <div className="mt-6 flex flex-col gap-2 w-full max-w-xs">
                    {AGENTS.filter((a) => a.status === 'active').map((a) => (
                      <button
                        key={a.id}
                        onClick={() => setSelectedAgent(a)}
                        className="flex items-center gap-3 px-3 py-2 bg-bg-2 rounded-xl border border-white/5 hover:border-white/12 transition-all text-left"
                      >
                        <span className="text-lg">{a.emoji}</span>
                        <div>
                          <div className="text-sm text-text-1 font-medium">{a.name}</div>
                          <div className="text-xs text-text-3">{a.role}</div>
                        </div>
                        <div className="ml-auto w-1.5 h-1.5 rounded-full bg-status-active" />
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Bottom: Agent grid */}
        <div className="flex-none border-t border-white/5">
          <div className="px-8 pt-6 pb-2">
            <h2 className="text-sm font-mono uppercase tracking-widest text-text-3 mb-4">
              Tous les agents{filter !== 'Tous' ? ` — ${filter}` : ''}{' '}
              <span className="text-text-2">({filteredAgents.length})</span>
            </h2>
          </div>
          <div className="px-8 pb-8 overflow-x-auto">
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 min-w-max lg:min-w-0">
              {filteredAgents.map((agent, i) => (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.04, duration: 0.3 }}
                >
                  <AgentCard
                    agent={agent}
                    onClick={() => setSelectedAgent(agent)}
                    selected={selectedAgent?.id === agent.id}
                  />
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
