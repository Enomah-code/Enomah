'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { motion, useInView, useScroll, useTransform } from 'framer-motion';
import {
  ArrowRight,
  Brain,
  Layers,
  Users,
  Zap,
  CheckCircle2,
  BarChart3,
  Target,
  Github,
  Twitter,
  Linkedin,
  ChevronRight,
} from 'lucide-react';
import AgentCard from '@/components/agents/AgentCard';
import { AGENTS } from '@/lib/data';

/* ─────────────────────────── helpers ─────────────────────────── */

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-mono uppercase tracking-widest border border-accent-purple/30 bg-accent-purple/8 text-accent-purple-light mb-6">
      {children}
    </span>
  );
}

function FadeInSection({
  children,
  delay = 0,
  className = '',
}: {
  children: React.ReactNode;
  delay?: number;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: '-60px' });
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 32 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.7, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/* ─────────────────────────── Nav ─────────────────────────── */

function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handler, { passive: true });
    return () => window.removeEventListener('scroll', handler);
  }, []);

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-bg-1/90 backdrop-blur-xl border-b border-white/6 shadow-[0_4px_32px_rgba(0,0,0,0.5)]'
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-purple to-accent-purple-dark flex items-center justify-center text-sm font-bold text-white shadow-purple-sm">
            A
          </div>
          <div className="flex items-baseline gap-0.5">
            <span className="text-text-3 font-mono text-xs">/</span>
            <span className="font-display font-bold text-text-1 text-lg tracking-tight">Angeleck</span>
          </div>
        </Link>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-8">
          {[
            { label: 'Fonctionnement', href: '#fonctionnement' },
            { label: 'Agents', href: '#agents' },
            { label: 'Tarifs', href: '#tarifs' },
          ].map(({ label, href }) => (
            <a
              key={label}
              href={href}
              className="text-sm text-text-2 hover:text-text-1 transition-colors font-medium"
            >
              {label}
            </a>
          ))}
          <Link
            href="/dashboard"
            className="text-sm text-text-2 hover:text-text-1 transition-colors font-medium"
          >
            Connexion
          </Link>
        </div>

        {/* CTA */}
        <Link
          href="/dashboard"
          className="hidden md:flex items-center gap-2 px-5 py-2 rounded-xl text-sm font-semibold text-white transition-all hover:scale-[1.03] active:scale-[0.98]"
          style={{ background: 'linear-gradient(135deg, #7C3AED, #5B21B6)' }}
        >
          Parler à Raphaël
          <ArrowRight size={14} />
        </Link>

        {/* Mobile hamburger */}
        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className="md:hidden p-2 rounded-lg text-text-2 hover:text-text-1"
        >
          <div className="flex flex-col gap-1.5">
            <span
              className={`block h-0.5 w-5 bg-current transition-transform origin-center ${menuOpen ? 'rotate-45 translate-y-2' : ''}`}
            />
            <span
              className={`block h-0.5 w-5 bg-current transition-opacity ${menuOpen ? 'opacity-0' : ''}`}
            />
            <span
              className={`block h-0.5 w-5 bg-current transition-transform origin-center ${menuOpen ? '-rotate-45 -translate-y-2' : ''}`}
            />
          </div>
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="md:hidden bg-bg-2/95 backdrop-blur-xl border-b border-white/6 px-6 py-4 flex flex-col gap-4"
        >
          {['Fonctionnement', 'Agents', 'Tarifs', 'Connexion'].map((l) => (
            <a key={l} href="#" className="text-sm text-text-2 hover:text-text-1 transition-colors">
              {l}
            </a>
          ))}
          <Link
            href="/dashboard"
            className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white mt-1"
            style={{ background: 'linear-gradient(135deg, #7C3AED, #5B21B6)' }}
          >
            Parler à Raphaël <ArrowRight size={14} />
          </Link>
        </motion.div>
      )}
    </nav>
  );
}

/* ─────────────────────────── Orbiting avatars ─────────────────────────── */

const ORBIT_AGENTS = [
  { emoji: '👩‍💼', name: 'Sofia', color: '#60A5FA', angle: 0 },
  { emoji: '📢', name: 'Maya', color: '#F87171', angle: 60 },
  { emoji: '✍️', name: 'Nathan', color: '#FB923C', angle: 120 },
  { emoji: '👩‍🎨', name: 'Elena', color: '#F472B6', angle: 180 },
  { emoji: '👨‍💻', name: 'Gabriel', color: '#2DD4BF', angle: 240 },
  { emoji: '💰', name: 'Adam', color: '#FCD34D', angle: 300 },
];

