import type { Metadata } from 'next';
import { Inter, Playfair_Display, JetBrains_Mono } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter', display: 'swap' });
const playfair = Playfair_Display({ subsets: ['latin'], variable: '--font-playfair', display: 'swap' });
const mono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono', display: 'swap' });

export const metadata: Metadata = {
  title: 'Angeleck — Organisation IA Autonome',
  description: 'Votre équipe d\'experts IA coordonnée par Raphaël. Créez, automatisez et développez vos business digitaux.',
  keywords: ['IA', 'agents', 'business', 'automatisation', 'Raphaël', 'Angeleck'],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className={`${inter.variable} ${playfair.variable} ${mono.variable}`}>
      <body className="antialiased">{children}</body>
    </html>
  );
}
