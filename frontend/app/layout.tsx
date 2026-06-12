import type { Metadata } from 'next';
import { Inter, Playfair_Display, DM_Mono } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter', display: 'swap' });
const playfair = Playfair_Display({
  subsets: ['latin'],
  weight: ['400', '700', '900'],
  style: ['normal', 'italic'],
  variable: '--font-playfair',
  display: 'swap',
});
const mono = DM_Mono({ subsets: ['latin'], weight: ['400', '500'], variable: '--font-mono', display: 'swap' });

export const metadata: Metadata = {
  title: 'Angeleck — Organisation IA Autonome',
  description: 'Votre équipe d\'experts IA coordonnée par Raphaël. Créez, automatisez et développez vos business digitaux.',
  keywords: ['IA', 'agents', 'business', 'automatisation', 'Raphaël', 'Angeleck'],
};

// Prevent theme flash: set data-theme before first paint (default = light "blanc sale").
const themeInit = `(function(){try{var t=localStorage.getItem('angeleck-theme')||'light';document.documentElement.setAttribute('data-theme',t);}catch(e){document.documentElement.setAttribute('data-theme','light');}})();`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" data-theme="light" className={`${inter.variable} ${playfair.variable} ${mono.variable}`}>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInit }} />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
