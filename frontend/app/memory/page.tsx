'use client';
import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, User, FolderOpen, Lightbulb, Dna, Tag, ChevronRight,
  Calendar, BarChart2, ArrowRight, Brain, Zap, Cpu, Database,
  Filter, Star, RefreshCw,
} from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import { MOCK_MEMORIES } from '@/lib/data';
import type { MemoryEntry } from '@/lib/types';

/* ------------------------------------------------------------------ */
/* Constants & helpers                                                  */
/* ------------------------------------------------------------------ */

type MemoryType = 'all' | MemoryEntry['type'];

const TYPE_CONFIG: Record<MemoryEntry['type'], {
  label: string; icon: React.ReactNode; bg: string; text: string;
  border: string; color: string; glow: string;
}> = {
  user: {
    label: 'Utilisateur',
    icon: <User size={14} />,
    bg: 'bg-blue-500/10', text: 'text-blue-400', border: 'border-blue-500/20',
    color: '#3B82F6', glow: '#3B82F620',
  },
  project: {
    label: 'Projet',
    icon: <FolderOpen size={14} />,
    bg: 'bg-green-500/10', text: 'text-green-400', border: 'border-green-500/20',
    color: '#22C55E', glow: '#22C55E20',
  },
  business: {
    label: 'Métier',
    icon: <Lightbulb size={14} />,
    bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/20',
    color: '#F59E0B', glow: '#F59E0B20',
  },
  evolution: {
    label: 'Évolution',
    icon: <Dna size={14} />,
    bg: 'bg-purple-500/10', text: 'text-purple-400', border: 'border-purple-500/20',
    color: '#8B5CF6', glow: '#8B5CF620',
  },
};

const LAYER_CARDS = [
  {
    type: 'user' as const,
    emoji: '👤',
    name: 'Mémoire Utilisateur',
    desc: 'Préférences, habitudes et contexte personnel',
    colorClass: 'from-blue-600/20 to-blue-900/10',
    borderClass: 'border-blue-500/15',
    pulseColor: '#3B82F6',
  },
  {
    type: 'project' as const,
    emoji: '📁',
    name: 'Mémoire Projet',
    desc: 'Données, résultats et apprentissages par projet',
    colorClass: 'from-green-600/20 to-green-900/10',
    borderClass: 'border-green-500/15',
    pulseColor: '#22C55E',
  },
  {
    type: 'business' as const,
    emoji: '💡',
    name: 'Mémoire Métier',
    desc: 'Méthodes éprouvées et bonnes pratiques sectorielles',
    colorClass: 'from-amber-600/20 to-amber-900/10',
    borderClass: 'border-amber-500/15',
    pulseColor: '#F59E0B',
  },
  {
    type: 'evolution' as const,
    emoji: '🧬',
    name: 'Mémoire Évolution',
    desc: 'Genèse des agents et adaptations du système',
    colorClass: 'from-purple-600/20 to-purple-900/10',
    borderClass: 'border-purple-500/15',
    pulseColor: '#8B5CF6',
  },
];

const ALL_TAGS = Array.from(new Set(MOCK_MEMORIES.flatMap((m) => m.tags))).sort();

function formatDate(d: Date) {
  return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' });
}

/* ------------------------------------------------------------------ */
/* Layer card                                                           */
/* ------------------------------------------------------------------ */
function MemoryLayerCard({
  layer, count, active, onClick,
}: {
  layer: typeof LAYER_CARDS[0];
  count: number;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <motion.button
      whileHover={{ y: -4 }}
      whileTap={{ scale: 0.97 }}
      onClick={onClick}
      className={`relative flex flex-col items-start p-5 rounded-2xl border transition-all text-left w-full overflow-hidden ${
        active
          ? `bg-gradient-to-br ${layer.colorClass} ${layer.borderClass} shadow-lg`
          : `bg-bg-2 border-white/5 hover:border-white/10`
      }`}
    >
      {/* Animated pulse dot */}
      <span
        className="absolute top-4 right-4 w-2 h-2 rounded-full"
        style={{ background: layer.pulseColor }}
      >
        <span
          className="absolute inset-0 rounded-full animate-ping opacity-60"
          style={{ background: layer.pulseColor }}
        />
      </span>

      <span className="text-2xl mb-3">{layer.emoji}</span>
      <div className="font-semibold text-text-1 text-sm leading-tight mb-1">{layer.name}</div>
      <div className="text-xs text-text-3 leading-relaxed mb-3">{layer.desc}</div>
      <div
        className="text-2xl font-bold font-mono"
        style={{ color: layer.pulseColor }}
      >
        {count}
        <span className="text-xs text-text-3 font-normal ml-1">entrées</span>
      </div>
    </motion.button>
  );
}

