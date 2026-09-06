# p5 Rendering Guide for Agents

## Scene Plan 與範例 runtime

完整 Schema 是 renderer-neutral 的計畫格式，不是「所有策略都有內建 renderer」的承諾。shared runtime 位於 `examples/shared/painter.js`，由兩個範例的 async setup 呼叫 `Painter.prepare()`，draw 呼叫 `Painter.render()`。

範例使用 normalized canvas 座標；bbox 為 `[x,y,w,h]`，geometry.points 的每個 `[x,y]` 也相對整張 canvas（不是相對 bbox）。layers / elements 均依 zIndex 穩定排序，相同 zIndex 保留原順序。字型大小與 strokeWeight 使用像素/brush 權重，不是 normalized 比例。

| drawStrategy | 範例需要的資料 |
|---|---|
| primitive | bbox；geometry.kind 為 rect 或 circle |
| polygon / watercolor | bbox；geometry.points 至少 3 點 |
| spline | bbox；geometry.points 至少 2 點，可選 curvature |
| repeated-marks | bbox；geometry.count（0–10000），在 bbox 內繪製固定 seed 的草狀線段 |
| text | bbox；text.content、language、font；可選文字排版欄位 |

style 支援 fill、opacity（0–255）、bleed、stroke、strokeWeight、brush；`style.medium: p5` 強制該形狀用原生 p5。`renderer: p5` 時全部用原生繪製；其 spline 是有警告的 polyline 近似，不冒充 brush spline。

範例不支援 interleaved text：所有題字須位於最後，並先渲染至 P2D 文字層。unsupported strategy、standalone 或 text-outline 會報錯，請另外生成相應程式。畫布限制每邊 8192、總計 16 megapixels，是範例保護，不是 Schema 的通用上限。

## 座標與可重現性

p5 P2D 原點在左上；WEBGL 原點在中心。draw 開始 push，WEBGL 平移一次 `translate(-width/2,-height/2)`，結束 pop。不能在 setup 平移後假定下一幀仍保留。

每次 draw 重設 randomSeed/noiseSeed；brush.scaleBrushes 只在 setup 執行一次。固定 pixelDensity(1) 防止 Retina 或系統縮放偷偷改變 PNG 實際尺寸。固定依賴、seed、字型與環境後再比較圖片；不同 GPU 不保證逐像素一致。

## 文字與版面

使用 `text.content`，不要在 sketch 再硬編碼另一份。bbox 轉像素後，水平/垂直 anchor 只計算一次。原生 p5 的 boxed text 與 single-point text 有不同定位語意，不要先加半個 bbox，再讓 boxed text 重複置中。

共用 drawTextBlock 使用 native Canvas2D metrics 計算整行的 ascent、descent、寬度與 leading，在 P2D 畫好後以 image 合成。明確換行 `\n` 才分行，不做未知語言的自動斷字。超出 bbox 時縮小字級並留下 warning；文字旋轉以 bbox 中心為基準，旋轉後是否超出畫布仍須視覺確認。

更複雜的字形輪廓、bezier、freehand、mass、hatch、紋理與局部編輯請保留穩定 element ID，讓 Agent 寫對應 renderer。不要以大量無意義控制點掩蓋不準確輪廓。

官方文件：https://p5js.org/reference/p5/textFont/ 、https://p5js.org/reference/p5/randomSeed/
