# Agent p5 Auto Painter Skill

一個給 Agent 使用的「圖片辨識 → Scene Plan → p5.js / p5.brush 程式繪圖 → 視覺驗收 → 局部迭代」技能包。

## 特色

- 把圖片觀察與繪圖生成分離，降低模型直接猜 code 的漂移。
- 幾何層採 p5-code-painter 類似的可編輯 graphic model。
- 自然筆觸層採 p5.brush。
- 固定 seed、delta edit、區域式視覺修正。
- 內建 scene schema、prompt settings、Prompt Templates 與靜態 validator。
- 支援 reconstruct / stylize / text-to-drawing / edit-existing。
- **支援題字與版面文字**：可在圖畫上加入中、英、日、韓、泰文。
- **支援多語字型策略**：預設使用 Noto 字型家族與安全 fallback。

## 快速使用

1. 把整個資料夾放進 Agent 的 skills 目錄。
2. 將參考圖片提供給 Agent。
3. 若有題字需求，直接把文字內容、語言、位置、風格一併交給 Agent。
4. 指令範例：

   `使用 agent-p5-auto-painter，把這張圖片重建成可編輯的 p5.brush 程式，右上角加上「夏日散步」與英文副標 "Summer Walk"，先對齊構圖與輪廓，再做水彩質感，最多迭代 4 輪。`

5. Agent 應先產生 `scene-analysis.json` 與 `scene-plan.json`，再產生 `sketch.js`。

## 新增的多語題字能力

- 中文：繁中 / 簡中皆可
- English
- 日本語
- 한국어
- ไทย

建議 Agent 於 Scene Plan 使用 `element.type = "text"`，並填入：

- `content`
- `language`
- `font.family`
- `font.size`
- `position` / `bbox`
- `fill` / `stroke`
- `renderMode`（`p5-text` 或 `text-outline`）

若任務需要高度忠實的排版，可先用 `p5.text()` 題字；若需要手寫/筆刷感，則可將文字輪廓轉為 `polygon/spline` 後再以 p5.brush 描線。

## 上游參考

- https://github.com/jackbdu/p5-code-painter — MIT
- https://github.com/acamposuribe/p5.brush — MIT

本包未複製上游 library 原始碼；執行範例透過 CDN 使用 p5.js/p5.brush 與 Google Fonts / Noto 字型。
