'use client';
import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus, ChevronDown, ChevronUp, CheckCircle, Clock, Circle,
  AlertCircle, Flame, ArrowRight, BarChart2, Calendar,
  Layers, Users, Target, TrendingUp,
} from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import { MOCK_PROJECTS, AGENTS } from '@/lib/data';
import type { Project, Mission } from '@/lib/types';

/* ---- helpers ---- */
const agentById = (id: string) => AGENTS.find((a) => a.id === id);

const STATUS_CONFIG = {
  planning: { label: 'Planification', bg: 'bg-blue-500/15', text: 'text-blue-400', border: 'border-blue-500/25', dot: '#3B82F6' },
  active:   { label: 'Actif',        bg: 'bg-green-500/15', text: 'text-green-400', border: 'border-green-500/25', dot: '#22C55E' },
  review:   { label: 'En revue',     bg: 'bg-amber-500/15', text: 'text-amber-400', border: 'border-amber-500/25', dot: '#F59E0B' },
  completed:{ label: 'Terminé',      bg: 'bg-zinc-500/15',  text: 'text-zinc-400',  border: 'border-zinc-500/25',  dot: '#71717A' },
} as const;

const PRIORITY_CONFIG = {
  critical: { label: 'Critique', color: '#EF4444' },
  high:     { label: 'Haute',    color: '#F97316' },
  medium:   { label: 'Moyenne',  color: '#EAB308' },
  low:      { label: 'Faible',   color: '#6B7280' },
} as const;

const MISSION_STATUS_ICONS: Record<Mission['status'], React.ReactNode> = {
  completed: <CheckCircle size={13} className="text-green-400 flex-none" />,
  active:    <Clock       size={13} className="text-amber-400 flex-none" />,
  pending:   <Circle      size={13} className="text-text-3 flex-none" />,
  failed:    <AlertCircle size={13} className="text-red-400 flex-none" />,
};

function formatDate(d: Date) {
  return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' });
}

function StatCard({ icon, label, value, color = '#7C3AED' }: { icon: React.ReactNode; label: string; value: number | string; color?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-bg-2 border border-white/5 rounded-2xl p-5 flex items-center gap-4"
    >
      <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-none" style={{ background: color + '20' }}>
        <span style={{ color }}>{icon}</span>
      </div>
      <div>
        <div className="text-2xl font-bold text-text-1 font-mono leading-none">{value}</div>
        <div className="text-xs text-text-3 mt-1">{label}</div>
      </div>
    </motion.div>
  );
}