function OrbitingAgents() {
  return (
    <div className="relative w-[360px] h-[360px] flex-shrink-0">
      {/* Orbit ring */}
      <div className="absolute inset-0 rounded-full border border-white/6" />
      <div className="absolute inset-8 rounded-full border border-accent-purple/12" />

      {/* Center — Raphaël */}
      <div className="absolute inset-0 flex items-center justify-center">
        <motion.div
          animate={{ scale: [1, 1.06, 1] }}
          transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
          className="w-20 h-20 rounded-full flex items-center justify-center text-4xl shadow-purple"
          style={{
            background: 'linear-gradient(135deg, #8B5CF6, #4C1D95)',
            boxShadow: '0 0 40px rgba(124,58,237,0.5)',
          }}
        >
          🧠
        </motion.div>
      </div>

      {/* Orbit track + agents */}
      <motion.div
        className="absolute inset-0"
        animate={{ rotate: 360 }}
        transition={{ duration: 22, repeat: Infinity, ease: 'linear' }}
      >
        {ORBIT_AGENTS.map((agent, i) => {
          const rad = (agent.angle * Math.PI) / 180;
          const r = 150; // orbit radius (half of 300px ring)
          const cx = 180 + r * Math.cos(rad) - 24; // 24 = half of agent circle size
          const cy = 180 + r * Math.sin(rad) - 24;
          return (
            <motion.div
              key={agent.name}
              className="absolute w-12 h-12 rounded-full flex items-center justify-center text-xl border border-white/10"
              style={{
                left: cx,
                top: cy,
                background: `linear-gradient(135deg, ${agent.color}44, ${agent.color}22)`,
                boxShadow: `0 0 14px ${agent.color}55`,
              }}
              // Counter-rotate so emoji stays upright
              animate={{ rotate: -360 }}
              transition={{ duration: 22, repeat: Infinity, ease: 'linear' }}
            >
              {agent.emoji}
            </motion.div>
          );
        })}
      </motion.div>

      {/* Decorative glow blobs */}
      <div
        className="absolute top-4 right-4 w-16 h-16 rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(201,168,76,0.15), transparent)',
          filter: 'blur(12px)',
        }}
      />
      <div
        className="absolute bottom-4 left-4 w-20 h-20 rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(124,58,237,0.2), transparent)',
          filter: 'blur(16px)',
        }}
      />
    </div>
  );
}

/* ─────────────────────────── Hero ─────────────────────────── */

const STATS = [
  { value: '11', label: 'agents experts' },
  { value: '95.8%', label: 'taux de succès' },
  { value: '1 247', label: 'missions réalisées' },
  { value: '99.7%', label: 'uptime' },
];

