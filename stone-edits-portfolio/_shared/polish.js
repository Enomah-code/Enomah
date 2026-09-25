/* Stone Edits — neutral polish kit shared by every project.
 * Grain, vignette, beat grid, seeded PRNG and safe-zone guides.
 * Everything here is seek-safe: state is derived from timeline time only. */
(function () {
  function prng(seed) {
    let s = seed >>> 0 || 1;
    return function () {
      s = (s + 0x6d2b79f5) >>> 0;
      let t = s;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // beat(n) -> seconds for beat index n at the given BPM (n may be fractional)
  function beatGrid(bpm) {
    const b = 60 / bpm;
    const fn = (n) => +(n * b).toFixed(4);
    fn.len = b;
    fn.bar = (n) => +(n * 4 * b).toFixed(4);
    return fn;
  }

  function noiseTile(size, seed, mono) {
    const c = document.createElement("canvas");
    c.width = c.height = size;
    const ctx = c.getContext("2d");
    const img = ctx.createImageData(size, size);
    const r = prng(seed);
    for (let i = 0; i < img.data.length; i += 4) {
      const v = Math.floor(r() * 255);
      img.data[i] = v;
      img.data[i + 1] = mono ? v : Math.floor(r() * 255);
      img.data[i + 2] = mono ? v : Math.floor(r() * 255);
      img.data[i + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
    return c.toDataURL("image/png");
  }

  // Animated film grain: a seeded noise tile whose offset jumps every frame.
  function addGrain(host, tl, opts) {
    const o = Object.assign({ opacity: 0.06, duration: 10, fps: 30, size: 256, blend: "overlay", seed: 7, z: 90 }, opts || {});
    const el = document.createElement("div");
    el.className = "se-grain";
    el.style.cssText =
      "position:absolute;inset:-4px;pointer-events:none;z-index:" + o.z + ";opacity:" + o.opacity +
      ";mix-blend-mode:" + o.blend + ";background-image:url(" + noiseTile(o.size, o.seed, true) + ");background-size:" + o.size + "px " + o.size + "px;";
    host.appendChild(el);
    const r = prng(o.seed * 31 + 3);
    const offs = [];
    const frames = Math.ceil(o.duration * o.fps) + 2;
    for (let i = 0; i < frames; i++) offs.push([Math.floor(r() * o.size), Math.floor(r() * o.size)]);
    const proxy = { f: 0 };
    tl.fromTo(proxy, { f: 0 }, {
      f: frames - 1, duration: o.duration, ease: "none",
      onUpdate: function () {
        const p = offs[Math.min(frames - 1, Math.floor(proxy.f))];
        el.style.backgroundPosition = p[0] + "px " + p[1] + "px";
      },
    }, 0);
    return el;
  }

  function addVignette(host, strength, color, z) {
    const el = document.createElement("div");
    el.className = "se-vignette";
    const c = color || "0,0,0";
    el.style.cssText =
      "position:absolute;inset:0;pointer-events:none;z-index:" + (z || 89) +
      ";background:radial-gradient(ellipse 75% 70% at 50% 50%, rgba(" + c + ",0) 55%, rgba(" + c + "," + (strength || 0.2) + ") 100%);";
    host.appendChild(el);
    return el;
  }

  // Development-only guides; never enabled in a render.
  function addSafeZones(host, format) {
    const el = document.createElement("div");
    el.className = "se-safe";
    let css = "position:absolute;pointer-events:none;z-index:999;outline:2px dashed rgba(255,0,120,.8);";
    if (format === "9x16") css += "top:220px;bottom:380px;left:60px;right:140px;";
    else css += "inset:80px;";
    el.style.cssText = css;
    host.appendChild(el);
    return el;
  }

  window.SE = { prng: prng, beatGrid: beatGrid, addGrain: addGrain, addVignette: addVignette, addSafeZones: addSafeZones };
})();