/* ------------------------------------------------------------------ */
/* Memory entry card                                                    */
/* ------------------------------------------------------------------ */
function MemoryCard({ entry }: { entry: MemoryEntry }) {
  const [expanded, setExpanded] = useState(false);
  const cfg = TYPE_CONFIG[entry.type];

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      whileHover={{ x: 2 }}
      onClick={() => setExpanded((v) => !v)}
      className="bg-bg-2 border border-white/5 rounded-xl p-4 cursor-pointer hover:border-white/10 transition-all group"
    >
      {/* Top row */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium border ${cfg.bg} ${cfg.text} ${cfg.border}`}>
            {cfg.icon}
            {cfg.label}
          </span>
          <span className="text-xs text-text-3 font-mono">via {entry.source}</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-text-3 flex-none">
          <Calendar size={11} />
          {formatDate(entry.createdAt)}
        </div>
      </div>

      {/* Content */}
      <p className={`text-sm text-text-2 leading-relaxed ${expanded ? '' : 'line-clamp-2'} transition-all group-hover:text-text-1`}>
        {entry.content}
      </p>

      {/* Relevance bar */}
      <div className="mt-3">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-1 text-xs text-text-3">
            <Star size={10} style={{ color: cfg.color }} />
            Pertinence
          </div>
          <span className="text-xs font-mono" style={{ color: cfg.color }}>{entry.relevance}%</span>
        </div>
        <div className="h-1 bg-bg-3 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${entry.relevance}%` }}
            transition={{ duration: 0.7, ease: 'easeOut', delay: 0.1 }}
            className="h-full rounded-full"
            style={{ background: cfg.color }}
          />
        </div>
      </div>

      {/* Tags */}
      {entry.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3">
          {entry.tags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs bg-bg-3 text-text-3 border border-white/5"
            >
              <Tag size={9} />
              {tag}
            </span>
          ))}
        </div>
      )}

      {expanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-3 pt-3 border-t border-white/5 text-xs text-text-3 font-mono"
        >
          ID: {entry.id} · Type: {entry.type} · Source: {entry.source}
        </motion.div>
      )}
    </motion.div>
  );
}

/* ------------------------------------------------------------------ */
/* Learning cycle flow                                                  */
/* ------------------------------------------------------------------ */
const FLOW_STEPS = [
  { icon: <User size={16} />, label: 'Input utilisateur', color: '#3B82F6' },
  { icon: <Cpu size={16} />, label: 'Mission agent', color: '#7C3AED' },
  { icon: <Zap size={16} />, label: 'Résultat', color: '#C9A84C' },
  { icon: <Brain size={16} />, label: 'Akasha', color: '#8B5CF6' },
  { icon: <RefreshCw size={16} />, label: 'Missions futures', color: '#22C55E' },
];