function Hero() {
  const { scrollYProgress } = useScroll();
  const bgY = useTransform(scrollYProgress, [0, 1], ['0%', '25%']);

  return (
    <section className="relative min-h-screen flex flex-col justify-center overflow-hidden bg-bg-1">
      {/* Background orbs */}
      <motion.div style={{ y: bgY }} className="absolute inset-0 pointer-events-none">
        <motion.div
          animate={{ x: [0, 40, 0], y: [0, -30, 0] }}
          transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute top-1/4 left-1/4 w-[600px] h-[600px] rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(124,58,237,0.18), transparent 70%)',
            filter: 'blur(60px)',
            opacity: 0.55,
          }}
        />
        <motion.div
          animate={{ x: [0, -50, 0], y: [0, 40, 0] }}
          transition={{ duration: 24, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(201,168,76,0.14), transparent 70%)',
            filter: 'blur(80px)',
            opacity: 0.45,
          }}
        />
      </motion.div>

      {/* Grid overlay */}
      <div className="absolute inset-0 bg-grid opacity-60 pointer-events-none" />

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 pt-28 pb-16 flex flex-col lg:flex-row items-center gap-12 lg:gap-16">
        {/* Left */}
        <div className="flex-1 flex flex-col items-start max-w-2xl">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="flex items-center gap-2 px-4 py-2 rounded-full border border-status-active/30 bg-status-active/8 text-status-active text-xs font-mono uppercase tracking-widest mb-8"
          >
            <span className="w-2 h-2 rounded-full bg-status-active status-active" />
            Organisation IA Autonome · v1.0
          </motion.div>

          {/* Headline */}
          <div className="mb-6">
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-2xl md:text-3xl text-text-2 font-sans font-light mb-1"
            >
              Bienvenue dans
            </motion.p>
            <motion.h1
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.2 }}
              className="font-display font-black text-7xl md:text-8xl text-gradient leading-none tracking-tight mb-3"
            >
              Angeleck
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.35 }}
              className="font-display italic text-2xl md:text-3xl"
              style={{ color: '#C9A84C' }}
            >
              L'entreprise IA qui grandit avec vous.
            </motion.p>
          </div>

          {/* Subtext */}
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.45 }}
            className="text-text-2 text-base md:text-lg leading-relaxed max-w-xl mb-8"
          >
            Une équipe d'agents intelligents capable de créer, analyser, automatiser et
            développer vos projets — coordonnée par Raphaël, votre directeur IA.
          </motion.p>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.55 }}
            className="flex flex-wrap gap-3 mb-10"
          >
            <Link
              href="/dashboard"
              className="group flex items-center gap-2 px-6 py-3.5 rounded-xl font-semibold text-white text-sm transition-all hover:scale-[1.03] active:scale-[0.97] shadow-purple"
              style={{ background: 'linear-gradient(135deg, #7C3AED, #5B21B6)' }}
            >
              Parler à Raphaël
              <ArrowRight size={15} className="transition-transform group-hover:translate-x-1" />
            </Link>
            <a
              href="#agents"
              className="flex items-center gap-2 px-6 py-3.5 rounded-xl font-semibold text-text-1 text-sm border border-white/12 bg-white/4 hover:bg-white/7 hover:border-white/20 transition-all"
            >
              Découvrir les agents
              <ChevronRight size={15} />
            </a>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.68 }}
            className="grid grid-cols-2 sm:grid-cols-4 gap-4"
          >
            {STATS.map(({ value, label }) => (
              <div key={label} className="flex flex-col">
                <span className="font-display font-bold text-2xl text-gradient-gold leading-none mb-0.5">
                  {value}
                </span>
                <span className="text-xs text-text-3 leading-tight">{label}</span>
              </div>
            ))}
          </motion.div>
        </div>

        {/* Right — orbiting agents */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.9, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
          className="hidden lg:flex flex-col items-center justify-center"
        >
          <OrbitingAgents />
          <p className="text-xs text-text-3 font-mono mt-4 tracking-wider">
            11 agents · réseau neural IA
          </p>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
      >
        <span className="text-xs text-text-3 font-mono tracking-widest uppercase">Découvrir</span>
        <motion.div
          animate={{ y: [0, 6, 0] }}
          transition={{ duration: 1.4, repeat: Infinity }}
          className="w-5 h-8 rounded-full border border-white/12 flex items-start justify-center p-1"
        >
          <div className="w-1 h-2 rounded-full bg-accent-purple" />
        </motion.div>
      </motion.div>
    </section>
  );
}

/* ─────────────────────────── How it works ─────────────────────────── */

const STEPS = [
  {
    number: '01',
    icon: Brain,
    title: 'Analyse profonde',
    description:
      'Raphaël écoute votre besoin, pose les bonnes questions et analyse en profondeur votre contexte, vos objectifs et vos contraintes pour construire une vision claire de la mission.',
    color: '#8B5CF6',
  },
  {
    number: '02',
    icon: Layers,
    title: 'Décomposition',
    description:
      'La mission est découpée en tâches précises et attribuées à chaque agent spécialisé selon ses compétences. Chaque micro-mission a un objectif clair et des critères de succès définis.',
    color: '#60A5FA',
  },
  {
    number: '03',
    icon: Zap,
    title: 'Activation agents',
    description:
      'Les agents experts sont mobilisés simultanément. Sofia analyse le marché, Maya prépare les campagnes, Nathan rédige les textes — tout en parallèle, sans perte de temps.',
    color: '#F59E0B',
  },
  {
    number: '04',
    icon: Users,
    title: 'Collaboration',
    description:
      'Les agents communiquent, partagent leurs données et s\'alignent en temps réel. Gabriel intègre les systèmes, Emma valide les métriques, Léa sécurise chaque décision sensible.',
    color: '#10B981',
  },
  {
    number: '05',
    icon: CheckCircle2,
    title: 'Synthèse & livraison',
    description:
      'Raphaël agrège tous les résultats, rédige le rapport final et vous livre un travail complet, cohérent et directement actionnable — avec mémoire de tout ce qui a été appris.',
    color: '#C9A84C',
  },
];

