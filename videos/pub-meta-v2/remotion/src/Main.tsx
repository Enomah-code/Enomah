// Pub Meta v2 — variante Remotion (React). Même storyboard, même bande son et mêmes repères
// que la variante HyperFrames (../shared/timeline.json) : seule la technique d'animation change
// (ressorts physiques `spring()` + `interpolate()` calculés image par image).
import React from "react";
import { AbsoluteFill, Audio, Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import "@fontsource/montserrat/600.css";
import "@fontsource/montserrat/700.css";
import "@fontsource/montserrat/800.css";
import "@fontsource/montserrat/900.css";
import timeline from "./data/timeline.json";
import content from "./data/content.json";

const C = { navy: "#081233", navy2: "#13285a", gold: "#d4af37", gold2: "#f2c14e", blue: "#4f6cf0", ink: "#0b1838", green: "#25d366", red: "#ff4b55", muted: "#93a0c8" };
const FONT = "Montserrat, sans-serif";

// ---------- outils d'animation ----------
type Ctx = { t: number; fps: number };
const Tctx = React.createContext<Ctx>({ t: 0, fps: 30 });
const useT = () => React.useContext(Tctx);
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
/** ressort démarrant à `at` secondes (0 → 1, avec dépassement selon l'amortissement) */
const useSpr = () => {
  const { t, fps } = useT();
  return (at: number, damping = 13, stiffness = 140, mass = 0.8) =>
    t < at ? 0 : spring({ frame: (t - at) * fps, fps, config: { damping, stiffness, mass } });
};
const lin = (t: number, a: number, b: number, x: number, y: number, e: (n: number) => number = Easing.out(Easing.cubic)) =>
  interpolate(t, [a, b], [x, y], { ...clamp, easing: e });
const pulse = (t: number, at: number, k = 0.08, d = 0.24) => 1 + k * interpolate(t, [at, at + d / 2, at + d], [0, 1, 0], clamp);
const shake = (t: number, at: number, a = 12) => (t >= at && t < at + 0.27 ? Math.sin((t - at) * 70) * a * (1 - (t - at) / 0.27) : 0);
const fr = (n: number) => Math.round(n).toLocaleString("fr-FR").replace(/ | /g, " ");

const abs = (s: React.CSSProperties): React.CSSProperties => ({ position: "absolute", ...s });
const Check: React.FC<{ size: number; color?: string }> = ({ size, color = "#fff" }) => (
  <svg viewBox="0 0 24 24" width={size} height={size} fill="none" stroke={color} strokeWidth={3.4} strokeLinecap="round" strokeLinejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5" /></svg>
);
const Star: React.FC<{ s: number; style?: React.CSSProperties }> = ({ s, style }) => (
  <svg viewBox="0 0 24 24" width={s} height={s} style={style}><path fill={C.gold2} d="M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 1.3-6.6-4.9-4.6 6.6-.8z" /></svg>
);

/** logo de la formation, tracé progressif (draw 0→1) puis cœur « IA » */
const FormationLogo: React.FC<{ draw: number; core: number; w: number }> = ({ draw, core, w }) => (
  <svg viewBox="0 0 260 390" width={w} height={(w * 390) / 260} style={{ overflow: "visible" }}>
    <path d="M130 2 L258 195 L130 388 L2 195 Z" fill="none" stroke={C.gold} strokeWidth={4} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} />
    <path d="M130 76 L210 195 L130 314 L50 195 Z" fill="none" stroke={C.gold} strokeWidth={2.6} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - Math.min(1, draw * 1.2)} />
    <g style={{ transform: `scale(${core})`, transformOrigin: "130px 195px", opacity: Math.min(1, core * 1.5) }}>
      <circle cx={130} cy={195} r={44} fill="#0b1838" stroke={C.blue} strokeWidth={2.6} />
      <text x={130} y={212} textAnchor="middle" fontFamily={FONT} fontWeight={800} fontSize={46} fill={C.gold}>IA</text>
    </g>
  </svg>
);

// ---------- décor permanent ----------
const Background: React.FC = () => {
  const { t } = useT();
  const k = Math.sin((t / 23) * Math.PI);
  return (
    <AbsoluteFill style={{ background: `radial-gradient(120% 70% at 50% 25%, ${C.navy2} 0%, ${C.navy} 60%, #040a20 100%)` }}>
      <div style={abs({ inset: -200, opacity: 0.35, transform: `translate(${-120 * (t / 46)}px, ${-240 * (t / 46)}px)`,
        backgroundImage: "linear-gradient(rgba(79,108,240,0.18) 2px, transparent 2px), linear-gradient(90deg, rgba(79,108,240,0.18) 2px, transparent 2px)",
        backgroundSize: "120px 120px" })} />
      <div style={abs({ left: -250 + 260 * k, top: 150 + 300 * k, width: 750, height: 750, borderRadius: "50%", background: "rgba(79,108,240,0.45)", filter: "blur(100px)" })} />
      <div style={abs({ left: 550 - 300 * k, top: 1150 - 260 * k, width: 700, height: 700, borderRadius: "50%", background: "rgba(212,175,55,0.35)", filter: "blur(100px)" })} />
    </AbsoluteFill>
  );
};