function LearningCycle() {
  return (
    <div className="bg-bg-2 border border-white/5 rounded-2xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <Database size={16} className="text-accent-purple" />
        <h3 className="text-sm font-mono uppercase tracking-widest text-text-3">
          Cycle d'apprentissage
        </h3>
      </div>
      <div className="flex items-center gap-2 flex-wrap">
        {FLOW_STEPS.map((step, i) => (
          <div key={step.label} className="flex items-center gap-2">
            <motion.div
              animate={{ scale: [1, 1.06, 1] }}
              transition={{ duration: 2.5, repeat: Infinity, delay: i * 0.5 }}
              className="flex flex-col items-center gap-2"
            >
              <div
                className="w-12 h-12 rounded-xl flex items-center justify-center"
                style={{ background: step.color + '20', color: step.color, border: `1px solid ${step.color}30` }}
              >
                {step.icon}
              </div>
              <span className="text-xs text-text-3 text-center w-20 leading-tight">{step.label}</span>
            </motion.div>
            {i < FLOW_STEPS.length - 1 && (
              <motion.div
                animate={{ opacity: [0.3, 1, 0.3] }}
                transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.5 }}
                className="mb-5"
              >
                <ArrowRight size={16} className="text-text-3" />
              </motion.div>
            )}
          </div>
        ))}
      </div>
      <p className="text-xs text-text-3 leading-relaxed mt-5 bg-bg-3/60 rounded-xl p-3 border border-white/5">
        Chaque interaction enrichit la mémoire Akasha. Les agents apprennent continuellement de
        chaque mission, adaptant leurs réponses futures grâce aux expériences accumulées.
      </p>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Main page                                                            */
