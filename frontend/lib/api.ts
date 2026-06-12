const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface StreamChunk {
  chunk?: string;
  type?: string;
  agent?: string;
  session_id?: string;
  error?: string;
}

export class AngeleckAPI {
  private baseUrl: string;

  constructor(baseUrl = API_URL) {
    this.baseUrl = baseUrl;
  }

  async chat(message: string, sessionId: string): Promise<{ response: string; agents_used: string[] }> {
    const res = await fetch(`${this.baseUrl}/api/v1/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: sessionId }),
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  }

  async *streamChat(message: string, sessionId: string): AsyncGenerator<StreamChunk> {
    const res = await fetch(`${this.baseUrl}/api/v1/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: sessionId }),
    });

    if (!res.ok || !res.body) throw new Error(`Stream error: ${res.status}`);

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') return;
          try { yield JSON.parse(data); } catch { /* skip */ }
        }
      }
    }
  }

  async getAgents(): Promise<{ agents: { name: string; tasks: number; success_rate: number }[]; total_tasks_processed: number }> {
    const res = await fetch(`${this.baseUrl}/api/v1/agents`);
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  }

  async getNetworkStatus(): Promise<{ status: string; agents: number; health: number }> {
    const res = await fetch(`${this.baseUrl}/api/v1/status`);
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  }
}

export const api = new AngeleckAPI();

// Mock fallback for offline / demo mode
export async function mockStream(message: string, onChunk: (text: string) => void, onAgents: (agents: string[]) => void): Promise<void> {
  const responses = buildMockResponse(message);
  onAgents(responses.agents);

  for (const chunk of responses.text) {
    await new Promise(r => setTimeout(r, 25 + Math.random() * 40));
    onChunk(chunk);
  }
}

function buildMockResponse(message: string): { text: string[]; agents: string[] } {
  const low = message.toLowerCase();

  if (low.includes('boutique') || low.includes('e-commerce') || low.includes('shopify')) {
    return {
      agents: ['Emma', 'Lucas', 'Nathan'],
      text: chars('J\'analyse votre demande concernant le e-commerce.\n\n**Mission activée :**\n\n**Emma** analyse le marché et les performances actuelles...\n**Lucas** examine l\'architecture de votre boutique...\n**Nathan** prépare les textes de conversion...\n\n---\n\n**Rapport consolidé :**\n\nPour optimiser une boutique e-commerce, voici la stratégie recommandée :\n\n1. **Audit UX** — Identifier les points de friction dans le parcours client\n2. **Fiches produits** — Textes persuasifs avec bénéfices + preuve sociale\n3. **Page de paiement** — Simplification maximale (1 étape)\n4. **Relances panier** — Séquence de 3 emails avec urgence\n5. **A/B testing** — Tester 2 versions pendant 14 jours\n\nLe taux de conversion moyen du secteur est de **2-3%**. Avec ces optimisations, nous visons **4-5%** dans les 90 jours.\n\nVoulez-vous que je détaille l\'une de ces étapes ?'),
    };
  }

  if (low.includes('marketing') || low.includes('publicité') || low.includes('campagne') || low.includes('pub')) {
    return {
      agents: ['Maya', 'Nathan', 'Elena', 'Adam'],
      text: chars('Parfait. Je vais coordonner l\'équipe marketing.\n\n**Agents mobilisés :**\n🎯 **Maya** — Stratégie d\'acquisition\n✍️ **Nathan** — Copywriting des publicités\n🎨 **Elena** — Créatifs visuels\n💰 **Adam** — Analyse budgétaire\n\n---\n\n**Plan de campagne recommandé :**\n\n**Phase 1 — Tests (2 semaines)**\nBudget: 500-800€\n• 3 audiences froides testées\n• 2 visuels par audience\n• Objectif: trouver le meilleur coût par clic\n\n**Phase 2 — Scaling (4 semaines)**\nBudget: 2 000-4 000€\n• Doubler le budget des audiences gagnantes\n• Retargeting des visiteurs (ROAS cible: 3x)\n• Lookalike audiences\n\n**KPIs cibles :**\n- CPM: < 12€\n- CTR: > 2%\n- ROAS: 3x minimum\n\nAdam valide la rentabilité du plan avant tout engagement budgétaire.\n\nSouhaitez-vous que je génère les textes publicitaires maintenant ?'),
    };
  }

  if (low.includes('stratégie') || low.includes('business') || low.includes('entreprise') || low.includes('produit')) {
    return {
      agents: ['Sofia', 'Emma', 'Adam'],
      text: chars('Excellente question stratégique. Je déploie l\'équipe.\n\n**Conseil activé :**\n👩‍💼 **Sofia** — Vision business et positionnement\n📊 **Emma** — Analyse de marché et données\n💰 **Adam** — Viabilité financière\n\n---\n\n**Diagnostic stratégique :**\n\nPour développer un business digital viable, voici le cadre d\'analyse :\n\n**1. Validation du marché**\n• Taille du marché adressable\n• Niveau de concurrence\n• Tendances émergentes\n\n**2. Positionnement différenciant**\n• Proposition de valeur unique (UVP)\n• Segment cible précis\n• Prix premium vs volume\n\n**3. Modèle économique**\n• Revenus récurrents (SaaS/abonnement)\n• Marges cibles: > 60% pour un digital\n• LTV/CAC ratio: objectif 3:1 minimum\n\n**4. Plan de lancement**\n• MVP en 30 jours\n• 10 premiers clients en 60 jours\n• Breakeven en 6 mois\n\nQuel aspect souhaitez-vous approfondir en premier ?'),
    };
  }

  return {
    agents: ['Raphaël'],
    text: chars('J\'ai bien reçu votre demande. Laissez-moi analyser comment je peux vous aider au mieux.\n\nEn tant que consultant stratégique d\'Angeleck, je coordonne une équipe de **10 experts spécialisés** :\n\n- 📢 **Maya** — Marketing & acquisition\n- 👩‍💼 **Sofia** — Stratégie business\n- ✍️ **Nathan** — Copywriting\n- 🎨 **Elena** — Création visuelle\n- 🛒 **Lucas** — E-commerce\n- 📊 **Emma** — Analyse data\n- 💰 **Adam** — Finance\n- 🎬 **Noah** — Vidéo\n- 👨‍💻 **Gabriel** — Technologie\n- 🛡️ **Léa** — Sécurité\n\nPour vous aider efficacement, pourriez-vous me préciser :\n\n1. **Quel est votre objectif principal** ?\n2. **Quel est votre secteur d\'activité** ?\n3. **Où en êtes-vous** (idée, lancement, croissance) ?\n\nAvec ces informations, je mobilise immédiatement les bons experts.'),
  };
}

function chars(text: string): string[] {
  const chunks: string[] = [];
  for (let i = 0; i < text.length; i += 3) {
    chunks.push(text.slice(i, i + 3));
  }
  return chunks;
}
