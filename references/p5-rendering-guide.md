# p5 Rendering Guide for Agents

## Geometry model

Borrow the useful model from p5-code-painter: represent every editable graphic with stable properties rather than raw drawing commands only.

Recommended element shape:

```json
{
  "id": "face-outline",
  "type": "shape",
  "bbox": [0.28, 0.17, 0.44, 0.51],
  "rotation": 0,
  "fill": "#F0C6A4",
  "stroke": "#2B201C",
  "strokeWeight": 2,
  "zIndex": 20
}
```

Recommended text element:

```json
{
  "id": "title-main",
  "type": "text",
  "drawStrategy": "text",
  "bbox": [0.08, 0.06, 0.42, 0.12],
  "text": {
    "content": "夏日散步",
    "language": "zh-Hant",
    "font": {"family": ["Noto Sans TC", "sans-serif"], "size": 42, "weight": 700},
    "align": "left",
    "verticalAlign": "top",
    "lineHeight": 1.2,
    "rotation": 0,
    "renderMode": "p5-text"
  }
}
```

Use one of:
- rect / roundedRect
- circle / ellipse
- line / polyline
- bezier
- polygon
- spline
- freehand path
- repeated marks
- text

## Code layout

```js
const CFG = {
  width: 1024,
  height: 1024,
  seed: 42,
  bg: '#f6f1e8'
};

function setup() {
  createCanvas(CFG.width, CFG.height, WEBGL);
  randomSeed(CFG.seed);
  noiseSeed(CFG.seed);
  noLoop();
}

function draw() {
  background(CFG.bg);
  translate(-width/2, -height/2);
  drawBackgroundLayer();
  drawMainSubject();
  drawDetails();
  drawLetteringLayer();
}
```

## Coordinate rules

Scene analysis uses top-left coordinates because they map naturally to image pixels and bbox detection.

p5 WEBGL uses center origin. Always translate once at the beginning of the render pass:

```js
translate(-width/2, -height/2);
```

After that, all Scene Plan coordinates remain top-left based.

## Text placement rules

- Keep text in its own layer when possible.
- Convert normalized bbox `[x, y, w, h]` to canvas coordinates before drawing text.
- Prefer using the bbox as a safe text block region, not only a single point.
- Main title can use `textSize()` relative to bbox height.
- For multiline text, set `textLeading(fontSize * lineHeight)`.
- For centered titles, use `textAlign(CENTER, CENTER)` and anchor the bbox center.

## Shape approximation

Prefer a small number of meaningful control points. A 1000-point contour is usually worse for Agent iteration than a 12–30 point polygon/spline.

Use:
- straight edges → polygon
- organic contour → spline
- isolated curvature → bezier
- hair/grass/fur → repeated spline/line marks
- soft mass → filled polygon/circle + texture layer
- clear title/caption → text
- brush-calligraphy title → text-outline or spline approximation

## Z-order

Sort `layers` and elements by zIndex before drawing. Do not rely on accidental code order.
