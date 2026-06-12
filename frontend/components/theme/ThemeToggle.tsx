'use client';
import { useEffect, useState } from 'react';
import { Moon, Sun } from 'lucide-react';

type Theme = 'light' | 'dark';

export default function ThemeToggle({ className = '' }: { className?: string }) {
  const [theme, setTheme] = useState<Theme>('light');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const saved = (localStorage.getItem('angeleck-theme') as Theme) || 'light';
    setTheme(saved);
    document.documentElement.setAttribute('data-theme', saved);
    setMounted(true);
  }, []);

  const toggle = () => {
    const next: Theme = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('angeleck-theme', next); } catch { /* ignore */ }
  };

  return (
    <button
      onClick={toggle}
      aria-label="Basculer le thème"
      className={`relative w-11 h-6 rounded-full border border-line/20 bg-bg-3 transition-colors flex items-center ${className}`}
    >
      <span
        className="absolute top-[3px] left-[3px] w-3.5 h-3.5 rounded-full flex items-center justify-center transition-transform duration-300"
        style={{
          transform: mounted && theme === 'dark' ? 'translateX(20px)' : 'translateX(0)',
          background: theme === 'dark' ? '#C9A84C' : '#4A4A4A',
        }}
      >
        {theme === 'dark'
          ? <Moon size={9} className="text-bg-0" />
          : <Sun size={9} className="text-white" />}
      </span>
    </button>
  );
}