// ---------- HOOK ----------
const Bubble: React.FC<{ side: "l" | "r"; top: number; p: number; children: React.ReactNode; w?: number }> = ({ side, top, p, children, w }) => (
  <div style={abs({ [side === "l" ? "left" : "right"]: 26, top, maxWidth: 470, width: w, padding: "22px 26px", borderRadius: 30,
    [side === "l" ? "borderTopLeftRadius" : "borderTopRightRadius"]: 8, background: side === "l" ? "#1f2c34" : "#005c4b",
    fontWeight: 600, fontSize: 31, lineHeight: 1.28, opacity: Math.min(1, p * 1.6),
    transform: `translateX(${(side === "l" ? -60 : 60) * (1 - p)}px) scale(${0.5 + 0.5 * p})`, transformOrigin: side === "l" ? "0 0" : "100% 0" })}>
    {children}
  </div>
);

const Hook: React.FC = () => {
  const { t } = useT();
  const s = useSpr();
  const enter = s(0, 16, 90);
  const notifP = s(3.05, 14, 160);
  const zoomIn = s(3.05, 18, 170) - s(3.45, 18, 170);
  const chatP = s(3.45, 20, 200);
  const toastP = s(4.62, 10, 160);
  const after = s(4.62, 20, 120);
  const startScale = interpolate(enter, [0, 1], [1.6, 1]);
  const scale = startScale * (1 + 0.12 * zoomIn) * (1 - 0.1 * after);
  const rot = interpolate(enter, [0, 1], [-6, 0]) + lin(t, 1.95, 2.85, 0, 1.5, Easing.inOut(Easing.sin)) * (1 - chatP);
  const y = interpolate(enter, [0, 1], [260, 0]) + 120 * zoomIn;
  const dim = lin(t, 1.9, 2.4, 0, 0.45);
  const typing = t >= 3.7 && t < 4.03;
  return (
    <AbsoluteFill>
      <div style={abs({ left: 230, top: 140, width: 620, height: 1210, borderRadius: 86, background: "#05070f", padding: 16,
        boxShadow: "0 60px 140px rgba(0,0,0,0.6), 0 0 0 3px #2a3354 inset", opacity: 1 - 0.45 * after,
        transform: `translate(${shake(t, 3.1, 6)}px, ${y}px) scale(${scale}) rotate(${rot}deg)` })}>
        <div style={{ position: "relative", width: "100%", height: "100%", borderRadius: 72, overflow: "hidden", background: "#0b141a" }}>
          <div style={abs({ left: "50%", top: 22, width: 170, height: 46, marginLeft: -85, borderRadius: 30, background: "#000", zIndex: 9 })} />
          <div style={abs({ inset: 0, background: "radial-gradient(120% 80% at 30% 10%, #2b3f8f 0%, #101a45 45%, #060a1d 100%)" })}>
            <div style={abs({ left: 0, right: 0, top: 150, textAlign: "center", fontWeight: 600, fontSize: 34, color: "rgba(255,255,255,0.8)", opacity: s(0.5) , transform: `translateY(${-30 * (1 - s(0.5))}px)` })}>jeudi 9 octobre</div>
            <div style={abs({ left: 0, right: 0, top: 190, textAlign: "center", fontWeight: 700, fontSize: 176, letterSpacing: "-0.04em",
              opacity: Math.min(1, s(0.3, 14, 200) * 1.5), transform: `scale(${interpolate(s(0.3, 14, 200), [0, 1], [1.8, 1])})` })}>03:07</div>
            <svg viewBox="0 0 24 24" width={80} height={80} style={abs({ left: 255, top: 470, transform: `scale(${s(1.95, 9)}) rotate(${-40 * (1 - s(1.95, 9))}deg)` })}>
              <path fill={C.gold2} d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z" />
            </svg>
            <div style={abs({ left: 340, top: 430, fontWeight: 900, fontSize: 54, color: C.gold2, opacity: lin(t, 2.05, 2.5, 0, 1), transform: `translateY(${lin(t, 2.05, 3.05, 30, -40, Easing.out(Easing.sin))}px)` })}>
              z<span style={{ fontSize: 40 }}>z</span><span style={{ fontSize: 30 }}>z</span>
            </div>
            <div style={abs({ inset: 0, background: "#000", opacity: dim })} />
          </div>
          {/* conversation WhatsApp */}
          <div style={abs({ inset: 0, background: "#0b141a", transform: `translateY(${1200 * (1 - chatP)}px)`, opacity: t < 3.45 ? 0 : 1 })}>
            <div style={abs({ left: 0, right: 0, top: 0, height: 190, background: "#1f2c34", display: "flex", alignItems: "flex-end", gap: 20, padding: "0 28px 24px" })}>
              <div style={{ width: 84, height: 84, borderRadius: "50%", background: `linear-gradient(135deg, ${C.gold2}, ${C.gold})`, color: C.ink, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 900, fontSize: 34 }}>IA</div>
              <div><div style={{ fontWeight: 800, fontSize: 36 }}>Agent IA · Boutique</div><div style={{ fontWeight: 600, fontSize: 26, color: C.green, marginTop: 4 }}>en ligne</div></div>
            </div>
            <Bubble side="l" top={240} p={s(3.5)}>Bonsoir ! La formation est encore disponible ?</Bubble>
            {typing && (
              <div style={abs({ right: 26, top: 450, padding: "26px 30px", borderRadius: 30, borderTopRightRadius: 8, background: "#005c4b", display: "flex", gap: 10 })}>
                {[0, 1, 2].map((i) => <i key={i} style={{ width: 16, height: 16, borderRadius: "50%", background: "rgba(255,255,255,0.8)", display: "block", transform: `translateY(${-10 * Math.abs(Math.sin((t - 3.75 - i * 0.07) * 13))}px)` }} />)}
              </div>
            )}
            <Bubble side="r" top={450} p={s(4.05)}>Oui ! Voici votre lien de paiement Mobile Money. Accès immédiat après paiement.</Bubble>
            <Bubble side="l" top={740} p={s(4.3)}>C'est payé, merci !</Bubble>
            <Bubble side="r" top={900} p={s(4.45)} w={430}>
              <div style={{ display: "flex", gap: 18, alignItems: "center" }}>
                <div style={{ width: 70, height: 70, borderRadius: "50%", background: C.green, display: "flex", alignItems: "center", justifyContent: "center" }}><Check size={42} /></div>
                <div>Paiement reçu<div style={{ fontSize: 21, color: "rgba(255,255,255,0.55)" }}>Commande validée</div></div>
              </div>
            </Bubble>
          </div>
          {/* notification */}
          <div style={abs({ left: 22, right: 22, top: 90, padding: "26px 28px", borderRadius: 40, background: "rgba(245,246,250,0.96)", color: "#111", display: "flex", gap: 22, alignItems: "center",
            zIndex: 5, boxShadow: "0 20px 50px rgba(0,0,0,0.4)", opacity: t < 3.05 ? 0 : 1 - lin(t, 3.45, 3.7, 0, 1),
            transform: `translateY(${-220 * (1 - notifP) - 200 * lin(t, 3.45, 3.7, 0, 1)}px)` })}>
            <div style={{ flex: "none", width: 84, height: 84, borderRadius: 22, background: C.green, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <svg viewBox="0 0 24 24" width={54} height={54} fill="#fff"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .2-3.3-.7-2.8-1.1-4.6-4-4.7-4.2-.1-.2-1.1-1.5-1.1-2.9s.7-2 1-2.3c.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.4 0 .5l-.4.6-.4.4c-.1.1-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.2 1 2.1 1.4 2.4 1.5.3.2.5.1.6 0l.9-1c.2-.3.4-.2.6-.1l1.9.9c.3.1.5.2.5.3.1.1.1.6-.2 1.2z" /></svg>
            </div>
            <div><div style={{ fontWeight: 700, fontSize: 26, color: "#6b7280" }}>WhatsApp · maintenant</div><div style={{ fontWeight: 700, fontSize: 31, lineHeight: 1.2, marginTop: 4 }}>Client : Bonsoir ! La formation est encore disponible ?</div></div>
          </div>
        </div>
      </div>
      {/* gerbe d'étincelles + toast */}
      {Array.from({ length: 16 }).map((_, i) => {
        const a = (i / 16) * Math.PI * 2;
        const d = lin(t, 4.62, 5.3, 0, 300 + (i % 3) * 90);
        return <div key={i} style={abs({ left: 540 + Math.cos(a) * d - 11, top: 680 + Math.sin(a) * d - 11, width: 22, height: 22, borderRadius: "50%", background: C.gold2, boxShadow: `0 0 20px ${C.gold2}`, opacity: t < 4.62 ? 0 : lin(t, 5.0, 5.5, 1, 0) })} />;
      })}
      <div style={abs({ left: 70, top: 560, width: 940, padding: "40px 46px", borderRadius: 44, display: "flex", gap: 34, alignItems: "center", background: "linear-gradient(135deg, #1fd16a, #10a854)",
        boxShadow: "0 40px 120px rgba(37,211,102,0.45)", opacity: Math.min(1, toastP * 2), transform: `translateY(${120 * (1 - toastP)}px) scale(${(0.3 + 0.7 * toastP) * pulse(t, 5.15, 0.05)})` })}>
        <div style={{ flex: "none", width: 140, height: 140, borderRadius: "50%", background: "#fff", display: "flex", alignItems: "center", justifyContent: "center" }}><Check size={90} color="#10a854" /></div>
        <div><div style={{ fontWeight: 900, fontSize: 76, letterSpacing: "-0.03em", lineHeight: 1 }}>Vente conclue !</div><div style={{ fontWeight: 700, fontSize: 34, marginTop: 12, color: "rgba(255,255,255,0.92)" }}>Pendant que tu dormais · 03:08</div></div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- SANS ----------
const SansRow: React.FC<{ top: number; at: number; x: number; word: string; icon: string; dimAt: number }> = ({ top, at, x, word, icon, dimAt }) => {
  const { t } = useT();
  const s = useSpr();
  const p = s(at, 14, 170);
  const dim = lin(t, dimAt, dimAt + 0.3, 0, 1);
  return (
    <div style={abs({ left: 90, top, width: 900, display: "flex", alignItems: "center", gap: 40, opacity: Math.min(1, p * 1.5) * (1 - 0.7 * dim),
      transform: `translateX(${-500 * (1 - p) + shake(t, x + 0.05, 14)}px) skewX(${-18 * (1 - p)}deg) scale(${1 - 0.08 * dim})` })}>
      <div style={{ position: "relative", flex: "none", width: 200, height: 200, borderRadius: 50, background: "rgba(255,255,255,0.07)", border: "3px solid rgba(255,255,255,0.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <svg viewBox="0 0 24 24" width={110} height={110} fill="none" stroke="#fff" strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round"><path d={icon} /></svg>
        <svg viewBox="0 0 100 100" width={220} height={220} style={abs({ left: -10, top: -10 })}>
          <path d="M18 18L82 82" stroke={C.red} strokeWidth={10} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - lin(t, x, x + 0.16, 0, 1)} />
          <path d="M82 18L18 82" stroke={C.red} strokeWidth={10} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - lin(t, x + 0.12, x + 0.28, 0, 1)} />
        </svg>
      </div>
      <div>
        <div style={{ fontWeight: 800, fontSize: 46, color: C.red, letterSpacing: "0.02em" }}>SANS</div>
        <div style={{ position: "relative", fontWeight: 900, fontSize: 96, letterSpacing: "-0.04em", lineHeight: 1 }}>
          {word}
          <div style={abs({ left: -6, right: -6, top: "52%", height: 12, borderRadius: 8, background: C.red, transformOrigin: "0 50%", transform: `scaleX(${lin(t, x + 0.05, x + 0.3, 0, 1)})` })} />
        </div>
      </div>
    </div>
  );
};

const Sans: React.FC = () => {
  const { t } = useT();
  const s = useSpr();
  const a = s(8.6, 14, 170);
  const b = s(9.75, 11, 190);
  return (
    <AbsoluteFill>
      <SansRow top={300} at={5.85} x={6.35} dimAt={8.55} word="développeur" icon="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16" />
      <SansRow top={600} at={7.25} x={7.65} dimAt={8.55} word="agence" icon="M4 21V5l8-3v19M12 9l8 3v9M2 21h20M7 8h2M7 12h2M7 16h2M15 14h2M15 17h2" />
      <div style={abs({ left: 0, right: 0, top: 930, textAlign: "center" })}>
        <div style={{ fontWeight: 900, fontSize: 130, letterSpacing: "-0.04em", opacity: Math.min(1, a * 1.5), transform: `translateY(${90 * (1 - a)}px)` }}>Juste toi</div>
        <div style={{ fontWeight: 900, fontSize: 190, letterSpacing: "-0.05em", color: C.gold2, lineHeight: 1, textShadow: "0 0 60px rgba(242,193,78,0.55)",
          opacity: Math.min(1, b * 2), transform: `scale(${interpolate(b, [0, 1], [2.4, 1]) * pulse(t, 10.15, 0.08)})` }}>+ l'IA</div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- REVEAL ----------
const Reveal: React.FC = () => {
  const { t } = useT();
  const s = useSpr();
  const pre = s(10.55, 14, 170);
  const preOut = lin(t, 12.42, 12.67, 0, 1, Easing.in(Easing.quad));
  const ia = s(12.68, 13, 200);
  const letters = "BUSINESS|BUILDING".split("");
  return (
    <AbsoluteFill>
      <div style={abs({ left: 60, right: 60, top: 640, textAlign: "center", fontWeight: 900, fontSize: 104, letterSpacing: "-0.035em", lineHeight: 0.95,
        opacity: Math.min(1, pre * 1.5) * (1 - preOut), transform: `scale(${(0.7 + 0.3 * pre) * (1 + lin(t, 10.95, 12.4, 0, 0.12, Easing.linear)) * (1 + 0.6 * preOut)})` })}>
        Ce que tu vas <span style={{ color: C.gold2 }}>construire</span>…
      </div>
      <div style={abs({ left: 240, top: 180, width: 600, height: 600, borderRadius: "50%", background: "radial-gradient(circle, rgba(242,193,78,0.55), rgba(242,193,78,0) 65%)",
        opacity: lin(t, 12.65, 13.4, 0, 1), transform: `scale(${lin(t, 12.65, 13.85, 0.5, 1.2)})` })} />
      <div style={abs({ left: 358, top: 210, transform: `scale(${lin(t, 12.9, 16.7, 1, 1.06, Easing.out(Easing.sin))})` })}>
        <FormationLogo w={364} draw={lin(t, 12.62, 13.22, 0, 1, Easing.inOut(Easing.cubic))} core={s(12.85, 9, 180)} />
      </div>
      <div style={abs({ left: 0, right: 0, top: 800, textAlign: "center" })}>
        <div style={{ fontWeight: 900, fontSize: 200, color: C.gold2, letterSpacing: "-0.04em", lineHeight: 0.95, opacity: Math.min(1, ia * 2), transform: `scale(${interpolate(ia, [0, 1], [2.6, 1])})` }}>IA</div>
        <div style={{ fontWeight: 900, fontSize: 112, letterSpacing: "-0.02em", lineHeight: 1, perspective: 600 }}>
          {letters.map((ch, i) => {
            if (ch === "|") return <br key={i} />;
            const p = s(12.85 + i * 0.028, 12, 200);
            return <span key={i} style={{ display: "inline-block", opacity: Math.min(1, p * 1.5), transform: `translateY(${90 * (1 - p)}px) rotateX(${-90 * (1 - p)}deg)` }}>{ch}</span>;
          })}
        </div>
      </div>
      <div style={abs({ left: 0, right: 0, top: 1200, display: "flex", justifyContent: "center", opacity: Math.min(1, s(14.08) * 1.5), transform: `scaleX(${0.2 + 0.8 * s(14.08, 14, 170)})` })}>
        <div style={{ padding: "16px 40px", border: `3px solid ${C.gold}`, borderRadius: 999, fontWeight: 800, fontSize: 38, letterSpacing: "0.3em", color: C.gold2 }}>CERTIFICATION</div>
      </div>
      <div style={abs({ left: 0, right: 0, top: 1300, textAlign: "center", fontWeight: 700, fontSize: 36, color: C.muted, opacity: s(15.3), transform: `translateY(${80 * (1 - s(15.3))}px)` })}>signée EMK Blue Diamond</div>
      <AbsoluteFill style={{ background: "#fff", opacity: t < 12.62 ? 0 : t < 12.68 ? 0.95 : lin(t, 12.68, 13.18, 0.95, 0) }} />
    </AbsoluteFill>
  );
};

// ---------- MODULES ----------
const CARD_T = [18.6, 19.28, 20.54, 21.73, 22.88, 23.92];
const Modules: React.FC = () => {
  const { t } = useT();
  const s = useSpr();
  const eight = s(16.8, 12, 160);
  const fills = [...CARD_T, 24.2, 24.32];
  return (
    <AbsoluteFill>
      <div style={abs({ left: 90, top: 170, fontWeight: 900, fontSize: 300, lineHeight: 1, color: C.gold2, letterSpacing: "-0.06em", opacity: Math.min(1, eight * 2),
        transform: `scale(${interpolate(eight, [0, 1], [3, 1])}) rotate(${-20 * (1 - eight)}deg)` })}>8</div>
      <div style={abs({ left: 330, top: 245 })}>
        <div style={{ fontWeight: 900, fontSize: 100, letterSpacing: "-0.04em", lineHeight: 1, opacity: s(16.98), transform: `translateX(${120 * (1 - s(16.98))}px)` }}>modules</div>
        <div style={{ fontWeight: 800, fontSize: 50, color: C.muted, marginTop: 10, opacity: s(17.68), transform: `translateX(${120 * (1 - s(17.68))}px)` }}>pas à pas</div>
      </div>
      <div style={abs({ left: 90, top: 530, width: 900, height: 20, display: "flex", gap: 12, opacity: s(17.3), transform: `translateY(${30 * (1 - s(17.3))}px)` })}>
        {fills.map((at, i) => (
          <i key={i} style={{ flex: 1, borderRadius: 10, background: "rgba(255,255,255,0.12)", display: "block", overflow: "hidden" }}>
            <b style={{ display: "block", width: "100%", height: "100%", background: `linear-gradient(90deg, ${C.gold}, ${C.gold2})`, transformOrigin: "0 50%", transform: `scaleX(${lin(t, at, at + 0.3, 0, 1)})` }} />
          </i>
        ))}
      </div>
      {content.cards.map((c, i) => {
        const at = CARD_T[i];
        const pin = s(at - 0.08, 14, 180);
        const out = i < CARD_T.length - 1 ? lin(t, CARD_T[i + 1] - 0.16, CARD_T[i + 1] + 0.16, 0, 1, Easing.in(Easing.cubic)) : 0;
        if (t < at - 0.08 || out >= 1) return null;
        const ic = s(at + 0.05, 9, 200);
        return (
          <div key={i} style={abs({ left: 130, top: 640, width: 820, height: 640, borderRadius: 56, padding: 56, background: "linear-gradient(160deg, rgba(255,255,255,0.13), rgba(255,255,255,0.04))",
            border: "3px solid rgba(255,255,255,0.16)", boxShadow: "0 50px 120px rgba(0,0,0,0.45)", opacity: Math.min(1, pin * 1.5) * (1 - out),
            transform: `translateX(${900 * (1 - pin) - 900 * out}px) rotate(${14 * (1 - pin) - 14 * out}deg) scale(${0.85 + 0.15 * pin - 0.15 * out})` })}>
            <div style={{ fontWeight: 800, fontSize: 32, letterSpacing: "0.25em", color: C.gold2 }}>{c.n}</div>
            <div style={{ marginTop: 40, width: 210, height: 210, borderRadius: 56, background: `linear-gradient(135deg, ${C.gold2}, ${C.gold})`, display: "flex", alignItems: "center", justifyContent: "center",
              boxShadow: "0 24px 60px rgba(212,175,55,0.4)", transform: `scale(${0.4 + 0.6 * ic}) rotate(${-30 * (1 - ic)}deg)` }}>
              <svg viewBox="0 0 24 24" width={120} height={120} fill="none" stroke={C.ink} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"><path d={c.icon} /></svg>
            </div>
            <div style={{ marginTop: 44, fontWeight: 900, fontSize: 78, letterSpacing: "-0.035em", lineHeight: 1 }}>{c.t}</div>
            <div style={{ marginTop: 18, fontWeight: 600, fontSize: 38, color: "rgba(255,255,255,0.75)" }}>{c.s}</div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// ---------- BONUS ----------
const Tile: React.FC<{ left: number; p: number; rot: number; v: React.ReactNode; l: React.ReactNode; k?: number }> = ({ left, p, rot, v, l, k = 1 }) => (
  <div style={abs({ left, top: 210, width: 430, height: 340, borderRadius: 44, padding: 40, background: "rgba(255,255,255,0.08)", border: "3px solid rgba(255,255,255,0.14)",
    opacity: Math.min(1, p * 1.5), transform: `translateY(${-300 * (1 - p)}px) rotate(${rot * (1 - p)}deg) scale(${k})` })}>
    <div style={{ fontWeight: 900, fontSize: 150, letterSpacing: "-0.05em", color: C.gold2, lineHeight: 1 }}>{v}</div>
    <div style={{ fontWeight: 800, fontSize: 42, lineHeight: 1.1, marginTop: 18 }}>{l}</div>
  </div>
);
const Bonus: React.FC = () => {
  const { t } = useT();
  const s = useSpr();
  const n = lin(t, 25.25, 26.15, 0, 100, Easing.out(Easing.quad));
  const cert = s(27.95, 12, 110);
  const stamp = lin(t, 28.3, 28.6, 0, 1, Easing.in(Easing.poly(4)));
  return (
    <AbsoluteFill>
      <Tile left={90} p={s(24.9, 10)} rot={-8} k={pulse(t, 26.15, 0.06)} v={<>{Math.round(n)}+</>} l={<>prompts<br />professionnels</>} />
      <Tile left={560} p={s(26.05, 10)} rot={8} v="10" l={<>modèles<br />d'automatisation</>} />
      <div style={abs({ left: 210, top: 620, width: 660, height: 660, borderRadius: 22, overflow: "hidden", boxShadow: "0 50px 120px rgba(0,0,0,0.55)", opacity: Math.min(1, cert * 1.5),
        transform: `translate(${shake(t, 28.6, 10)}px, ${900 * (1 - cert)}px) rotate(${25 * (1 - cert) - 3 + lin(t, 28.5, 29.8, 0, 5, Easing.inOut(Easing.sin))}deg) scale(${0.6 + 0.4 * cert})` })}>
        <Img src={staticFile("certificat.png")} style={{ width: "100%", height: "100%", display: "block" }} />
      </div>
      <div style={abs({ left: 720, top: 1060, width: 250, height: 250, borderRadius: "50%", border: `10px solid ${C.gold2}`, color: C.gold2, background: "rgba(8,18,51,0.9)",
        display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", fontWeight: 900, fontSize: 40, lineHeight: 1.05, letterSpacing: "0.04em",
        opacity: t < 28.3 ? 0 : 1, transform: `scale(${interpolate(stamp, [0, 1], [2.6, 1])}) rotate(${interpolate(stamp, [0, 1], [-40, -12])}deg)` })}>TON<br />CERTIFICAT</div>
    </AbsoluteFill>
  );
};

// ---------- PROOF ----------
const Proof: React.FC = () => {
  const { t } = useT();
  const s = useSpr();
  const num = s(29.4, 10, 150);
  const rate = s(31.8, 14);
  return (
    <AbsoluteFill>
      <div style={abs({ left: 0, right: 0, top: 190, textAlign: "center", fontWeight: 900, fontSize: 300, letterSpacing: "-0.06em", lineHeight: 1, color: C.gold2,
        opacity: Math.min(1, num * 1.5), transform: `scale(${(0.4 + 0.6 * num) * pulse(t, 30.3, 0.07)})` })}>+{Math.round(lin(t, 29.45, 30.25, 0, 100, Easing.out(Easing.quad)))}</div>
      <div style={abs({ left: 0, right: 0, top: 500, textAlign: "center", fontWeight: 900, fontSize: 64, letterSpacing: "-0.03em", lineHeight: 1.05, opacity: s(30.4), transform: `translateY(${80 * (1 - s(30.4))}px)` })}>
        apprenants nous font<br /><span style={{ color: C.gold2 }}>déjà confiance</span>
      </div>
      <div style={abs({ left: 90, top: 690, width: 900, height: 170 })}>
        {content.avatars.map(([l, col], i) => {
          const p = s(29.5 + i * 0.06, 9, 200);
          return <div key={i} style={abs({ left: i * 75, top: 0, width: 150, height: 150, borderRadius: "50%", border: `6px solid ${C.navy}`, background: col, zIndex: 20 - i,
            display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 900, fontSize: 50, color: C.ink, opacity: Math.min(1, p * 2), transform: `translateY(${60 * (1 - p)}px) scale(${p})` })}>{l}</div>;
        })}
      </div>
      <div style={abs({ left: 0, right: 0, top: 920, display: "flex", justifyContent: "center", alignItems: "center", gap: 30, opacity: rate, transform: `translateY(${80 * (1 - rate)}px)` })}>
        <div style={{ fontWeight: 900, fontSize: 140, letterSpacing: "-0.05em", color: C.gold2, lineHeight: 1 }}>100 %</div>
        <div><div style={{ fontWeight: 800, fontSize: 46, lineHeight: 1.05 }}>d'avis positifs</div>
          <div style={{ display: "flex", gap: 8, marginTop: 12 }}>{[0, 1, 2, 3, 4].map((i) => { const p = s(32.0 + i * 0.07, 8, 220); return <Star key={i} s={50} style={{ transform: `scale(${p}) rotate(${-90 * (1 - p)}deg)` }} />; })}</div></div>
      </div>
      <div style={abs({ left: 0, right: 0, top: 1150, display: "flex", justifyContent: "center", gap: 20 })}>
        {[["Côte d'Ivoire", ["#f77f00", "#fff", "#009e60"]], ["Bénin", null], ["Cameroun", ["#007a5e", "#ce1126", "#fcd116"]]].map(([name, cols], i) => {
          const p = s(32.6 + i * 0.1, 10);
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 14, padding: "16px 26px", borderRadius: 999, background: "rgba(255,255,255,0.09)", fontWeight: 700, fontSize: 32, opacity: Math.min(1, p * 1.5), transform: `translateY(${60 * (1 - p)}px)` }}>
              <div style={{ width: 56, height: 38, borderRadius: 6, overflow: "hidden", display: "flex" }}>
                {cols ? (cols as string[]).map((c, j) => <span key={j} style={{ flex: 1, background: c }} />) : (
                  <><span style={{ flex: 0.4, background: "#008751" }} /><span style={{ flex: 0.6, display: "flex", flexDirection: "column" }}><span style={{ flex: 1, background: "#fcd116" }} /><span style={{ flex: 1, background: "#e8112d" }} /></span></>
                )}
              </div>
              {name as string}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ---------- OFFER ----------
const Offer: React.FC = () => {
  const { t } = useT();
  const s = useSpr();
  const card = s(33.9, 14, 120);
  const price = lin(t, 35.2, 36.55, 35000, 4999, Easing.out(Easing.cubic));
  const badge = lin(t, 37.85, 38.15, 0, 1, Easing.in(Easing.poly(4)));
  const guar = s(39.7, 11, 140);
  const shrink = s(39.7, 18);
  return (
    <AbsoluteFill>
      <div style={abs({ left: 0, right: 0, top: 150, display: "flex", justifyContent: "center", opacity: Math.min(1, s(33.85) * 1.5), transform: `scale(${0.4 + 0.6 * s(33.85, 10)})` })}>
        <div style={{ padding: "14px 38px", borderRadius: 999, background: C.red, fontWeight: 900, fontSize: 38, letterSpacing: "0.12em" }}>AUJOURD'HUI</div>
      </div>
      <div style={abs({ left: 140, top: 250, width: 800, height: 960, borderRadius: 48, background: "#fff", overflow: "hidden", boxShadow: "0 60px 140px rgba(0,0,0,0.55)",
        opacity: Math.min(1, card * 1.5),
        transform: `translate(${shake(t, 38.15, 8)}px, ${1100 * (1 - card) - 40 * shrink + (t > 36.6 && t < 36.76 ? 16 * Math.sin(((t - 36.6) / 0.16) * Math.PI) : 0)}px) rotate(${-8 * (1 - card)}deg) scale(${1 - 0.06 * shrink})` })}>
        <div style={{ width: 800, height: 560, overflow: "hidden" }}><Img src={staticFile("formation-vignette.png")} style={{ width: 800, height: 800, marginTop: -40, display: "block" }} /></div>
        <div style={{ padding: "36px 48px 0", fontWeight: 900, fontSize: 40, color: C.ink, lineHeight: 1.1 }}>CERTIFICATION IA BUSINESS BUILDING</div>
        <div style={{ padding: "18px 48px 0", fontWeight: 900, fontSize: 150, letterSpacing: "-0.05em", color: C.ink, lineHeight: 1, transform: `scale(${pulse(t, 36.55, 0.1)})`, transformOrigin: "20% 50%" }}>
          {fr(price)} <small style={{ fontSize: 60, letterSpacing: "-0.02em", color: C.gold }}>F CFA</small>
        </div>
        <div style={{ position: "relative", display: "inline-block", margin: "16px 48px 0", fontWeight: 800, fontSize: 54, color: "#8a90a6", opacity: lin(t, 37.3, 37.6, 0, 1), transform: `translateX(${lin(t, 37.3, 37.6, -60, 0)}px)` }}>
          35 000 F
          <div style={abs({ left: -6, right: -6, top: "50%", height: 9, borderRadius: 6, background: C.red, transformOrigin: "0 50%", transform: `scaleX(${lin(t, 37.7, 37.95, 0, 1)})` })} />
        </div>
      </div>
      <div style={abs({ left: 780, top: 190, width: 250, height: 250, borderRadius: "50%", background: C.red, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
        fontWeight: 900, boxShadow: "0 24px 60px rgba(255,75,85,0.5)", opacity: t < 37.85 ? 0 : 1,
        transform: `scale(${interpolate(badge, [0, 1], [3, 1])}) rotate(${interpolate(badge, [0, 1], [-40, 14]) - 8 * Math.max(0, Math.sin((t - 38.4) * Math.PI * 2)) * (t > 38.4 && t < 40.4 ? 1 : 0)}deg)` })}>
        <div style={{ fontSize: 84, letterSpacing: "-0.04em", lineHeight: 1 }}>-86%</div><div style={{ fontSize: 26, letterSpacing: "0.1em" }}>LANCEMENT</div>
      </div>
      <div style={abs({ left: 90, top: 1130, width: 900, padding: "28px 36px", borderRadius: 36, background: "linear-gradient(135deg, #1fd16a, #10a854)", display: "flex", alignItems: "center", gap: 28,
        boxShadow: "0 30px 80px rgba(37,211,102,0.4)", opacity: Math.min(1, guar * 1.5), transform: `translateY(${400 * (1 - guar)}px) scale(${pulse(t, 41.1, 0.04)})` })}>
        <svg viewBox="0 0 24 24" width={100} height={100} fill="none" stroke="#fff" strokeWidth={2} strokeLinejoin="round"><path d="M12 2l8 3v6c0 5-3.4 9.3-8 11-4.6-1.7-8-6-8-11V5z" fill="rgba(255,255,255,0.15)" /><path d="M8 12l3 3 5-6" strokeWidth={2.6} strokeLinecap="round" /></svg>
        <div><div style={{ fontWeight: 900, fontSize: 46, letterSpacing: "-0.02em", lineHeight: 1.05 }}>Satisfait ou remboursé</div><div style={{ fontWeight: 700, fontSize: 32, marginTop: 6 }}>Garantie 7 jours · Accès à vie</div></div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- CTA ----------
const Cta: React.FC = () => {
  const { t } = useT();
  const s = useSpr();
  const pill = s(42.6, 9);
  const press = t > 42.92 && t < 43.12 ? Math.sin(((t - 42.92) / 0.2) * Math.PI) : 0;
  const breathe = t > 43.4 ? 1 + 0.06 * Math.abs(Math.sin((t - 43.4) * Math.PI / 0.9)) : 1;
  const hand = s(42.62, 16, 180);
  return (
    <AbsoluteFill>
      <div style={abs({ left: 410, top: 150 })}><FormationLogo w={260} draw={lin(t, 42.3, 42.8, 0, 1, Easing.inOut(Easing.cubic))} core={s(42.5, 9, 180)} /></div>
      <div style={abs({ left: 0, right: 0, top: 580, textAlign: "center", opacity: s(42.45), transform: `translateY(${60 * (1 - s(42.45))}px)` })}>
        <div style={{ fontWeight: 900, fontSize: 150, color: C.gold2, letterSpacing: "-0.04em", lineHeight: 0.95 }}>IA</div>
        <div style={{ fontWeight: 900, fontSize: 92, letterSpacing: "-0.02em", lineHeight: 1 }}>BUSINESS BUILDING</div>
      </div>
      <div style={abs({ left: 0, right: 0, top: 960, display: "flex", justifyContent: "center" })}>
        <div style={{ display: "flex", alignItems: "center", gap: 20, padding: "36px 64px", borderRadius: 999, background: `linear-gradient(135deg, ${C.gold2}, ${C.gold})`, color: C.ink, fontWeight: 900, fontSize: 54,
          boxShadow: "0 24px 70px rgba(212,175,55,0.5)", opacity: Math.min(1, pill * 1.5), transform: `scale(${(0.5 + 0.5 * pill) * (1 - 0.08 * press) * breathe})` }}>
          Rejoindre la formation
          <svg viewBox="0 0 24 24" width={54} height={54} fill="none" stroke={C.ink} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
        </div>
      </div>
      <svg viewBox="0 0 24 24" width={120} height={120} fill="#fff" stroke={C.ink} strokeWidth={1.2} strokeLinejoin="round"
        style={abs({ left: 700, top: 1050, opacity: hand, transform: `translate(${160 * (1 - hand)}px, ${160 * (1 - hand)}px) scale(${1 - 0.2 * press})` })}>
        <path d="M9 11V4.5a1.5 1.5 0 013 0V10l5.3 1.1a2 2 0 011.6 2.3l-.9 5A3 3 0 0115 21h-4.2a3 3 0 01-2.4-1.2L5 15.3a1.5 1.5 0 012.2-2L9 15z" />
      </svg>
      <div style={abs({ left: 0, right: 0, top: 1150, textAlign: "center", fontWeight: 900, fontSize: 60, letterSpacing: "-0.02em", opacity: Math.min(1, s(43.7) * 1.5), transform: `scale(${0.6 + 0.4 * s(43.7, 10)})` })}>
        Commence <span style={{ color: C.gold2 }}>dès ce soir</span>
      </div>
      <div style={abs({ left: 0, right: 0, top: 1245, display: "flex", justifyContent: "center", alignItems: "center", gap: 14, fontWeight: 800, fontSize: 40, color: C.gold2, opacity: s(44.0), transform: `translateY(${80 * (1 - s(44.0))}px)` })}>
        <svg viewBox="0 0 24 24" width={44} height={44} fill="none" stroke={C.gold2} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" style={{ transform: `translateY(${t > 44.3 ? 14 * Math.abs(Math.sin((t - 44.3) * Math.PI / 0.56)) : 0}px)` }}><path d="M12 4v15M5 12l7 7 7-7" /></svg>
        Lien sous la vidéo
      </div>
    </AbsoluteFill>
  );
};

// ---------- transitions + sous-titres ----------
const Wipe: React.FC = () => {
  const { t } = useT();
  const b = timeline.scenes.slice(1).map((s) => s.start).find((x) => t >= x - 0.21 && t < x + 0.22);
  if (b === undefined) return null;
  const x = lin(t, b - 0.21, b + 0.21, -900, 1500, Easing.inOut(Easing.quad));
  return <div style={abs({ left: -200, top: -400, width: 700, height: 2800, zIndex: 40, transform: `translateX(${x}px) rotate(14deg)`,
    background: `linear-gradient(90deg, rgba(242,193,78,0), ${C.gold2} 40%, ${C.gold} 60%, rgba(212,175,55,0))` })} />;
};

const Captions: React.FC = () => {
  const { t } = useT();
  const cap = timeline.captions.find((c) => t >= c.s && t < c.e);
  if (!cap) return null;
  const inP = lin(t, cap.s, cap.s + 0.14, 0, 1);
  return (
    <div style={abs({ left: 50, right: 50, top: 1420, textAlign: "center", fontWeight: 900, fontSize: 68, letterSpacing: "-0.02em", lineHeight: 1.1, zIndex: 50,
      textShadow: "0 6px 24px rgba(0,0,0,0.85), 0 2px 4px rgba(0,0,0,0.9)", opacity: inP, transform: `translateY(${30 * (1 - inP)}px) scale(${0.9 + 0.1 * inP})` })}>
      {cap.words.map((w, j) => (
        <span key={j} style={{ display: "inline-block", margin: "0 13px", color: t >= w.s && w.hl ? C.gold2 : "#fff", transform: `scale(${pulse(t, w.s, 0.1, 0.24)})` }}>{w.w}</span>
      ))}
    </div>
  );
};

const SCENES: Record<string, React.FC> = { hook: Hook, sans: Sans, reveal: Reveal, modules: Modules, bonus: Bonus, proof: Proof, offer: Offer, cta: Cta };

export const Main: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  return (
    <Tctx.Provider value={{ t, fps }}>
      <AbsoluteFill style={{ fontFamily: FONT, color: "#fff", overflow: "hidden" }}>
        <Background />
        {timeline.scenes.map((sc) => {
          const S = SCENES[sc.id];
          return t >= sc.start && t < sc.end ? <AbsoluteFill key={sc.id}><S /></AbsoluteFill> : null;
        })}
        <Wipe />
        <Captions />
        <Audio src={staticFile("mix.wav")} />
      </AbsoluteFill>
    </Tctx.Provider>
  );
};