function HowItWorks() {
  return (
    <section id="fonctionnement" className="py-28 bg-bg-0 relative overflow-hidden">
      <div className="absolute inset-0 bg-grid opacity-40 pointer-events-none" />

      <div className="max-w-7xl mx-auto px-6 relative z-10">
        <FadeInSection className="text-center mb-20">
          <SectionLabel>Fonctionnement</SectionLabel>
          <h2 className="font-display font-bold text-4xl md:text-5xl text-text-1 mb-4">
            Comment fonctionne{' '}
            <span className="text-gradient">Angeleck</span>
          </h2>
          <p className="text-text-2 text-lg max-w-2xl mx-auto">
            Un processus en 5 étapes, orchestré par Raphaël, pour transformer vos idées en
            résultats concrets.
          </p>
        </FadeInSection>

        <div className="flex flex-col gap-12">
          {STEPS.map((step, i) => {
            const Icon = step.icon;
            const isLeft = i % 2 === 0;
            return (
              <FadeInSection key={step.number} delay={i * 0.08}>
                <div
                  className={`flex flex-col md:flex-row items-center gap-8 ${
                    isLeft ? 'md:flex-row' : 'md:flex-row-reverse'
                  }`}
                >
                  {/* Number */}
                  <div className="flex-shrink-0 w-20 h-20 rounded-2xl glass flex items-center justify-center">
                    <span
                      className="font-display font-black text-3xl"
                      style={{ color: step.color }}
                    >
                      {step.number}
                    </span>
                  </div>

                  {/* Connector line */}
                  <div className="hidden md:block flex-shrink-0 w-8 h-0.5 bg-gradient-to-r from-white/5 to-white/10" />

                  {/* Card */}
                  <div
                    className={`flex-1 glass rounded-2xl p-6 border transition-all hover:border-white/12 group relative overflow-hidden`}
                    style={{ borderColor: `${step.color}18` }}
                  >
                    <div
                      className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity"
                      style={{
                        background: `radial-gradient(circle at ${isLeft ? '0% 50%' : '100% 50%'}, ${step.color}08, transparent 60%)`,
                      }}
                    />
                    <div className="relative z-10 flex items-start gap-4">
                      <div
                        className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                        style={{ background: `${step.color}18`, color: step.color }}
                      >
                        <Icon size={18} />
                      </div>
                      <div>
                        <h3 className="font-display font-bold text-xl text-text-1 mb-2">
                          {step.title}
                        </h3>
                        <p className="text-text-2 text-sm leading-relaxed">{step.description}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </FadeInSection>
            );
          })}
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────── Agents preview ─────────────────────────── */

const PREVIEW_AGENT_IDS = ['sofia', 'maya', 'nathan', 'elena', 'gabriel', 'adam'];

function AgentsPreview() {
  const previewAgents = AGENTS.filter((a) => PREVIEW_AGENT_IDS.includes(a.id));

  return (
    <section id="agents" className="py-28 bg-bg-1 relative overflow-hidden">
      {/* Background glow */}
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] rounded-full pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse, rgba(124,58,237,0.08), transparent 70%)',
          filter: 'blur(40px)',
        }}
      />

      <div className="max-w-7xl mx-auto px-6 relative z-10">
        <FadeInSection className="text-center mb-16">
          <SectionLabel>L'équipe</SectionLabel>
          <h2 className="font-display font-bold text-4xl md:text-5xl text-text-1 mb-4">
            L'équipe d'experts
          </h2>
          <p className="text-text-2 text-lg max-w-2xl mx-auto">
            11 agents IA spécialisés, chacun maître dans son domaine, travaillant en symbiose
            sous la direction de Raphaël.
          </p>
        </FadeInSection>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 mb-10">
          {previewAgents.map((agent, i) => (
            <FadeInSection key={agent.id} delay={i * 0.07}>
              <AgentCard agent={agent} />
            </FadeInSection>
          ))}
        </div>

        <FadeInSection delay={0.4} className="flex justify-center">
          <Link
            href="/dashboard"
            className="group flex items-center gap-2 px-6 py-3 rounded-xl border border-accent-purple/30 bg-accent-purple/8 text-accent-purple-light text-sm font-semibold hover:bg-accent-purple/15 hover:border-accent-purple/50 transition-all"
          >
            Voir les 11 agents
            <ArrowRight size={14} className="transition-transform group-hover:translate-x-1" />
          </Link>
        </FadeInSection>
      </div>
    </section>
  );
}

/* ─────────────────────────── CTA section ─────────────────────────── */

