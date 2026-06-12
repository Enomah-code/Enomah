'use client';
import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Sparkles, Mic, Paperclip } from 'lucide-react';
import { AGENTS, MOCK_MESSAGES } from '@/lib/data';
import { chatStream, type ChatTurn } from '@/lib/api';
import type { Message } from '@/lib/types';
import AgentAvatarSVG from '../agents/AgentAvatarSVG';

const SUGGESTIONS = [
  'Crée une stratégie marketing pour mon produit',
  'Lance ma boutique en ligne sur Shopify',
  'Analyse mon marché et mes concurrents',
  'Rédige une page de vente persuasive',
  'Crée une campagne Meta Ads complète',
  'Construis un plan business en 90 jours',
];

function renderMarkdown(text: string) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`\n]+)`/g, '<code>$1</code>')
    .replace(/^---$/gm, '<hr/>')
    .replace(/^#{1,3} (.+)$/gm, (_, t) => `<div class="font-bold text-text-1 mt-3 mb-1">${t}</div>`)
    .replace(/^[•\-] (.+)$/gm, (_, t) => `<li class="ml-4">${t}</li>`)
    .replace(/(<li[^>]*>.*<\/li>\n?)+/g, m => `<ul>${m}</ul>`)
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n(?!<)/g, '<br/>');
}

interface Props {
  onAgentsChange?: (agents: string[]) => void;
}