function MissionRow({ mission }: { mission: Mission }) {
  return (
    <div className="flex items-center gap-3 py-2.5 px-3 rounded-lg hover:bg-bg-3/40 transition-all group">
      {MISSION_STATUS_ICONS[mission.status]}
      <div className="flex-1 min-w-0">
        <div className="text-sm text-text-2 truncate group-hover:text-text-1 transition-colors">
          {mission.title}
        </div>
        {mission.agents.length > 0 && (
          <div className="flex items-center gap-1 mt-0.5">
            {mission.agents.map((id) => {
              const a = agentById(id);
              return a ? (
                <span key={id} className="text-xs" title={a.name}>{a.emoji}</span>
              ) : null;
            })}
          </div>
        )}
      </div>
      <div className="flex-none text-right">
        <div className="text-xs font-mono text-text-3">{mission.progress}%</div>
        {mission.completedAt && (
          <div className="text-xs text-text-3">{formatDate(mission.completedAt)}</div>
        )}
      </div>
      {mission.progress > 0 && mission.progress < 100 && (
        <div className="flex-none w-16">
          <div className="h-1 bg-bg-3 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-accent-purple"
              style={{ width: `${mission.progress}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

function ProjectCard({ project }: { project: Project }) {
  const [expanded, setExpanded] = useState(false);
  const sc = STATUS_CONFIG[project.status];
  const pc = PRIORITY_CONFIG[project.priority];

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-bg-2 border border-white/5 rounded-2xl overflow-hidden hover:border-white/10 transition-all group"
    >
      {/* Priority stripe */}
      <div className="h-0.5 w-full" style={{ background: `linear-gradient(90deg, ${pc.color}80, transparent)` }} />

      <div className="p-6">
        {/* Top row: badges + menu */}
        <div className="flex items-center justify-between mb-4 gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${sc.bg} ${sc.text} ${sc.border}`}>
              <span className="w-1.5 h-1.5 rounded-full" style={{ background: sc.dot }} />
              {sc.label}
            </span>
            <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-bg-3 border border-white/5" style={{ color: pc.color }}>
              <Flame size={10} />
              {pc.label}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            {project.tags.map((tag) => (
              <span key={tag} className="text-xs px-2 py-0.5 rounded-md bg-bg-3 text-text-3 border border-white/5">
                {tag}
              </span>
            ))}
          </div>
        </div>

        {/* Name + description */}
        <h3 className="font-display text-lg font-bold text-text-1 leading-tight mb-1.5 group-hover:text-white transition-colors">
          {project.name}
        </h3>
        <p className="text-sm text-text-3 leading-relaxed mb-5">{project.description}</p>

        {/* Progress bar */}
        <div className="mb-5">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs text-text-3">Progression</span>
            <span className="text-xs font-mono font-bold text-text-2">{project.progress}%</span>
          </div>
          <div className="h-1.5 bg-bg-3 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${project.progress}%` }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
              className="h-full rounded-full"
              style={{
                background:
                  project.progress === 100
                    ? 'linear-gradient(90deg, #22C55E, #16A34A)'
                    : 'linear-gradient(90deg, #7C3AED, #C9A84C)',
              }}
            />
          </div>
        </div>

        {/* Agents + dates */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex -space-x-1.5">
              {project.agents.slice(0, 5).map((id) => {
                const a = agentById(id);
                return a ? (
                  <div
                    key={id}
                    title={a.name}
                    className="w-7 h-7 rounded-full border-2 border-bg-2 flex items-center justify-center text-sm cursor-default hover:z-10 relative hover:scale-110 transition-transform"
                    style={{ background: `linear-gradient(135deg, ${a.gradient[0]}, ${a.gradient[1]})` }}
                  >
                    {a.emoji}
                  </div>
                ) : null;
              })}
              {project.agents.length > 5 && (
                <div className="w-7 h-7 rounded-full border-2 border-bg-2 bg-bg-3 flex items-center justify-center text-xs text-text-3 font-mono">
                  +{project.agents.length - 5}
                </div>
              )}
            </div>
            <span className="text-xs text-text-3">{project.agents.length} agent{project.agents.length > 1 ? 's' : ''}</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-text-3">
            <Calendar size={11} />
            <span>{formatDate(project.createdAt)}</span>
            <ArrowRight size={10} />
            <span>{formatDate(project.updatedAt)}</span>
          </div>
        </div>

        {/* Expand button */}
        <button
          onClick={() => setExpanded((v) => !v)}
          className="mt-5 w-full flex items-center justify-between px-3 py-2 rounded-xl bg-bg-3/60 hover:bg-bg-3 border border-white/5 text-xs text-text-3 hover:text-text-2 transition-all"
        >
          <span className="font-mono uppercase tracking-wider">
            {project.missions.length} mission{project.missions.length > 1 ? 's' : ''}
          </span>
          {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
        </button>
      </div>

      {/* Missions list */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="px-6 pb-5 border-t border-white/5 pt-4">
              <div className="text-xs font-mono uppercase tracking-widest text-text-3 mb-3">
                Missions
              </div>
              <div className="flex flex-col">
                {project.missions.map((m) => (
                  <MissionRow key={m.id} mission={m} />
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function ProjectsPage() {
  const stats = useMemo(() => {
    const active = MOCK_PROJECTS.filter((p) => p.status === 'active').length;
    const completed = MOCK_PROJECTS.filter((p) => p.status === 'completed').length;
    const planning = MOCK_PROJECTS.filter((p) => p.status === 'planning').length;
    const agentIds = new Set(MOCK_PROJECTS.flatMap((p) => p.agents));
    return { active, completed, planning, agents: agentIds.size };
  }, []);

  return (
    <AppLayout>
      <div className="flex flex-col h-full overflow-hidden">
        {/* Header */}
        <div className="flex-none px-8 py-6 border-b border-white/5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="font-display text-3xl font-bold text-text-1 tracking-tight">Mes Projets</h1>
              <p className="text-text-3 text-sm mt-1">
                Pilotez vos missions multi-agents en temps réel
              </p>
            </div>
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              className="flex items-center gap-2 px-4 py-2.5 bg-accent-purple hover:bg-accent-purple/90 text-white text-sm font-semibold rounded-xl shadow-purple transition-all"
            >
              <Plus size={16} />
              Nouveau Projet
            </motion.button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-8 py-6">
          {/* Stats row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <StatCard icon={<TrendingUp size={18} />} label="Projets actifs"   value={stats.active}    color="#22C55E" />
            <StatCard icon={<CheckCircle size={18} />}  label="Terminés"        value={stats.completed}  color="#7C3AED" />
            <StatCard icon={<Layers size={18} />}        label="En planification" value={stats.planning}  color="#3B82F6" />
            <StatCard icon={<Users size={18} />}         label="Agents déployés" value={stats.agents}    color="#C9A84C" />
          </div>

          {/* Projects grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {MOCK_PROJECTS.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>

          {MOCK_PROJECTS.length === 0 && (
            <div className="flex flex-col items-center justify-center py-24 text-center">
              <Target size={40} className="text-text-3 mb-4" />
              <h3 className="text-text-2 font-medium mb-2">Aucun projet</h3>
              <p className="text-text-3 text-sm">Créez votre premier projet pour démarrer.</p>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