/* ------------------------------------------------------------------ */
export default function MemoryPage() {
  const [typeFilter, setTypeFilter] = useState<MemoryType>('all');
  const [search, setSearch] = useState('');
  const [minRelevance, setMinRelevance] = useState(0);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);

  // Counts per layer
  const counts = useMemo(() => {
    const c: Record<MemoryEntry['type'], number> = { user: 0, project: 0, business: 0, evolution: 0 };
    MOCK_MEMORIES.forEach((m) => { c[m.type]++; });
    return c;
  }, []);

  const filtered = useMemo(() => {
    return MOCK_MEMORIES.filter((m) => {
      if (typeFilter !== 'all' && m.type !== typeFilter) return false;
      if (m.relevance < minRelevance) return false;
      if (selectedTag && !m.tags.includes(selectedTag)) return false;
      if (search) {
        const q = search.toLowerCase();
        return m.content.toLowerCase().includes(q) || m.source.toLowerCase().includes(q) || m.tags.some((t) => t.toLowerCase().includes(q));
      }
      return true;
    });
  }, [typeFilter, search, minRelevance, selectedTag]);

  return (
    <AppLayout>
      <div className="flex flex-col h-full overflow-hidden">
        {/* Header */}
        <div className="flex-none px-8 py-6 border-b border-white/5">
          <div className="flex items-start justify-between gap-6 flex-wrap">
            <div>
              <h1 className="font-display text-3xl font-bold text-text-1 tracking-tight">
                Mémoire Akasha
              </h1>
              <p className="text-text-3 text-sm mt-1">
                La mémoire vivante d'Angeleck — chaque interaction enrichit le système
              </p>
            </div>
            <div className="relative">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-3" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Rechercher dans la mémoire…"
                className="pl-9 pr-4 py-2 bg-bg-2 border border-white/8 rounded-xl text-sm text-text-1 placeholder:text-text-3 focus:outline-none focus:border-accent-purple/40 w-64 transition-all"
              />
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-8 py-6">
          {/* Layer cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {LAYER_CARDS.map((layer) => (
              <MemoryLayerCard
                key={layer.type}
                layer={layer}
                count={counts[layer.type]}
                active={typeFilter === layer.type}
                onClick={() => setTypeFilter((prev) => prev === layer.type ? 'all' : layer.type)}
              />
            ))}
          </div>

          {/* Main 2-column layout */}
          <div className="flex gap-6">
            {/* Left: filter sidebar */}
            <div className="w-56 flex-none">
              <div className="bg-bg-2 border border-white/5 rounded-2xl p-4 sticky top-0">
                <div className="flex items-center gap-2 mb-4">
                  <Filter size={13} className="text-text-3" />
                  <span className="text-xs font-mono uppercase tracking-widest text-text-3">Filtres</span>
                </div>

                {/* Type filter */}
                <div className="mb-5">
                  <div className="text-xs text-text-3 mb-2">Type</div>
                  <div className="flex flex-col gap-1">
                    {(['all', 'user', 'project', 'business', 'evolution'] as MemoryType[]).map((t) => {
                      const cfg = t !== 'all' ? TYPE_CONFIG[t] : null;
                      return (
                        <button
                          key={t}
                          onClick={() => setTypeFilter(t)}
                          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs transition-all text-left ${
                            typeFilter === t
                              ? 'bg-accent-purple/15 text-accent-purple-light border border-accent-purple/25'
                              : 'text-text-3 hover:text-text-2 hover:bg-bg-3'
                          }`}
                        >
                          {cfg ? cfg.icon : <BarChart2 size={13} />}
                          {cfg ? cfg.label : 'Tous'}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Relevance slider */}
                <div className="mb-5">
                  <div className="flex justify-between text-xs text-text-3 mb-2">
                    <span>Pertinence min.</span>
                    <span className="text-accent-purple font-mono">{minRelevance}%</span>
                  </div>
                  <input
                    type="range"
                    min={0}
                    max={100}
                    step={5}
                    value={minRelevance}
                    onChange={(e) => setMinRelevance(Number(e.target.value))}
                    className="w-full accent-accent-purple cursor-pointer"
                  />
                </div>

                {/* Tag cloud */}
                <div>
                  <div className="text-xs text-text-3 mb-2">Tags</div>
                  <div className="flex flex-wrap gap-1.5">
                    {ALL_TAGS.map((tag) => (
                      <button
                        key={tag}
                        onClick={() => setSelectedTag((prev) => prev === tag ? null : tag)}
                        className={`px-2 py-0.5 rounded-md text-xs border transition-all ${
                          selectedTag === tag
                            ? 'bg-accent-purple/20 text-accent-purple-light border-accent-purple/30'
                            : 'bg-bg-3 text-text-3 border-white/5 hover:border-white/12 hover:text-text-2'
                        }`}
                      >
                        {tag}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Reset */}
                {(typeFilter !== 'all' || minRelevance > 0 || selectedTag || search) && (
                  <button
                    onClick={() => { setTypeFilter('all'); setMinRelevance(0); setSelectedTag(null); setSearch(''); }}
                    className="mt-4 w-full text-xs text-text-3 hover:text-text-2 flex items-center justify-center gap-1.5 py-2 rounded-lg hover:bg-bg-3 transition-all border border-white/5"
                  >
                    <RefreshCw size={11} />
                    Réinitialiser
                  </button>
                )}
              </div>
            </div>

            {/* Right: memory entries */}
            <div className="flex-1 min-w-0">
              {/* Results header */}
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-mono text-text-3 uppercase tracking-widest">
                  {filtered.length} entrée{filtered.length !== 1 ? 's' : ''}
                  {typeFilter !== 'all' && ` · ${TYPE_CONFIG[typeFilter as MemoryEntry['type']].label}`}
                  {selectedTag && ` · #${selectedTag}`}
                </span>
                <div className="flex items-center gap-1 text-xs text-text-3">
                  <ChevronRight size={12} />
                  triées par pertinence
                </div>
              </div>

              <AnimatePresence mode="popLayout">
                <div className="flex flex-col gap-3">
                  {filtered
                    .slice()
                    .sort((a, b) => b.relevance - a.relevance)
                    .map((entry) => (
                      <MemoryCard key={entry.id} entry={entry} />
                    ))}
                </div>
              </AnimatePresence>

              {filtered.length === 0 && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex flex-col items-center justify-center py-20 text-center"
                >
                  <Brain size={36} className="text-text-3 mb-4" />
                  <h3 className="text-text-2 font-medium mb-2">Aucune mémoire trouvée</h3>
                  <p className="text-text-3 text-sm">Ajustez vos filtres pour afficher les entrées.</p>
                </motion.div>
              )}
            </div>
          </div>

          {/* Learning cycle */}
          <div className="mt-8">
            <LearningCycle />
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
