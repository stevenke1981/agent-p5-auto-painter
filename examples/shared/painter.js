/* Shared demo runtime. Advanced scene strategies still require agent-authored code. */
(function (root) {
  'use strict';
  const state = { ready: false, error: null, warnings: [] };
  const warn = (message) => { if (!state.warnings.includes(message)) state.warnings.push(message); };
  const status = (message) => { const el = root.document?.getElementById('status'); if (el) el.textContent = message; };
  function fail(error) {
    state.ready = false;
    state.error = String(error?.message || error);
    status(`無法繪製：${state.error}`);
    const button = root.document?.getElementById('download');
    if (button) button.disabled = true;
  }
  function orderedElements(scene) {
    return [...scene.layers].sort((a, b) => a.zIndex - b.zIndex).flatMap(layer =>
      [...layer.elements].sort((a, b) => (a.zIndex ?? 0) - (b.zIndex ?? 0)));
  }
  function pixelBox(bbox, width, height) {
    if (!Array.isArray(bbox) || bbox.length !== 4 || !bbox.every(Number.isFinite) || bbox[2] <= 0 || bbox[3] <= 0) {
      throw new Error('bbox must contain four finite numbers with positive width/height');
    }
    return [bbox[0] * width, bbox[1] * height, bbox[2] * width, bbox[3] * height];
  }
  function fontSpec(font, size = font.size) {
    const families = Array.isArray(font.family) ? font.family : [font.family];
    const generic = new Set(['serif', 'sans-serif', 'monospace', 'cursive', 'fantasy', 'system-ui']);
    const family = families.map(name => generic.has(name) ? name : JSON.stringify(name)).join(', ');
    return `${font.style || 'normal'} ${font.weight || 400} ${size}px ${family}`;
  }
  function textAnchor(box, align, verticalAlign, textHeight, ascent) {
    const [x, y, w, h] = box;
    return [x + (align === 'center' ? w / 2 : align === 'right' ? w : 0),
      y + (verticalAlign === 'middle' ? (h - textHeight) / 2 : verticalAlign === 'bottom' ? h - textHeight : 0) + ascent];
  }
  function drawTextBlock(graphics, element, scene) {
    const ctx = graphics.drawingContext;
    const t = element.text;
    const box = pixelBox(element.bbox, scene.canvas.width, scene.canvas.height);
    const lines = t.content.split(/\r\n|\n|\r/u); // Never split Thai/combining sequences into characters.
    ctx.save();
    try {
      ctx.textBaseline = 'alphabetic';
      ctx.font = fontSpec(t.font);
      if (t.letterSpacing) {
        if (!('letterSpacing' in ctx)) throw new Error(`${element.id}: letterSpacing unsupported by this browser`);
        ctx.letterSpacing = `${t.letterSpacing}px`;
      }
      const measure = () => {
        const metrics = lines.map(line => ctx.measureText(line || ' '));
        return { width: Math.max(...metrics.map(m => m.width)),
          ascent: Math.max(...metrics.map(m => m.actualBoundingBoxAscent)),
          descent: Math.max(...metrics.map(m => m.actualBoundingBoxDescent)) };
      };
      let metrics = measure();
      const leading = t.font.size * (t.lineHeight || 1.2);
      const height = metrics.ascent + metrics.descent + (lines.length - 1) * leading;
      const scale = Math.min(1, box[2] / (metrics.width || 1), box[3] / (height || 1));
      if (scale < 1) warn(`${element.id}: font size fitted from ${t.font.size} to ${(t.font.size * scale).toFixed(2)}px`);
      ctx.font = fontSpec(t.font, t.font.size * scale);
      if (t.letterSpacing) ctx.letterSpacing = `${t.letterSpacing * scale}px`;
      metrics = measure();
      const fittedHeight = metrics.ascent + metrics.descent + (lines.length - 1) * leading * scale;
      const align = t.align || 'left';
      ctx.textAlign = align;
      ctx.fillStyle = element.style?.fill || '#2d241d';
      ctx.translate(box[0] + box[2] / 2, box[1] + box[3] / 2);
      ctx.rotate((t.rotation || 0) * Math.PI / 180);
      const local = [-box[2] / 2, -box[3] / 2, box[2], box[3]];
      const [x, y] = textAnchor(local, align, t.verticalAlign, fittedHeight, metrics.ascent);
      lines.forEach((line, i) => ctx.fillText(line, x, y + i * leading * scale));
    } finally { ctx.restore(); }
  }
  async function waitForFonts(elements, timeout = 8000) {
    if (!root.document?.fonts) { warn('Font Loading API unavailable; verify fallback glyphs'); return; }
    let timer;
    const loading = Promise.all(elements.map(async (el) => {
      try {
        const loaded = await root.document.fonts.load(fontSpec(el.text.font), el.text.content);
        if (!loaded.length) warn(`${el.id}: system/fallback font used; verify glyph coverage`);
      } catch (_) { warn(`${el.id}: font download failed; fallback used`); }
    }));
    try {
      await Promise.race([loading, new Promise(resolve => {
        timer = setTimeout(() => { warn('Font loading timed out; fallback used'); resolve(); }, timeout);
      })]);
    } finally { clearTimeout(timer); }
  }
  function validateDemo(scene) {
    const { canvas, seed, renderer } = scene;
    if (!canvas || ![canvas.width, canvas.height].every(n => Number.isSafeInteger(n) && n > 0 && n <= 8192)
        || canvas.width * canvas.height > 16777216) throw new Error('Demo canvas limit: 8192 per side / 16 megapixels');
    if (!Number.isInteger(seed) || seed < 0 || seed > 4294967295) throw new Error('seed must be a uint32 integer');
    if (scene.build && scene.build !== 'p5') throw new Error('These demos support the p5 build only');
    if (!['p5', 'p5-brush', 'hybrid'].includes(renderer)) throw new Error('Invalid renderer');
    let sawText = false;
    for (const el of orderedElements(scene)) {
      pixelBox(el.bbox, canvas.width, canvas.height);
      if (el.type === 'text' || el.drawStrategy === 'text') {
        sawText = true;
        if (el.drawStrategy !== 'text' || !el.text?.font || !Number.isFinite(el.text.font.size)
            || el.text.font.size <= 0 || typeof el.text.content !== 'string' || !el.text.content.trim()) {
          throw new Error(`${el.id}: invalid text block; run validate_scene.py`);
        }
        if (el.text.renderMode && el.text.renderMode !== 'p5-text') throw new Error(`${el.id}: outline conversion is not implemented in these demos`);
      } else {
        if (sawText) throw new Error('Demo lettering must be the final layer; interleaved text requires custom code');
        if (!['primitive', 'polygon', 'watercolor', 'spline', 'repeated-marks'].includes(el.drawStrategy)) {
          throw new Error(`${el.id}: unsupported demo strategy ${el.drawStrategy}`);
        }
        if (el.drawStrategy === 'primitive' && !['rect', 'circle'].includes(el.geometry?.kind)) throw new Error(`${el.id}: unsupported primitive`);
        if (['polygon', 'watercolor', 'spline'].includes(el.drawStrategy)) {
          const points = el.geometry?.points;
          const minimum = el.drawStrategy === 'spline' ? 2 : 3;
          if (!Array.isArray(points) || points.length < minimum || points.length > 10000
              || !points.every(p => Array.isArray(p) && p.length === 2 && p.every(Number.isFinite))) {
            throw new Error(`${el.id}: geometry.points must contain ${minimum}–10000 normalized [x,y] pairs`);
          }
        }
        if (el.drawStrategy === 'repeated-marks' && (!Number.isInteger(el.geometry?.count) || el.geometry.count < 0 || el.geometry.count > 10000)) {
          throw new Error(`${el.id}: mark count must be 0–10000`);
        }
      }
    }
  }
  async function prepare(url) {
    state.ready = false; state.error = null; state.warnings = [];
    if (root.location.protocol === 'file:') throw new Error('請使用 HTTP server 開啟範例，不要直接開啟 HTML 檔');
    const response = await fetch(url, { cache: 'no-store' });
    if (!response.ok) throw new Error(`Scene Plan HTTP ${response.status}: ${url}`);
    const scene = await response.json();
    validateDemo(scene);
    await waitForFonts(orderedElements(scene).filter(el => el.drawStrategy === 'text'));
    root.pixelDensity(1);
    const canvas = root.createCanvas(scene.canvas.width, scene.canvas.height, scene.renderer === 'p5' ? root.P2D : root.WEBGL);
    canvas.parent('artwork');
    canvas.elt.setAttribute('role', 'img');
    canvas.elt.setAttribute('aria-label', orderedElements(scene).filter(el => el.text).map(el => el.text.content).join(' / ') || '程式繪製的水彩風景');
    if (scene.renderer !== 'p5') root.brush.scaleBrushes(3);
    root.noLoop();
    const text = root.createGraphics(scene.canvas.width, scene.canvas.height, root.P2D);
    text.pixelDensity(1);
    orderedElements(scene).filter(el => el.drawStrategy === 'text').forEach(el => drawTextBlock(text, el, scene));
    const button = root.document.getElementById('download');
    if (button) button.onclick = () => {
      try { root.saveCanvas(canvas.elt, 'agent-p5-painting', 'png'); }
      catch (error) { fail(error); }
    };
    return { scene, text };
  }
  function drawShape(el, scene) {
    const s = el.style || {};
    const native = scene.renderer === 'p5' || s.medium === 'p5';
    const api = native ? root : root.brush;
    const [x, y, w, h] = pixelBox(el.bbox, scene.canvas.width, scene.canvas.height);
    root.push();
    try {
      api.noFill(); api.noStroke();
      if (!native) { api.noHatch(); api.noMass(); }
      if (s.fill) {
        if (native) { const c = root.color(s.fill); c.setAlpha(s.opacity ?? 255); root.fill(c); }
        else { api.fill(s.fill, s.opacity ?? 120); api.fillBleed(s.bleed ?? 0.08); }
      }
      if (s.stroke) {
        if (native) { api.stroke(s.stroke); api.strokeWeight(s.strokeWeight ?? 1); }
        else api.set(s.brush || 'HB', s.stroke, s.strokeWeight ?? 1);
      }
      switch (el.drawStrategy) {
        case 'primitive':
          if (el.geometry.kind === 'rect') api.rect(x, y, w, h);
          else if (native) root.circle(x + w / 2, y + h / 2, Math.min(w, h));
          else api.circle(x + w / 2, y + h / 2, Math.min(w, h) / 2); // brush takes radius, p5 takes diameter.
          break;
        case 'watercolor': case 'polygon': case 'spline': {
          const points = el.geometry.points.map(([px, py]) => [px * scene.canvas.width, py * scene.canvas.height]);
          if (native) { // Native spline demo is an explicit polyline approximation.
            if (el.drawStrategy === 'spline') { api.noFill(); warn(`${el.id}: p5 spline preview uses a polyline`); }
            root.beginShape(); points.forEach(p => root.vertex(...p));
            if (el.drawStrategy === 'spline') root.endShape(); else root.endShape(root.CLOSE);
          } else if (el.drawStrategy === 'spline') api.spline(points, el.geometry.curvature ?? 0.35);
          else api.polygon(points);
          break;
        }
        case 'repeated-marks':
          for (let i = 0; i < el.geometry.count; i++) {
            const px = root.random(x + w * 0.02, x + w * 0.98);
            const py = root.random(y + h * 0.12, y + h);
            api.line(px, py, px + root.random(-w * 0.01, w * 0.01), py - root.random(h * 0.03, h * 0.12));
          }
          break;
      }
    } finally { root.pop(); }
  }
  function render(prepared) {
    const { scene, text } = prepared;
    root.randomSeed(scene.seed); root.noiseSeed(scene.seed); // Reset on every redraw, not only setup.
    root.background(scene.canvas.background || '#ffffff');
    root.push();
    try {
      if (scene.renderer !== 'p5') root.translate(-scene.canvas.width / 2, -scene.canvas.height / 2);
      orderedElements(scene).filter(el => el.drawStrategy !== 'text').forEach(el => drawShape(el, scene));
      root.image(text, 0, 0);
    } finally { root.pop(); }
    root.requestAnimationFrame(() => {
      if (state.error) return;
      state.ready = true;
      status(state.warnings.length ? `已完成；${state.warnings.join('；')}` : '已完成，可下載 PNG');
      const button = root.document.getElementById('download');
      if (button) button.disabled = false;
    });
  }
  const api = { state, orderedElements, pixelBox, fontSpec, textAnchor, drawTextBlock, waitForFonts, validateDemo, prepare, render, fail };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.Painter = api;
  root.__PAINTER__ = state;
  root.addEventListener?.('error', event => {
    if (event.error || event.message) fail(event.error || event.message);
    else if (event.target?.tagName === 'SCRIPT') fail(`Script load failed: ${event.target.src}`);
    else if (event.target?.tagName === 'LINK') warn('Stylesheet download failed; verify fallback fonts');
  }, true);
  root.addEventListener?.('unhandledrejection', event => fail(event.reason));
})(globalThis);