export default function ChatWindow({ onAgentsChange }: Props) {
  const [messages, setMessages] = useState<Message[]>(MOCK_MESSAGES as Message[]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [streamText, setStreamText] = useState('');
  const [activeAgents, setActiveAgents] = useState<string[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollBottom = useCallback(() => {
    requestAnimationFrame(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }));
  }, []);

  useEffect(() => { scrollBottom(); }, [messages, streamText]);

  const send = useCallback(async () => {
    const msg = input.trim();
    if (!msg || streaming) return;
    setInput('');

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: msg, timestamp: new Date() };

    // Build the conversation history (exclude the seed welcome message).
    const history: ChatTurn[] = messages
      .filter((m) => m.role === 'user' || m.role === 'assistant')
      .map((m) => ({ role: m.role as 'user' | 'assistant', content: m.content }));

    setMessages(prev => [...prev, userMsg]);
    setStreaming(true);
    setStreamText('');
    setActiveAgents([]);

    let fullText = '';
    let usedAgents: string[] = [];

    await chatStream(
      msg,
      history,
      (chunk) => {
        fullText += chunk;
        setStreamText(fullText);
      },
      (agents) => {
        usedAgents = agents;
        setActiveAgents(agents);
        onAgentsChange?.(agents);
      }
    );

    const aiMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: fullText,
      timestamp: new Date(),
      agentsUsed: usedAgents,
    };

    setMessages(prev => [...prev, aiMsg]);
    setStreaming(false);
    setStreamText('');
    setActiveAgents([]);
    onAgentsChange?.([]);
  }, [input, streaming, messages, onAgentsChange]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  };

  const autoResize = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 140) + 'px';
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">

        {/* Welcome / Suggestions when no user messages */}
        {messages.length <= 1 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center pt-8 pb-4 gap-6">
            <div className="text-center">
              <div className="text-5xl mb-3">🧠</div>
              <h3 className="font-display font-bold text-2xl text-text-1 mb-2">Que souhaitez-vous créer ?</h3>
              <p className="text-text-3 text-sm max-w-sm">Raphaël mobilise les bons experts pour chaque mission.</p>
            </div>
            <div className="grid grid-cols-2 gap-2 max-w-2xl w-full">
              {SUGGESTIONS.map(s => (
                <motion.button key={s} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                  onClick={() => { setInput(s); textareaRef.current?.focus(); }}
                  className="text-left p-3 rounded-xl border border-line/8 bg-bg-2 hover:bg-bg-3 hover:border-accent-purple/20 text-xs text-text-2 transition-all shadow-soft">
                  {s}
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}

        {/* Messages */}
        <AnimatePresence initial={false}>
          {messages.map(msg => (
            <motion.div key={msg.id} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              {/* Avatar */}
              {msg.role === 'assistant' ? (
                <div className="flex-shrink-0"><AgentAvatarSVG agent={AGENTS[0]} size={32} showBadge={false} /></div>
              ) : (
                <div className="w-8 h-8 rounded-full bg-bg-3 border border-line/12 flex items-center justify-center text-xs font-bold text-text-2 flex-shrink-0">V</div>
              )}
              {/* Bubble */}
              <div className={`max-w-[78%] ${msg.role === 'user' ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
                <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-accent-purple/25 border border-accent-purple/30 text-text-1 rounded-tr-sm'
                    : 'bg-bg-2 border border-line/8 text-text-2 rounded-tl-sm'
                }`}>
                  {msg.role === 'assistant' ? (
                    <div className="chat-content" dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }} />
                  ) : (
                    msg.content
                  )}
                </div>
                {/* Agents used */}
                {msg.agentsUsed && msg.agentsUsed.length > 0 && (
                  <div className="flex items-center gap-1 px-1">
                    <span className="text-xs text-text-3">via</span>
                    {msg.agentsUsed.map(name => {
                      const agent = AGENTS.find(a => a.name === name);
                      return agent ? (
                        <span key={name} className="text-xs px-1.5 py-0.5 rounded-full" style={{ color: agent.color, background: `${agent.color}18` }}>
                          {agent.emoji} {name}
                        </span>
                      ) : null;
                    })}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Streaming message */}
        <AnimatePresence>
          {streaming && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="flex gap-3">
              <div className="flex-shrink-0"><AgentAvatarSVG agent={AGENTS[0]} size={32} showBadge={false} /></div>
              <div className="max-w-[78%]">
                {/* Active agents */}
                {activeAgents.length > 0 && (
                  <div className="flex items-center gap-1.5 mb-2 flex-wrap">
                    {activeAgents.map(name => {
                      const agent = AGENTS.find(a => a.name === name);
                      return agent ? (
                        <motion.span key={name} initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
                          className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border"
                          style={{ color: agent.color, borderColor: `${agent.color}40`, background: `${agent.color}12` }}>
                          <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
                          {agent.emoji} {name}
                        </motion.span>
                      ) : null;
                    })}
                  </div>
                )}
                <div className="rounded-2xl rounded-tl-sm px-4 py-3 bg-bg-2 border border-line/8 text-sm text-text-2 leading-relaxed">
                  {streamText ? (
                    <>
                      <div className="chat-content" dangerouslySetInnerHTML={{ __html: renderMarkdown(streamText) }} />
                      <span className="cursor-blink" />
                    </>
                  ) : (
                    <div className="flex items-center gap-2">
                      <span className="text-text-3">Raphaël analyse</span>
                      <div className="flex gap-1">
                        {[0,1,2].map(i => (
                          <motion.div key={i} animate={{ scale: [0.6,1,0.6], opacity: [0.4,1,0.4] }}
                            transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
                            className="w-1.5 h-1.5 rounded-full bg-accent-purple" />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-4 pb-4 pt-2 border-t border-line/8">
        <div className="flex gap-2 items-end bg-bg-2 border border-line/10 rounded-2xl px-4 py-3 shadow-soft focus-within:border-accent-purple/30 transition-colors">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={autoResize}
            onKeyDown={handleKeyDown}
            placeholder="Demandez à Raphaël... (Entrée pour envoyer)"
            rows={1}
            className="flex-1 bg-transparent resize-none outline-none text-sm text-text-1 placeholder-text-3 leading-relaxed max-h-36"
            style={{ scrollbarWidth: 'none' }}
          />
          <div className="flex items-center gap-1.5 pb-0.5">
            <button className="p-1.5 rounded-lg text-text-3 hover:text-text-2 hover:bg-bg-3 transition-colors"><Paperclip size={14} /></button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={send}
              disabled={!input.trim() || streaming}
              className="w-8 h-8 rounded-xl flex items-center justify-center transition-all disabled:opacity-30 disabled:cursor-not-allowed"
              style={{ background: 'linear-gradient(135deg, #7C3AED, #5B21B6)' }}
            >
              <Send size={14} className="text-white" />
            </motion.button>
          </div>
        </div>
        <div className="flex items-center justify-between px-1 mt-1.5">
          <div className="flex items-center gap-1 text-xs text-text-3">
            <Sparkles size={10} className="text-accent-purple" />
            <span>Propulsé par Claude · Angeleck v1.0</span>
          </div>
          <span className="text-xs text-text-3 font-mono">{input.length}</span>
        </div>
      </div>
    </div>
  );
}
