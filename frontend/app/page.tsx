'use client';

import { useRef } from 'react';
import Link from 'next/link';
import { motion, useInView } from 'framer-motion';
import AgentAvatarSVG from '@/components/agents/AgentAvatarSVG';
import ThemeToggle from '@/components/theme/ThemeToggle';
import { AGENTS } from '@/lib/data';
import type { Agent } from '@/lib/types';

/* ─────────────────────────── helpers ─────────────────────────── */

function Reveal({
  children,
  delay = 0,
  x = 0,
  className = '',
}: {
  children: React.ReactNode;
  delay?: number;
  x?: number;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: '0px 0px -60px 0px' });
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: x === 0 ? 44 : 0, x }}
      animate={inView ? { opacity: 1, y: 0, x: 0 } : {}}
      transition={{ duration: 0.9, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

const RAPHAEL: Agent = AGENTS[0];
const ORBIT_AGENTS = AGENTS.filter((a) =>
  ['sofia', 'gabriel', 'elena', 'nathan', 'maya', 'lucas'].includes(a.id),
);
const FLOAT_CLASSES = ['av-float-0', 'av-float-1', 'av-float-2', 'av-float-3'];

/* ─────────────────────────── Nav ─────────────────────────── */

const NAV_LINKS = [
  { label: 'Vision', href: '#vision' },
  { label: 'Raphaël', href: '#raphael' },
  { label: 'Agents', href: '#agents' },
  { label: 'Architecture', href: '#architecture' },
  { label: 'Genesis', href: '#genesis' },
  { label: 'Tarifs', href: '#pricing' },
];

function Nav() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-[1000] flex items-center justify-between px-5 sm:px-10 py-[18px] bg-bg-0/[0.88] backdrop-blur-2xl border-b border-line/[0.07]">
      <Link href="/" className="flex items-center gap-2.5">
        <div className="w-[38px] h-[38px] rounded-[11px] flex items-center justify-center font-display text-[17px] font-black text-white shadow-purple"
          style={{ background: 'linear-gradient(135deg, #6B46C1, #2563EB)' }}>
          A
        </div>
        <span className="font-display text-xl font-black tracking-tight text-text-1">Angeleck</span>
      </Link>

      <div className="hidden lg:flex items-center gap-8">
        {NAV_LINKS.map(({ label, href }) => (
          <a key={label} href={href} className="text-sm font-medium text-text-2 hover:text-text-1 transition-colors">
            {label}
          </a>
        ))}
      </div>

      <div className="flex items-center gap-4 sm:gap-5">
        <ThemeToggle />
        <Link
          href="/dashboard"
          className="px-5 py-[9px] rounded-full text-white text-[0.82rem] font-semibold shadow-purple transition-all hover:-translate-y-px"
          style={{ background: '#6B46C1' }}
        >
          Commencer →
        </Link>
      </div>
    </nav>
  );
}

/* ─────────────────────────── Hero ─────────────────────────── */

const ORBIT_POSITIONS = [
  { top: '20px', left: '60px', float: 'av-float-1' },
  { top: '60px', right: '40px', float: 'av-float-2' },
  { bottom: '80px', right: '50px', float: 'av-float-3' },
  { bottom: '60px', left: '50px', float: 'av-float-0' },
  { top: '200px', right: '20px', float: 'av-float-1' },
  { top: '200px', left: '20px', float: 'av-float-2' },
];

