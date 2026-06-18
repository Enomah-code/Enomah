const EASE = {
  entry: "back.out(1.04)", // soft overshoot — tiny "settle"
  emphasis: "power3.inOut", // viscous, liquid acceleration
  exit: "power2.in", // sink, don't fly
  drift: "sine.inOut", // ambient float on idle panels
};
const DUR = {
  snap: 0.28,
  med: 0.5,
  slow: 1.1, // aurora cycles use longer than this
};
// RULE: every glass panel entry is a translate + scale, never opacity-only.
// RULE: never crossfade two glass panels — the lower one will look murky.
// RULE: panels are continuous — never "blink in". Move them onstage from off-canvas.
