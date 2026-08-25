# p5.brush Agent Guide

## Build decision

Default to p5 build.

### p5 build

```html
<script src="https://cdn.jsdelivr.net/npm/p5@2.2/lib/p5.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/p5.brush@latest"></script>
```

```js
function setup() {
  createCanvas(600, 600, WEBGL);
  brush.scaleBrushes(3);
  randomSeed(42);
  noiseSeed(42);
}
```

Do not call `brush.render()` in this build.

### Standalone build

Use only when explicitly requested. It has a different lifecycle and must call `brush.render()`.

## High-value API for automatic drawing

### Stroke

```js
brush.set('HB', '#222', 1.0);
brush.line(x1, y1, x2, y2);
brush.spline([[x1,y1], [x2,y2,0.8], [x3,y3]], 0.5);
```

### Watercolor-like fill

```js
brush.fill('#c8926b', 120);
brush.fillBleed(0.12);
brush.noStroke();
brush.polygon(points);
```

### Hatch

```js
brush.hatch(7, 35, { rand: 0.15 });
brush.hatchStyle('HB', '#40352f', 0.8);
```

### Dry-media mass

Use `brush.mass()` for crayon/pastel-like filled shading where a solid fill looks too digital.

### Hand-drawn movement

```js
brush.field('hand');
brush.wiggle(0.08);
```

Use sparingly. Geometry errors must be corrected geometrically, not hidden with wobble.

## Lettering with p5.brush

p5.brush 沒有直接取代所有 typography API，因此題字通常有三種方式：

1. **可讀字優先**：用 p5 `text()` 畫主標與說明文字。
2. **筆刷質感優先**：先用 p5 `text()` 定位，再對外框加 brush 線條或陰影。
3. **完全手寫感**：將字輪廓轉為 points/path，再用 `brush.spline()`、`brush.line()` 或 `brush.polygon()` 近似。

### 常見混合寫法

```js
function drawLetteringLayer() {
  push();
  textFont('Noto Sans TC');
  textSize(42);
  textAlign(LEFT, TOP);
  noStroke();
  fill('#1f1b16');
  text('夏日散步', 80, 60);

  brush.set('rotring', '#563f2e', 0.7);
  brush.line(80, 110, 240, 110); // decorative underline
  pop();
}
```

### 多語字型注意事項

- 中文、日文、韓文、泰文優先使用 Noto 系列。
- 需要 web font 時，可在 HTML `<head>` 先引入 Google Fonts。
- 若字型尚未載入完成，不要在第一幀立即繪製最終題字；可在 `preload()` 載入或於 `setup()` 確保使用 fallback stack。
- Thai 需要正確 shaping，盡量避免把字拆成逐字手動定位。

## Scaling

Built-in brushes often need `brush.scaleBrushes()`. Start near 3 for 600×600 and scale proportionally with canvas size, then visually verify.

## State discipline

Group draw calls by style when possible:

1. set stroke/fill/hatch state
2. draw several related elements
3. change state only when needed
4. draw text in a dedicated lettering phase

This improves code clarity and can reduce expensive fill-state changes.