function Hero() {
  return (
    <section id="home" className="relative min-h-screen flex items-center pt-[140px] pb-20 overflow-hidden">
      {/* Orbs */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <motion.div
          animate={{ x: [0, 30, 0], y: [0, -40, 0], scale: [1, 1.06, 1] }}
          transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute rounded-full opacity-10 dark:opacity-[0.18]"
          style={{ width: 700, height: 700, top: -200, right: -150, background: '#6B46C1', filter: 'blur(100px)' }}
        />
        <motion.div
          animate={{ x: [0, -30, 0], y: [0, 40, 0], scale: [1, 1.06, 1] }}
          transition={{ duration: 14, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute rounded-full opacity-10 dark:opacity-[0.18]"
          style={{ width: 500, height: 500, bottom: -200, left: -100, background: '#2563EB', filter: 'blur(100px)' }}
        />
        <motion.div
          animate={{ x: [0, 30, 0], y: [0, -40, 0], scale: [1, 1.06, 1] }}
          transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut', delay: 2 }}
          className="absolute rounded-full opacity-10 dark:opacity-[0.18]"
          style={{ width: 350, height: 350, top: '40%', left: '35%', background: '#C9A84C', filter: 'blur(100px)' }}
        />
      </div>

      <div className="relative z-10 w-full max-w-[1240px] mx-auto px-7">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-20 items-center">
          {/* Left */}
          <motion.div
            initial={{ opacity: 0, y: 44 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
          >
            <div className="inline-flex items-center gap-2 glass-md rounded-full px-4 py-[7px] mb-7">
              <span className="w-[7px] h-[7px] rounded-full bg-status-active status-active" />
              <span className="font-mono text-[0.7rem] tracking-[0.12em] uppercase text-text-3">
                Organisation IA Autonome · v1.0
              </span>
            </div>

            <h1 className="font-display font-black leading-[0.97] tracking-[-0.03em] text-[clamp(3rem,7vw,7.5rem)] mb-6 text-text-1">
              Angel<span className="text-gradient">eck</span>
              <br />
              L&apos;Intelligence
              <br />
              <em className="italic">Collective</em>
            </h1>

            <p className="text-[1.15rem] leading-[1.75] max-w-[520px] mb-12 text-text-2">
              Un réseau d&apos;agents IA spécialisés, coordonné par Raphaël, capable de gérer, créer,
              analyser et développer vos business digitaux en totale autonomie.
            </p>

            <div className="flex flex-wrap gap-3.5">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 px-8 py-[15px] rounded-full text-white font-semibold text-[0.92rem] shadow-purple transition-all hover:-translate-y-0.5"
                style={{ background: '#6B46C1' }}
              >
                Rencontrer l&apos;équipe →
              </Link>
              <a
                href="#architecture"
                className="inline-flex items-center gap-2 px-8 py-[15px] rounded-full font-semibold text-[0.92rem] text-text-1 border-2 border-line/[0.12] hover:border-line/30 transition-all hover:-translate-y-0.5"
              >
                Architecture
              </a>
            </div>
          </motion.div>

          {/* Right — Raphaël + orbiting agents */}
          <motion.div
            initial={{ opacity: 0, scale: 0.92 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.9, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
            className="relative h-[520px] hidden lg:flex items-center justify-center"
          >
            {/* Central Raphaël */}
            <div className="relative z-[2] flex flex-col items-center gap-2">
              <div className="av-float-0" style={{ filter: 'drop-shadow(0 20px 40px rgba(107,70,193,.4))' }}>
                <AgentAvatarSVG agent={RAPHAEL} size={130} showBadge={false} />
              </div>
              <div className="font-display font-bold text-[1.1rem] text-text-1">Raphaël</div>
              <div className="font-mono text-[0.68rem] tracking-[0.18em] uppercase text-text-3">
                Orchestrateur Central
              </div>
            </div>

            {/* Orbiting agents */}
            {ORBIT_AGENTS.map((agent, i) => {
              const pos = ORBIT_POSITIONS[i];
              return (
                <div
                  key={agent.id}
                  className={`absolute z-[2] flex flex-col items-center gap-1 ${pos.float}`}
                  style={{ top: pos.top, bottom: pos.bottom, left: pos.left, right: pos.right }}
                >
                  <div
                    className="w-14 h-14 rounded-full glass-md flex items-center justify-center overflow-hidden shadow-card"
                    style={{ borderColor: `${agent.color}4d` }}
                  >
                    <AgentAvatarSVG agent={agent} size={56} showBadge={false} />
                  </div>
                  <div className="text-[0.62rem] font-semibold tracking-wide opacity-70 text-text-1">
                    {agent.name}
                  </div>
                </div>
              );
            })}
          </motion.div>
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────── Manifeste / Vision ─────────────────────────── */

const LOIS = [
  {
    num: '01',
    title: 'Collaboration obligatoire',
    text: 'Aucun agent ne travaille isolément. Chaque mission active la synergie de l\'équipe entière selon les compétences requises.',
  },
  {
    num: '02',
    title: 'Raphaël coordonne',
    text: 'Raphaël reste le chef d\'orchestre incontesté. Il analyse, planifie, délègue, supervise et synthétise chaque résultat.',
  },
  {
    num: '03',
    title: 'Validation humaine',
    text: 'Les décisions importantes — financières, légales, critiques — nécessitent toujours une validation humaine avant exécution.',
  },
  {
    num: '04',
    title: 'Amélioration continue',
    text: 'Chaque mission enrichit Akasha Memory. Angeleck devient plus intelligent et précis avec chaque interaction.',
  },
];

function Manifeste() {
  return (
    <section id="vision" className="py-20 md:py-[130px] bg-bg-1">
      <div className="max-w-[1240px] mx-auto px-7">
        <Reveal>
          <div className="eyebrow mb-[18px]">Manifeste</div>
          <blockquote className="font-display italic leading-[1.55] text-[clamp(1.4rem,2.8vw,2.4rem)] border-l-[3px] pl-9 max-w-[820px] mx-auto mb-20 text-text-1"
            style={{ borderColor: '#6B46C1' }}>
            « Angeleck n&apos;est pas un assistant.
            <br />C&apos;est une organisation digitale autonome
            <br />composée d&apos;experts IA spécialisés. »
          </blockquote>
        </Reveal>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {LOIS.map((loi, i) => (
            <Reveal key={loi.num} delay={i * 0.1}>
              <div className="glass-md rounded-[20px] p-[30px] h-full transition-all duration-300 hover:-translate-y-1.5 hover:shadow-card-hover">
                <div className="font-mono text-[2.5rem] font-medium leading-none mb-2.5" style={{ color: '#6B46C1', opacity: 0.25 }}>
                  {loi.num}
                </div>
                <div className="font-bold text-[0.95rem] mb-1.5 text-text-1">{loi.title}</div>
                <div className="text-[0.83rem] leading-[1.65] text-text-3">{loi.text}</div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────── Raphaël ─────────────────────────── */

const POWERS = [
  {
    icon: '🧠',
    bg: 'rgba(107,70,193,.1)',
    title: 'Diagnostic profond',
    desc: 'Comprend le besoin réel, le contexte, les contraintes et l\'objectif final derrière chaque demande.',
  },
  {
    icon: '🎯',
    bg: 'rgba(37,99,235,.1)',
    title: 'Décomposition en missions',
    desc: 'Transforme une demande vague en missions précises assignées aux bons experts.',
  },
  {
    icon: '⚡',
    bg: 'rgba(201,168,76,.1)',
    title: 'Orchestration temps réel',
    desc: 'Coordonne jusqu\'à 10 agents en parallèle avec suivi et contrôle qualité en continu.',
  },
  {
    icon: '🔄',
    bg: 'rgba(16,185,129,.1)',
    title: 'Synthèse & amélioration',
    desc: 'Vérifie, améliore et assemble les résultats avant livraison. Stocke les apprentissages dans Akasha.',
  },
];

function RaphaelSection() {
  return (
    <section id="raphael" className="py-20 md:py-[130px]">
      <div className="max-w-[1240px] mx-auto px-7">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-[100px] items-center">
          {/* Avatar + rings */}
          <Reveal x={-44} className="flex justify-center">
            <div className="relative w-[320px] h-[320px] flex items-center justify-center">
              {/* Rings */}
              <div className="absolute rounded-full animate-ring-rot" style={{ inset: -60, border: '1px solid rgba(107,70,193,.18)' }}>
                <span className="absolute top-0 left-1/2 w-2.5 h-2.5 rounded-full -translate-x-1/2 -translate-y-1/2"
                  style={{ background: '#6B46C1', boxShadow: '0 0 12px rgba(107,70,193,.6)' }} />
              </div>
              <div className="absolute rounded-full animate-ring-rot" style={{ inset: -100, border: '1px dashed rgba(107,70,193,.1)', animationDuration: '35s', animationDirection: 'reverse' }}>
                <span className="absolute top-0 left-1/2 w-2.5 h-2.5 rounded-full -translate-x-1/2 -translate-y-1/2"
                  style={{ background: '#C9A84C', boxShadow: '0 0 12px rgba(201,168,76,.6)' }} />
              </div>
              <div className="absolute rounded-full animate-ring-rot" style={{ inset: -140, border: '1px solid rgba(201,168,76,.15)', animationDuration: '45s' }}>
                <span className="absolute bottom-0 left-1/2 w-2.5 h-2.5 rounded-full -translate-x-1/2 translate-y-1/2"
                  style={{ background: '#2563EB', boxShadow: '0 0 12px rgba(37,99,235,.6)' }} />
              </div>
              {/* Avatar */}
              <div className="relative z-[2] av-float-0">
                <AgentAvatarSVG agent={RAPHAEL} size={190} showBadge={false} />
              </div>
            </div>
          </Reveal>

          {/* Text + powers */}
          <Reveal x={44}>
            <div className="eyebrow mb-[18px]">Agent Central</div>
            <h2 className="font-display font-bold leading-[1.1] tracking-[-0.02em] text-[clamp(2.2rem,4vw,4.2rem)] mb-4 text-text-1">
              Raphaël
              <br />
              <span className="italic text-text-3" style={{ fontSize: '70%' }}>Directeur Intelligence</span>
            </h2>
            <p className="mb-9 text-text-2 leading-[1.78]">
              Consultant IA stratégique, chef d&apos;orchestre numérique et coordinateur de l&apos;organisation.
              Sa mission : transformer vos intentions en résultats concrets en mobilisant les bonnes ressources au bon moment.
            </p>

            <div className="flex flex-col gap-3.5">
              {POWERS.map((p) => (
                <div key={p.title} className="flex items-start gap-3.5 px-5 py-4 rounded-2xl glass-md transition-transform duration-200 hover:translate-x-1.5">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center text-[18px] flex-shrink-0" style={{ background: p.bg }}>
                    {p.icon}
                  </div>
                  <div>
                    <div className="text-[0.88rem] font-bold mb-[3px] text-text-1">{p.title}</div>
                    <div className="text-[0.78rem] leading-[1.55] text-text-3">{p.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────── Agents ─────────────────────────── */

function AgentsSection() {
  return (
    <section id="agents" className="py-20 md:py-[130px] bg-bg-1">
      <div className="max-w-[1240px] mx-auto px-7">
        <Reveal className="max-w-[640px] mb-[70px]">
          <div className="eyebrow mb-[18px]">Conseil des Experts</div>
          <h2 className="font-display font-bold leading-[1.1] tracking-[-0.02em] text-[clamp(2.2rem,4vw,4.2rem)] text-text-1">
            11 spécialistes
            <br />à votre service
          </h2>
          <p className="mt-4 text-text-2 leading-[1.78]">
            Chaque agent possède une identité propre, une expertise profonde et des outils spécifiques.
            Ensemble, ils forment une organisation digitale sans précédent.
          </p>
        </Reveal>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 xl:grid-cols-6 gap-[22px]">
          {AGENTS.map((agent, i) => (
            <Reveal key={agent.id} delay={(i % 6) * 0.07}>
              <div
                className="group relative glass-md rounded-3xl px-[18px] pt-7 pb-[22px] text-center cursor-pointer overflow-hidden transition-all duration-300 hover:-translate-y-2.5"
                style={{ ['--agent-color' as string]: agent.color }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = `${agent.color}40`;
                  e.currentTarget.style.boxShadow = `0 24px 60px ${agent.color}18`;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = '';
                  e.currentTarget.style.boxShadow = '';
                }}
              >
                <span className="absolute top-3.5 right-3.5 w-2 h-2 rounded-full bg-status-active status-active" />

                <div className="relative w-[90px] h-[90px] mx-auto mb-4">
                  <div className={FLOAT_CLASSES[i % 4]}>
                    <AgentAvatarSVG agent={agent} size={88} />
                  </div>
                  <div
                    className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-[50px] h-2.5 rounded-full blur-[8px] opacity-50"
                    style={{ background: agent.color }}
                  />
                </div>

                <div className="font-display text-[1.15rem] font-bold mb-[3px] text-text-1">{agent.name}</div>
                <div className="font-mono text-[0.62rem] tracking-[0.12em] uppercase opacity-45 mb-3 text-text-1">
                  {agent.role}
                </div>
                <div className="flex flex-wrap gap-1 justify-center">
                  {agent.skills.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="text-[0.62rem] px-2 py-[3px] rounded-full bg-bg-3 text-text-3 border border-line/[0.07]"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────── How it works ─────────────────────────── */

const STEPS = [
  {
    num: '01',
    icon: '🔍',
    title: 'Étape 1 — Compréhension',
    desc: 'Raphaël analyse la demande en profondeur : ce qui est dit, ce qui est voulu, les contraintes cachées et l\'objectif final réel.',
  },
  {
    num: '02',
    icon: '🗺️',
    title: 'Étape 2 — Mission structurée',
    desc: 'La demande est transformée en plan d\'action précis : objectifs clairs, compétences identifiées, agents sélectionnés.',
  },
  {
    num: '03',
    icon: '⚡',
    title: 'Étape 3 — Activation des experts',
    desc: 'Les agents spécialisés sont mobilisés simultanément. Chacun reçoit une fiche de mission précise avec contexte, tâche et contraintes.',
  },
  {
    num: '04',
    icon: '🤝',
    title: 'Étape 4 — Collaboration',
    desc: 'Les agents travaillent en réseau, s\'alimentent mutuellement. Sofia informe Maya, Emma éclaire Adam, Elena guide Nathan.',
  },
  {
    num: '05',
    icon: '✨',
    title: 'Étape 5 — Livraison premium',
    desc: 'Raphaël contrôle, améliore et assemble. Le résultat final est vérifié, optimisé et présenté de façon claire et exploitable.',
  },
];

function HowItWorks() {
  return (
    <section id="how" className="py-20 md:py-[130px]">
      <div className="max-w-[1240px] mx-auto px-7">
        <Reveal className="max-w-[580px] mb-20">
          <div className="eyebrow mb-[18px]">Processus</div>
          <h2 className="font-display font-bold leading-[1.1] tracking-[-0.02em] text-[clamp(2.2rem,4vw,4.2rem)] text-text-1">
            5 étapes vers le résultat
          </h2>
          <p className="mt-4 text-text-2 leading-[1.78]">
            Chaque demande déclenche un protocole structuré. De l&apos;analyse à la livraison, Angeleck
            opère comme une équipe professionnelle rodée.
          </p>
        </Reveal>

        <div className="relative">
          {/* Central vertical line */}
          <div
            className="absolute top-10 bottom-10 w-px left-[28px] md:left-1/2 md:-translate-x-1/2"
            style={{ background: 'linear-gradient(to bottom, transparent, #6B46C1 20%, #6B46C1 80%, transparent)' }}
          />

          <div className="flex flex-col gap-10">
            {STEPS.map((step, i) => {
              const isLeft = i % 2 === 0;
              return (
                <Reveal key={step.num} delay={i * 0.1}>
                  <div className="grid items-center gap-0 grid-cols-[56px_1fr] md:grid-cols-[1fr_80px_1fr]">
                    {/* Content */}
                    <div className={`${isLeft ? 'md:order-1 col-start-2 md:col-start-auto' : 'md:order-3 col-start-2 md:col-start-auto'}`}>
                      <div className="glass-md rounded-[18px] p-[26px]">
                        <span className="text-[1.8rem] mb-2.5 block">{step.icon}</span>
                        <div className="font-bold text-base mb-1.5 text-text-1">{step.title}</div>
                        <div className="text-[0.83rem] leading-[1.65] text-text-2">{step.desc}</div>
                      </div>
                    </div>
                    {/* Node */}
                    <div className="order-first md:order-2 row-start-1 col-start-1 md:col-start-auto flex justify-center">
                      <div
                        className="w-[52px] h-[52px] rounded-full flex items-center justify-center font-mono text-[0.9rem] font-medium relative z-[2] bg-bg-0"
                        style={{ border: '2px solid #6B46C1', color: '#6B46C1', boxShadow: '0 0 0 6px rgb(var(--bg-0))' }}
                      >
                        {step.num}
                      </div>
                    </div>
                    {/* Empty (desktop balance) */}
                    <div className={`hidden md:block ${isLeft ? 'md:order-3' : 'md:order-1'}`} />
                  </div>
                </Reveal>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────── Architecture ─────────────────────────── */

const TECH_CARDS = [
  {
    cat: 'Cerveau IA',
    items: [
      { dot: '#6B46C1', label: 'Claude API (Anthropic)' },
      { dot: '#2563EB', label: 'LangGraph (Orchestration)' },
      { dot: '#10B981', label: 'LangChain (Agents)' },
    ],
  },
  {
    cat: 'Backend',
    items: [
      { dot: '#F59E0B', label: 'Python 3.12' },
      { dot: '#EF4444', label: 'FastAPI' },
      { dot: '#8B5CF6', label: 'WebSocket (Streaming)' },
    ],
  },
  {
    cat: 'Mémoire',
    items: [
      { dot: '#2563EB', label: 'PostgreSQL' },
      { dot: '#10B981', label: 'Weaviate (Vecteurs)' },
      { dot: '#F97316', label: 'Redis (Cache)' },
    ],
  },
  {
    cat: 'Frontend',
    items: [
      { dot: '#1F2937', label: 'Next.js 14' },
      { dot: '#06B6D4', label: 'Tailwind CSS' },
      { dot: '#7C3AED', label: 'Framer Motion' },
    ],
  },
  {
    cat: 'Automatisation',
    items: [
      { dot: '#EF4444', label: 'n8n (Workflows)' },
      { dot: '#10B981', label: 'Shopify API' },
      { dot: '#3B82F6', label: 'Meta Ads API' },
    ],
  },
  {
    cat: 'Infrastructure',
    items: [
      { dot: '#F59E0B', label: 'AWS / GCP' },
      { dot: '#8B5CF6', label: 'Docker + K8s' },
      { dot: '#10B981', label: 'Cloudflare CDN' },
    ],
  },
];

const FLOW = [
  { label: 'Utilisateur', bg: 'rgba(107,70,193,.12)', color: '#6B46C1', border: 'rgba(107,70,193,.2)' },
  { label: 'Raphaël', bg: 'rgba(107,70,193,.2)', color: '#6B46C1', border: 'rgba(107,70,193,.3)' },
  { label: 'LangGraph Router', bg: 'rgb(var(--bg-3))', color: 'rgb(var(--text-1))', border: 'rgba(127,127,127,.2)' },
  { label: 'Agents (×n)', bg: 'rgba(37,99,235,.1)', color: '#2563EB', border: 'rgba(37,99,235,.2)' },
  { label: 'Akasha Memory', bg: 'rgba(16,185,129,.1)', color: '#10B981', border: 'rgba(16,185,129,.2)' },
  { label: 'Résultat ✓', bg: 'rgba(201,168,76,.15)', color: '#C9A84C', border: 'rgba(201,168,76,.3)' },
];

function Architecture() {
  return (
    <section id="architecture" className="py-20 md:py-[130px] bg-bg-1">
      <div className="max-w-[1240px] mx-auto px-7">
        <Reveal>
          <div className="eyebrow mb-[18px]">Architecture Technique</div>
          <h2 className="font-display font-bold leading-[1.1] tracking-[-0.02em] text-[clamp(2.2rem,4vw,4.2rem)] mb-4 text-text-1">
            Stack de niveau
            <br />production
          </h2>
          <p className="max-w-[580px] text-text-2 leading-[1.78]">
            Angeleck repose sur les technologies les plus avancées, conçues pour évoluer de quelques
            utilisateurs à des millions.
          </p>
        </Reveal>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-[18px] mt-[60px]">
          {TECH_CARDS.map((card, i) => (
            <Reveal key={card.cat} delay={(i % 6) * 0.1}>
              <div className="glass-md rounded-[18px] p-6 h-full">
                <div className="font-mono text-[0.62rem] tracking-[0.18em] uppercase text-text-3 mb-3.5">
                  {card.cat}
                </div>
                <div className="flex flex-col gap-2">
                  {card.items.map((it) => (
                    <div
                      key={it.label}
                      className="flex items-center gap-2.5 px-3 py-2 rounded-[10px] bg-bg-0 border border-line/[0.07] text-[0.82rem] font-medium text-text-1 transition-colors hover:border-accent-purple/60"
                    >
                      <span className="w-[7px] h-[7px] rounded-full flex-shrink-0" style={{ background: it.dot }} />
                      {it.label}
                    </div>
                  ))}
                </div>
              </div>
            </Reveal>
          ))}
        </div>

        {/* Data flow */}
        <Reveal>
          <div className="mt-12 glass-md rounded-3xl p-10 text-center">
            <div className="font-mono text-[0.68rem] tracking-[0.18em] uppercase text-text-3 mb-5">
              Flux de données
            </div>
            <div className="flex items-center justify-center flex-wrap gap-y-2">
              {FLOW.map((node, i) => (
                <span key={node.label} className="flex items-center">
                  <span
                    className="px-5 py-2.5 rounded-full text-[0.85rem] font-semibold whitespace-nowrap"
                    style={{ background: node.bg, color: node.color, border: `1px solid ${node.border}` }}
                  >
                    {node.label}
                  </span>
                  {i < FLOW.length - 1 && <span className="text-text-3 text-[1.2rem] px-2">→</span>}
                </span>
              ))}
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}

/* ─────────────────────────── Genesis ─────────────────────────── */

const GEN_STEPS = [
  { num: '1', strong: 'Détection du manque', text: ' — Raphaël identifie qu\'aucun agent existant ne couvre la compétence requise.' },
  { num: '2', strong: 'Définition du rôle', text: ' — Genesis spécifie la fonction, les compétences, la personnalité et les outils du nouvel expert.' },
  { num: '3', strong: 'Attribution d\'identité', text: ' — Un prénom humain, une personnalité professionnelle et un domaine précis sont assignés.' },
  { num: '4', strong: 'Validation humaine', text: ' — Le nouvel agent est présenté à l\'utilisateur pour approbation avant intégration.' },
  { num: '5', strong: 'Intégration réseau', text: ' — L\'agent rejoint l\'organigramme, la mémoire Akasha et le routeur de compétences.' },
];

function Genesis() {
  return (
    <section id="genesis" className="py-20 md:py-[130px]">
      <div className="max-w-[1240px] mx-auto px-7">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-20 items-start">
          {/* Left — steps */}
          <Reveal x={-44}>
            <div className="eyebrow mb-[18px]">Genesis Engine</div>
            <h2 className="font-display font-bold leading-[1.1] tracking-[-0.02em] text-[clamp(2.2rem,4vw,4.2rem)] mb-4 text-text-1">
              Le créateur
              <br />d&apos;experts IA
            </h2>
            <p className="mb-9 text-text-2 leading-[1.78]">
              Quand une compétence manque, Genesis entre en action. Il conçoit, configure et intègre
              automatiquement un nouvel agent spécialisé dans le réseau Angeleck.
            </p>

            <div className="flex flex-col gap-3.5">
              {GEN_STEPS.map((s) => (
                <div key={s.num} className="flex gap-3.5 items-start px-[18px] py-4 rounded-2xl glass-md transition-transform duration-200 hover:translate-x-1">
                  <div className="w-[30px] h-[30px] rounded-lg flex-shrink-0 flex items-center justify-center text-white font-mono text-[0.78rem] font-medium" style={{ background: '#6B46C1' }}>
                    {s.num}
                  </div>
                  <div className="text-[0.84rem] leading-[1.65] text-text-2">
                    <strong className="text-text-1">{s.strong}</strong>{s.text}
                  </div>
                </div>
              ))}
            </div>
          </Reveal>

          {/* Right — example */}
          <Reveal x={44}>
            <div className="font-mono text-[0.68rem] tracking-[0.18em] uppercase text-text-3 mb-4">
              Exemple en temps réel
            </div>
            <div className="rounded-[20px] p-8 font-mono text-[0.78rem] leading-[1.9] text-text-2 bg-bg-4 border border-line/[0.07]">
              <span className="text-text-3">{'// Demande utilisateur'}</span><br />
              <span style={{ color: '#6B46C1', fontWeight: 500 }}>User:</span> &quot;Analyse mon portefeuille crypto avec gestion du risque DeFi&quot;<br /><br />
              <span className="text-text-3">{'// Raphaël analyse'}</span><br />
              <span style={{ color: '#6B46C1', fontWeight: 500 }}>Raphaël:</span> Agent Finance insuffisant.<br />
              → Compétence absente: <strong className="text-text-1">DeFi + Risk</strong><br /><br />
              <span className="text-text-3">{'// Genesis crée'}</span><br />
              <span style={{ color: '#6B46C1', fontWeight: 500 }}>Genesis:</span> {'{'}<br />
              &nbsp;&nbsp;&quot;name&quot;: &quot;<strong className="text-text-1">Victor</strong>&quot;,<br />
              &nbsp;&nbsp;&quot;role&quot;: &quot;Expert Crypto &amp; DeFi&quot;,<br />
              &nbsp;&nbsp;&quot;skills&quot;: [&quot;DeFi&quot;, &quot;Risk Mgmt&quot;, &quot;on-chain&quot;],<br />
              &nbsp;&nbsp;&quot;tools&quot;: [&quot;Dune Analytics&quot;, &quot;DefiLlama&quot;],<br />
              &nbsp;&nbsp;&quot;personality&quot;: &quot;analytique, prudent&quot;<br />
              {'}'}<br /><br />
              <span className="text-text-3">{'// Validation requise'}</span><br />
              <span style={{ color: '#6B46C1', fontWeight: 500 }}>Raphaël →</span> &quot;Souhaitez-vous intégrer Victor ?&quot;<br />
              <span style={{ color: '#6B46C1', fontWeight: 500 }}>User →</span> &quot;Oui&quot;<br />
              <span style={{ color: '#6B46C1', fontWeight: 500 }}>✓</span> Victor rejoint Angeleck.
            </div>

            <div className="mt-6 px-6 py-5 rounded-2xl" style={{ background: 'rgba(107,70,193,.06)', border: '1px solid rgba(107,70,193,.15)' }}>
              <div className="font-bold text-[0.9rem] mb-2" style={{ color: '#6B46C1' }}>Potentiel d&apos;évolution</div>
              <div className="text-[0.83rem] leading-[1.7] text-text-2">
                10 agents → 50 agents → 500 experts spécialisés.<br />
                Chaque nouvel agent enrichit l&apos;intelligence collective d&apos;Angeleck.
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────── Akasha Memory ─────────────────────────── */

const MEMORIES = [
  {
    icon: '👤',
    color: '#6B46C1',
    title: 'Mémoire Utilisateur',
    desc: 'Préférences, habitudes de travail et objectifs personnels mémorisés pour des réponses toujours plus adaptées.',
    items: ['Préférences de style', 'Secteur d\'activité', 'Objectifs business'],
  },
  {
    icon: '📁',
    color: '#2563EB',
    title: 'Mémoire Projet',
    desc: 'Chaque projet est archivé avec ses objectifs, décisions, stratégies et résultats pour continuité parfaite.',
    items: ['Décisions prises', 'Fichiers & livrables', 'Résultats mesurés'],
  },
  {
    icon: '💡',
    color: '#10B981',
    title: 'Mémoire Métier',
    desc: 'Méthodes qui fonctionnent, bonnes pratiques sectorielles et stratégies validées sur des centaines de missions.',
    items: ['Méthodes efficaces', 'Bonnes pratiques', 'Stratégies prouvées'],
  },
  {
    icon: '🧬',
    color: '#C9A84C',
    title: 'Mémoire Évolution',
    desc: 'Nouveaux agents créés, améliorations appliquées et erreurs corrigées — l\'ADN évolutif d\'Angeleck.',
    items: ['Agents créés', 'Améliorations', 'Erreurs corrigées'],
  },
];

function Akasha() {
  return (
    <section id="akasha" className="py-20 md:py-[130px] bg-bg-1">
      <div className="max-w-[1240px] mx-auto px-7">
        <Reveal className="max-w-[640px]">
          <div className="eyebrow mb-[18px]">Akasha Memory System</div>
          <h2 className="font-display font-bold leading-[1.1] tracking-[-0.02em] text-[clamp(2.2rem,4vw,4.2rem)] text-text-1">
            La mémoire
            <br />vivante d&apos;Angeleck
          </h2>
          <p className="mt-4 text-text-2 leading-[1.78]">
            Akasha n&apos;est pas un simple historique. C&apos;est la connaissance accumulée de
            l&apos;organisation — Angeleck apprend de chaque interaction et devient plus efficace avec
            l&apos;expérience.
          </p>
        </Reveal>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mt-[60px]">
          {MEMORIES.map((mem, i) => (
            <Reveal key={mem.title} delay={i * 0.1}>
              <div
                className="relative rounded-[22px] p-[30px] glass-md h-full overflow-hidden transition-transform duration-300 hover:-translate-y-1.5"
                style={{ borderColor: `${mem.color}26`, color: mem.color }}
              >
                <span className="text-[2rem] mb-4 block">{mem.icon}</span>
                <div className="font-bold text-base mb-2 text-text-1">{mem.title}</div>
                <div className="text-[0.82rem] leading-[1.65] text-text-2 mb-3.5">{mem.desc}</div>
                <div className="flex flex-col gap-[5px]">
                  {mem.items.map((it) => (
                    <div key={it} className="text-[0.75rem] text-text-3 flex items-center gap-1.5">
                      <span className="opacity-50">→</span>
                      {it}
                    </div>
                  ))}
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────── Pricing ─────────────────────────── */

const TIERS = [
  {
    tier: 'Démarrage',
    name: 'Explorer',
    amount: '0',
    sup: '€',
    sub: '/mois',
    period: 'Gratuit pour toujours',
    cta: 'Commencer gratuitement',
    featured: false,
    feats: [
      { label: 'Raphaël + 3 agents', on: true },
      { label: '50 missions/mois', on: true },
      { label: 'Mémoire basique', on: true },
      { label: 'Interface chat', on: true },
      { label: 'Agents avancés', on: false },
      { label: 'Genesis Engine', on: false },
    ],
  },
  {
    tier: 'Croissance',
    name: 'Pro',
    amount: '79',
    sup: '€',
    sub: '/mois',
    period: 'Facturation mensuelle',
    cta: 'Démarrer Pro →',
    featured: true,
    badge: 'Le plus populaire',
    feats: [
      { label: 'Tous les 11 agents', on: true },
      { label: 'Missions illimitées', on: true },
      { label: 'Akasha Memory complète', on: true },
      { label: 'Outils externes (Shopify, Meta)', on: true },
      { label: 'Genesis (5 agents custom)', on: true },
      { label: 'Tableau de bord avancé', on: true },
    ],
  },
  {
    tier: 'Organisation',
    name: 'Enterprise',
    amount: 'Sur mesure',
    period: 'Tarif personnalisé',
    cta: 'Contacter l\'équipe',
    featured: false,
    feats: [
      { label: 'Agents illimités', on: true },
      { label: 'Genesis sans limites', on: true },
      { label: 'Intégrations API totales', on: true },
      { label: 'Déploiement privé', on: true },
      { label: 'Support dédié 24/7', on: true },
      { label: 'SLA garanti', on: true },
    ],
  },
];

function Pricing() {
  return (
    <section id="pricing" className="py-20 md:py-[130px]">
      <div className="max-w-[1240px] mx-auto px-7">
        <Reveal className="text-center">
          <div className="eyebrow justify-center mb-[18px]" style={{ display: 'inline-flex' }}>Business Model</div>
          <h2 className="font-display font-bold leading-[1.1] tracking-[-0.02em] text-[clamp(2.2rem,4vw,4.2rem)] text-text-1">
            Choisissez votre
            <br />niveau d&apos;intelligence
          </h2>
          <p className="max-w-[520px] mx-auto mt-4 text-text-2 leading-[1.78]">
            De l&apos;entrepreneur solo à l&apos;entreprise internationale, Angeleck s&apos;adapte à votre ambition.
          </p>
        </Reveal>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-[22px] mt-[70px]">
          {TIERS.map((tier, i) => (
            <Reveal key={tier.name} delay={i * 0.1}>
              <div
                className={`relative rounded-[26px] p-[38px] h-full transition-all duration-300 hover:-translate-y-2 hover:shadow-card-hover ${
                  tier.featured ? '' : 'glass-md'
                }`}
                style={
                  tier.featured
                    ? {
                        border: '1px solid #6B46C1',
                        background: 'linear-gradient(160deg, rgba(107,70,193,.06), rgba(37,99,235,.04))',
                      }
                    : undefined
                }
              >
                {tier.featured && tier.badge && (
                  <div className="absolute -top-[13px] left-1/2 -translate-x-1/2 text-white font-mono text-[0.65rem] font-medium px-[18px] py-[5px] rounded-full tracking-[0.1em] uppercase whitespace-nowrap" style={{ background: '#6B46C1' }}>
                    {tier.badge}
                  </div>
                )}

                <div className="font-mono text-[0.65rem] tracking-[0.18em] uppercase text-text-3 mb-3">
                  {tier.tier}
                </div>
                <div className="font-display text-[1.7rem] font-bold mb-5 text-text-1">{tier.name}</div>

                <div className="text-[2.8rem] font-extrabold leading-none mb-1.5 text-text-1">
                  {tier.sup && <sup className="text-[1.3rem] align-top mt-2 inline-block font-normal opacity-60">{tier.sup}</sup>}
                  {tier.amount}
                  {tier.sub && <sub className="text-[0.9rem] font-normal opacity-50">{tier.sub}</sub>}
                </div>
                <div className="text-[0.82rem] text-text-3 mb-7">{tier.period}</div>

                <div className="flex flex-col gap-3 mb-8">
                  {tier.feats.map((f) => (
                    <div key={f.label} className={`flex items-center gap-2.5 text-[0.85rem] text-text-1 ${f.on ? '' : 'opacity-40'}`}>
                      <span
                        className="w-5 h-5 rounded-full flex-shrink-0 flex items-center justify-center text-[0.65rem]"
                        style={
                          f.on
                            ? { background: 'rgba(16,185,129,.1)', border: '1px solid rgba(16,185,129,.3)', color: '#10B981' }
                            : { border: '1px solid rgba(127,127,127,.2)', color: 'rgb(var(--text-3))' }
                        }
                      >
                        {f.on ? '✓' : '—'}
                      </span>
                      {f.label}
                    </div>
                  ))}
                </div>

                <Link
                  href="/dashboard"
                  className={`block w-full text-center py-3.5 rounded-full text-[0.88rem] font-semibold transition-all ${
                    tier.featured
                      ? 'text-white shadow-purple'
                      : 'text-text-1 border-2 border-line/[0.12] hover:border-line/30'
                  }`}
                  style={tier.featured ? { background: '#6B46C1', border: '2px solid #6B46C1' } : undefined}
                >
                  {tier.cta}
                </Link>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────── CTA ─────────────────────────── */

function CtaSection() {
  return (
    <section id="cta" className="relative py-40 text-center overflow-hidden">
      <div
        className="absolute inset-0 z-0 pointer-events-none"
        style={{ background: 'radial-gradient(ellipse at center, rgba(107,70,193,.08) 0%, transparent 70%)' }}
      />
      <div className="relative z-10 max-w-[1240px] mx-auto px-7">
        <Reveal>
          <div className="border-glow rounded-3xl inline-block w-full">
            <div className="rounded-3xl bg-bg-2 px-7 py-16 md:px-16">
              <div className="eyebrow justify-center mb-[18px]" style={{ display: 'inline-flex' }}>
                Commencer maintenant
              </div>
              <h2 className="font-display font-bold leading-[1.1] tracking-[-0.02em] text-[clamp(2.2rem,4vw,4.2rem)] mb-5 text-text-1">
                Prêt à créer votre
                <br />
                <span className="text-gradient">organisation IA ?</span>
              </h2>
              <p className="text-[1.1rem] mb-12 max-w-[520px] mx-auto text-text-2 leading-[1.78]">
                Rejoignez les entrepreneurs qui ont déjà confié leur business digital à Angeleck.
                Votre équipe d&apos;experts IA vous attend.
              </p>
              <div className="flex flex-wrap gap-3.5 justify-center">
                <Link
                  href="/dashboard"
                  className="inline-flex items-center gap-2 px-10 py-[18px] rounded-full text-white font-semibold text-base shadow-purple-lg transition-all hover:-translate-y-0.5"
                  style={{ background: '#6B46C1' }}
                >
                  Démarrer avec Raphaël →
                </Link>
                <a
                  href="#architecture"
                  className="inline-flex items-center gap-2 px-10 py-[18px] rounded-full font-semibold text-base text-text-1 border-2 border-line/[0.12] hover:border-line/30 transition-all hover:-translate-y-0.5"
                >
                  Voir l&apos;architecture
                </a>
              </div>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}

/* ─────────────────────────── Footer ─────────────────────────── */

const FOOTER_COLS = [
  {
    title: 'Système',
    links: [
      { label: 'Raphaël', href: '#raphael' },
      { label: 'Les Agents', href: '#agents' },
      { label: 'Genesis Engine', href: '#genesis' },
      { label: 'Akasha Memory', href: '#akasha' },
    ],
  },
  {
    title: 'Architecture',
    links: [
      { label: 'Stack technique', href: '#architecture' },
      { label: 'Processus', href: '#how' },
      { label: 'Tarifs', href: '#pricing' },
      { label: 'Documentation', href: '#' },
    ],
  },
  {
    title: 'Contact',
    links: [
      { label: 'hello@angeleck.ai', href: '#' },
      { label: 'Twitter / X', href: '#' },
      { label: 'LinkedIn', href: '#' },
      { label: 'GitHub', href: '#' },
    ],
  },
];

function Footer() {
  return (
    <footer className="bg-bg-1 border-t border-line/[0.07] pt-[70px] pb-9">
      <div className="max-w-[1240px] mx-auto px-7">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-[2fr_1fr_1fr_1fr] gap-9 lg:gap-12 mb-[60px]">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="w-[38px] h-[38px] rounded-[11px] flex items-center justify-center font-display text-[17px] font-black text-white"
                style={{ background: 'linear-gradient(135deg, #6B46C1, #2563EB)' }}>
                A
              </div>
              <span className="font-display text-xl font-black text-text-1">Angeleck</span>
            </div>
            <p className="text-[0.85rem] text-text-3 leading-[1.7] max-w-[260px] mt-3.5">
              Organisation IA autonome pour la création, la gestion et l&apos;automatisation de business
              digitaux. Coordonnée par Raphaël.
            </p>
          </div>

          {FOOTER_COLS.map((col) => (
            <div key={col.title}>
              <div className="text-[0.8rem] font-bold tracking-[0.1em] uppercase mb-[18px] text-text-1">
                {col.title}
              </div>
              <div className="flex flex-col gap-2.5">
                {col.links.map((l) => (
                  <a key={l.label} href={l.href} className="text-[0.84rem] text-text-3 hover:text-text-1 transition-colors">
                    {l.label}
                  </a>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="border-t border-line/[0.07] pt-6 flex justify-between items-center flex-wrap gap-3">
          <p className="text-[0.78rem] text-text-3">© 2026 Angeleck. Tous droits réservés.</p>
          <div className="inline-flex items-center gap-1.5 font-mono text-[0.65rem] tracking-[0.1em] text-text-3 px-3 py-[5px] rounded-full border border-line/[0.07]">
            <span>⚡</span>
            <span>Propulsé par Genesis Engine v1.0</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

/* ─────────────────────────── Page ─────────────────────────── */

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-bg-0 overflow-x-hidden">
      <Nav />
      <Hero />
      <Manifeste />
      <RaphaelSection />
      <AgentsSection />
      <HowItWorks />
      <Architecture />
      <Genesis />
      <Akasha />
      <Pricing />
      <CtaSection />
      <Footer />
    </div>
  );
}
