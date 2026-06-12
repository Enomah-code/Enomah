'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  MessageSquare, FolderKanban, Users, Brain, Zap, Settings,
  ChevronLeft, ChevronRight, Activity
} from 'lucide-react';
import { NETWORK_STATS } from '@/lib/data';
import { useState } from 'react';

const NAV = [
  { href: '/dashboard', icon: MessageSquare, label: 'Conversation', desc: 'Chat avec Raphaël' },
  { href: '/projects', icon: FolderKanban, label: 'Projets', desc: 'Gestion des missions' },
  { href: '/agents', icon: Users, label: 'Agents', desc: 'L\'équipe IA' },
  { href: '/memory', icon: Brain, label: 'Mémoire Akasha', desc: 'Intelligence accumulée' },
  { href: '/dashboard#automation', icon: Zap, label: 'Automatisation', desc: 'Workflows & outils' },
  { href: '/dashboard#settings', icon: Settings, label: 'Paramètres', desc: 'Configuration' },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? 68 : 240 }}
      transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
      className="flex flex-col h-full bg-bg-2 border-r border-white/5 relative z-10 overflow-hidden flex-shrink-0"
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-white/5">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-accent-purple to-accent-purple-dark flex items-center justify-center flex-shrink-0 shadow-purple">
          <span className="font-display font-black text-white text-base">A</span>
        </div>
        {!collapsed && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}>
            <div className="font-display font-bold text-text-1 text-sm leading-tight">Angeleck</div>
            <div className="text-text-3 text-xs font-mono">v1.0 · Opérationnel</div>
          </motion.div>
        )}
      </div>

      {/* Network status */}
      {!collapsed && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="px-3 py-3 border-b border-white/5">
          <div className="rounded-xl bg-bg-3 border border-white/5 p-3">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-status-active status-active" />
              <span className="text-xs text-text-2 font-medium">Réseau actif</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <div className="text-lg font-bold text-accent-purple">{NETWORK_STATS.activeAgents}</div>
                <div className="text-xs text-text-3">agents actifs</div>
              </div>
              <div>
                <div className="text-lg font-bold text-accent-gold">{NETWORK_STATS.successRate}%</div>
                <div className="text-xs text-text-3">succès</div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Navigation */}
      <nav className="flex-1 p-2 overflow-y-auto">
        {!collapsed && (
          <div className="px-2 py-1 mb-1">
            <span className="text-xs font-mono text-text-3 uppercase tracking-widest">Menu</span>
          </div>
        )}
        <div className="flex flex-col gap-1">
          {NAV.map(({ href, icon: Icon, label, desc }) => {
            const active = pathname === href || (href !== '/dashboard' && pathname?.startsWith(href.split('#')[0]));
            return (
              <Link key={href} href={href}>
                <motion.div
                  whileHover={{ x: 2 }}
                  className={`flex items-center gap-3 rounded-xl px-3 py-2.5 transition-all cursor-pointer group ${
                    active
                      ? 'nav-link-active'
                      : 'text-text-2 hover:bg-white/5 hover:text-text-1'
                  }`}
                >
                  <Icon size={16} className={`flex-shrink-0 ${active ? 'text-accent-purple-light' : 'text-text-3 group-hover:text-text-2'}`} />
                  {!collapsed && (
                    <div className="min-w-0">
                      <div className={`text-sm font-medium truncate ${active ? 'text-accent-purple-light' : ''}`}>{label}</div>
                      <div className="text-xs text-text-3 truncate hidden group-hover:block">{desc}</div>
                    </div>
                  )}
                </motion.div>
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Bottom: Raphaël avatar */}
      {!collapsed && (
        <div className="p-3 border-t border-white/5">
          <div className="flex items-center gap-3 px-2 py-2 rounded-xl bg-bg-3">
            <div className="relative flex-shrink-0">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-purple-900 flex items-center justify-center text-sm">🧠</div>
              <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-status-active border-2 border-bg-3" />
            </div>
            <div className="min-w-0">
              <div className="text-sm font-semibold text-text-1 truncate">Raphaël</div>
              <div className="text-xs text-text-3">En ligne · prêt</div>
            </div>
            <Activity size={12} className="text-status-active flex-shrink-0 ml-auto" />
          </div>
        </div>
      )}

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute top-4 -right-3 w-6 h-6 rounded-full bg-bg-3 border border-white/10 flex items-center justify-center text-text-3 hover:text-text-1 hover:bg-bg-4 transition-colors z-10"
      >
        {collapsed ? <ChevronRight size={12} /> : <ChevronLeft size={12} />}
      </button>
    </motion.aside>
  );
}
