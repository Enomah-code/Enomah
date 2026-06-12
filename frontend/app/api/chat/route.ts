import Anthropic from '@anthropic-ai/sdk';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const MODEL = 'claude-opus-4-8';

const RAPHAEL_SYSTEM = `Tu es **Raphaël**, l'intelligence centrale et l'orchestrateur de **Angeleck** — une organisation IA autonome qui aide les entrepreneurs à créer, gérer et développer leurs business digitaux.

## Ton rôle
Tu es un consultant stratégique de niveau mondial et le chef d'orchestre d'une équipe de 10 agents experts spécialisés :
- **Sofia** — Directrice Stratégie Business (business model, marché, croissance)
- **Maya** — Directrice Marketing & Acquisition (Meta/Google/TikTok Ads, SEO, tunnels)
- **Nathan** — Expert Copywriting (pages de vente, emails, scripts, persuasion)
- **Elena** — Directrice Créative (branding, direction artistique, visuels)
- **Gabriel** — Architecte Technologie (API, automatisation, IA, infrastructure)
- **Lucas** — Directeur E-commerce (Shopify, conversion, UX, marketplaces)
- **Emma** — Analyste Data (marché, statistiques, tendances, KPIs)
- **Adam** — Directeur Finance (marges, ROI, cash flow, rentabilité)
- **Noah** — Producteur Média (vidéos publicitaires, montage, contenu)
- **Léa** — Responsable Sécurité (validation des décisions sensibles, RGPD)

## Ta méthode
1. **Comprendre** le besoin réel derrière la demande.
2. **Mobiliser** les bons experts (cite-les par leur nom quand c'est pertinent).
3. **Synthétiser** un plan d'action clair, concret et actionnable.

## Ton style
- Réponds en français, avec un ton professionnel, chaleureux et direct.
- Structure tes réponses (titres en **gras**, listes, étapes numérotées).
- Donne des chiffres concrets, des fourchettes de budget, des KPIs cibles quand c'est utile.
- Termine souvent par une question pour faire avancer la mission.
- Les décisions financières/légales critiques nécessitent une validation humaine — mentionne-le quand c'est pertinent.

Réponds directement avec ta réponse finale, sans exposer ton raisonnement interne.`;

// Keyword routing for the "active agents" badges shown in the UI.
function detectAgents(message: string): string[] {
  const low = message.toLowerCase();
  if (/(boutique|e-?commerce|shopify|vente en ligne|panier)/.test(low)) return ['Emma', 'Lucas', 'Nathan'];
  if (/(marketing|publicit|campagne|\bpub\b|ads|acquisition)/.test(low)) return ['Maya', 'Nathan', 'Elena', 'Adam'];
  if (/(stratégie|business|entreprise|produit|march|lancement)/.test(low)) return ['Sofia', 'Emma', 'Adam'];
  if (/(copywriting|rédige|texte|email|page de vente|script)/.test(low)) return ['Nathan', 'Elena'];
  if (/(vidéo|montage|réseaux sociaux|contenu)/.test(low)) return ['Noah', 'Elena'];
  if (/(technique|api|automatis|code|intégration|développ)/.test(low)) return ['Gabriel'];
  if (/(finance|budget|marge|roi|rentab)/.test(low)) return ['Adam', 'Emma'];
  return ['Raphaël'];
}

interface ChatBody {
  message?: string;
  history?: { role: 'user' | 'assistant'; content: string }[];
}

export async function POST(req: Request) {
  const apiKey = process.env.ANTHROPIC_API_KEY;

  // Signal to the client that no key is configured → fall back to demo mode.
  if (!apiKey) {
    return new Response(JSON.stringify({ error: 'no_api_key' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  let body: ChatBody;
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify({ error: 'invalid_body' }), { status: 400 });
  }

  const message = (body.message || '').trim();
  if (!message) {
    return new Response(JSON.stringify({ error: 'empty_message' }), { status: 400 });
  }

  const history = Array.isArray(body.history) ? body.history.slice(-12) : [];
  const agents = detectAgents(message);

  const client = new Anthropic({ apiKey });

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      const send = (obj: unknown) => controller.enqueue(encoder.encode(`data: ${JSON.stringify(obj)}\n\n`));
      try {
        // Tell the UI which experts Raphaël is mobilising.
        send({ type: 'agents', agents });

        const messages = [
          ...history.map((m) => ({ role: m.role, content: m.content })),
          { role: 'user' as const, content: message },
        ];

        const claudeStream = await client.messages.create({
          model: MODEL,
          max_tokens: 4096,
          system: RAPHAEL_SYSTEM,
          messages,
          stream: true,
        });

        for await (const event of claudeStream) {
          if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
            send({ chunk: event.delta.text });
          }
        }

        send({ type: 'done' });
        controller.enqueue(encoder.encode('data: [DONE]\n\n'));
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'unknown_error';
        send({ error: msg });
      } finally {
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream; charset=utf-8',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
    },
  });
}
