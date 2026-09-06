# p5.brush Agent Guide

## 固定版本與 build

範例使用以下組合，升級必須重新執行 browser smoke test：

```html
<script src="https://cdn.jsdelivr.net/npm/p5@2.2.0/lib/p5.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/p5.brush@2.2.2/dist/p5.brush.js"></script>
```

p5 build：p5.js 2.x、WEBGL canvas、p5 push/pop/translate、randomSeed/noiseSeed；每幀自動 flush，不需要 brush.render。standalone：不用 p5，但需 WebGL2、brush.createCanvas/seed/transforms，且每幀末尾 brush.render。只有使用者明確要求時才採用 standalone；範例不實作它。

brush.scaleBrushes(3) 是約 600–1000 像素畫布的起始調整，不是通用最佳值；在 setup 執行一次，再視覺確認。不要每次 redraw 重複累乘。

## 常用 API

```js
brush.set('HB', '#222', 1);
brush.line(x1, y1, x2, y2);
brush.spline([[x1, y1], [x2, y2, 0.8], [x3, y3]], 0.5);
brush.noStroke();
brush.fill('#c8926b', 120); // opacity 0–255
brush.fillBleed(0.12);
brush.polygon(points);
```

brush.circle 第三參數是半徑；p5.circle 第三參數是直徑。轉換 renderer 時不能直接套用同一數值。

hatch、mass、vector fields、custom brushes 為 Agent 可進階生成的策略。使用前查對該版本官方 API，特別是角度單位、參數與 state。不要用 wiggle/noise 掩蓋幾何錯誤。

## 狀態與題字

每個獨立元素用 push/pop 隔離狀態，明確設定或關閉 stroke、fill、hatch、mass。需要最佳化時才合併相同 style 的批次，不可破壞 zIndex 順序。

題字先在 P2D / Canvas2D 完成 shaping 與字型載入，再合成；詳見 `multilingual-lettering.md`。不能在 WebGL 直接 `textFont('Noto Sans TC')` 就假設網頁字型可用。書法 outline 需要實際輪廓與驗證，不等於 brush 已有文字或筆順引擎。

官方來源：https://github.com/acamposuribe/p5.brush 、https://github.com/acamposuribe/p5.brush/releases