function CtaSection() {
  return (
    <section className="py-28 bg-bg-0 relative overflow-hidden">
      <div className="absolute inset-0 bg-grid opacity-30 pointer-events-none" />

      <div className="max-w-4xl mx-auto px-6 relative z-10">
        <FadeInSection>
          <div className="border-glow rounded-3xl p-px">
            <div className="rounded-3xl bg-bg-2 p-12 md:p-16 text-center relative overflow-hidden">
              {/* Inner glow */}
              <div
                className="absolute inset-0 pointer-events-none"
                style={{
                  background:
                    'radial-gradient(ellipse at 50% 0%, rgba(124,58,237,0.12), transparent 60%)',
                }}
              />

              <div className="relative z-10">
                <div className="text-5xl mb-6">🚀</div>
                <h2 className="font-display font-bold text-4xl md:text-5xl text-text-1 mb-4 leading-tight">
                  Prêt à créer votre
                  <br />
                  <span className="text-gradient">organisation IA ?</span>
                </h2>
                <p className="text-text-2 text-lg mb-10 max-w-xl mx-auto leading-relaxed">
                  Rejoignez les entrepreneurs qui font confiance à Angeleck pour automatiser,
                  analyser et développer leur business — sans se noyer dans les outils.
                </p>
                <div className="flex flex-wrap gap-4 justify-center">
                  <Link
                    href="/dashboard"
                    className="group flex items-center gap-2 px-8 py-4 rounded-xl font-bold text-white text-base transition-all hover:scale-[1.03] active:scale-[0.97] shadow-purple-lg"
                    style={{ background: 'linear-gradient(135deg, #7C3AED, #5B21B6)' }}
                  >
                    Commencer gratuitement
                    <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
                  </Link>
                  <a
                    href="#fonctionnement"
                    className="flex items-center gap-2 px-8 py-4 rounded-xl font-semibold text-text-1 text-base border border-white/12 hover:border-white/20 hover:bg-white/4 transition-all"
                  >
                    En savoir plus
                  </a>
                </div>

                {/* Trust indicators */}
                <div className="flex flex-wrap gap-6 justify-center mt-10">
                  {[
                    { icon: CheckCircle2, text: 'Sans carte bancaire' },
                    { icon: BarChart3, text: 'Résultats en 24h' },
                    { icon: Target, text: '99.7% de disponibilité' },
                  ].map(({ icon: Icon, text }) => (
                    <div key={text} className="flex items-center gap-2 text-sm text-text-3">
                      <Icon size={14} className="text-status-active" />
                      <span>{text}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </FadeInSection>
      </div>
    </section>
  );
}

/* ─────────────────────────── Footer ─────────────────────────── */

function Footer() {
  return (
    <footer className="bg-bg-0 border-t border-white/5 py-14">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 mb-12">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-purple to-accent-purple-dark flex items-center justify-center text-sm font-bold text-white">
                A
              </div>
              <span className="font-display font-bold text-text-1 text-lg">Angeleck</span>
            </div>
            <p className="text-text-3 text-sm leading-relaxed max-w-xs">
              Votre organisation IA autonome. 11 agents experts, une mission : faire croître votre
              business.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="text-text-2 font-semibold text-sm mb-4 uppercase tracking-wider">
              Plateforme
            </h4>
            <ul className="flex flex-col gap-2.5">
              {['Vision', 'Agents', 'Architecture', 'Mémoire'].map((l) => (
                <li key={l}>
                  <a
                    href="#"
                    className="text-text-3 text-sm hover:text-text-1 transition-colors"
                  >
                    {l}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Social */}
          <div>
            <h4 className="text-text-2 font-semibold text-sm mb-4 uppercase tracking-wider">
              Communauté
            </h4>
            <div className="flex gap-3">
              {[
                { icon: Twitter, label: 'Twitter' },
                { icon: Github, label: 'Github' },
                { icon: Linkedin, label: 'LinkedIn' },
              ].map(({ icon: Icon, label }) => (
                <a
                  key={label}
                  href="#"
                  aria-label={label}
                  className="w-9 h-9 rounded-xl glass border border-white/6 flex items-center justify-center text-text-3 hover:text-text-1 hover:border-accent-purple/30 transition-all"
                >
                  <Icon size={15} />
                </a>
              ))}
            </div>
          </div>
        </div>

        <div className="border-t border-white/5 pt-6 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-xs text-text-3 font-mono">
            © 2026 Angeleck. Tous droits réservés.
          </p>
          <p className="text-xs text-text-3">
            Propulsé par{' '}
            <span className="text-accent-purple-light">Claude · Anthropic</span>
          </p>
        </div>
      </div>
    </footer>
  );
}

/* ─────────────────────────── Page ─────────────────────────── */

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-bg-1 overflow-x-hidden">
      <Nav />
      <Hero />
      <HowItWorks />
      <AgentsPreview />
      <CtaSection />
      <Footer />
    </div>
  );
}
