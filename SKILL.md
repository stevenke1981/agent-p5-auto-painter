---
name: agent-p5-auto-painter
description: Automatically reconstruct, stylize, or create drawings from reference images or text using image understanding, p5.js geometry, p5.brush natural media, and multilingual lettering. Produces deterministic code, render plans, and iterative visual corrections.
version: 1.1.0
language: zh-TW
---

# Agent p5 Auto Painter

## 目的

讓 Agent 能把「看懂圖片」轉成「可重現、可修改、可迭代的程式繪圖」。核心不是直接猜 p5.js，而是先建立可驗證的 Scene Plan，再生成 p5.js / p5.brush 程式碼，渲染後重新觀察結果並修正。

本 Skill 蒸餾自兩類能力：

- **p5-code-painter 思想**：圖形物件與可重現 p5.js statement 對應；每個 rect / ellipse / line / bezier / freehand 都有明確幾何參數。
- **p5.brush 能力**：在 p5.js 幾何之上加入 pencil、charcoal、marker、watercolor、hatch、spline、flow/vector field、custom brush 等自然媒材。
- **圖片辨識流程**：先實際查看輸入圖片與尺寸，再做 composition、elements、palette、z-order、geometry、texture、lighting 的結構化拆解；不憑檔名或文字描述猜座標。
- **多語題字流程**：讓 Agent 能把標題、副標、簽名、註記、章標、標籤加到圖畫上，並正確處理 **中 / 英 / 日 / 韓 / 泰文**。

## 何時使用

使用者要求以下任一工作時啟用：

- 把圖片轉成 p5.js / generative art / code drawing。
- 讓 Agent 自動照著參考圖畫圖。
- 產生手繪、水彩、鉛筆、麥克筆、炭筆或線稿風格。
- 把圖片簡化成幾何圖形、icon、海報、插圖、白板圖。
- 根據文字描述自動產生可執行的繪圖程式。
- 對現有 p5.js / p5.brush 圖面做視覺對齊與反覆修正。
- 在畫面上加入標題、題字、標籤、簽名、說明文字或雙語排版。

## 核心原則

1. **Observe before code**：有參考圖時，第一步必須看圖並確認原始寬高與長寬比。
2. **Structure before aesthetics**：先對齊構圖、比例、位置、z-order，再處理筆刷與質感。
3. **Geometry + Brush + Text 分層**：幾何描述「畫什麼」，brush 描述「怎麼畫」，text 描述「寫什麼、放哪裡、用哪種字型」。
4. **Deterministic first**：預設使用固定 seed；只有使用者要求完全隨機時才關閉。
5. **Region-wise iteration**：一次優先修正 1–3 個最大誤差區域，不重寫整張圖。
6. **No hidden text guessing**：圖片中的文字只有在明確可辨識且任務需要時才重建；否則保留為後製文字層或 placeholder。
7. **Prefer editable primitives**：能用 rect/circle/polygon/spline/text element 表達時，不要先 rasterize。
8. **Visual validation is mandatory**：若環境能渲染/截圖，至少做一次 render → observe → revise。
9. **Unicode-safe output**：所有題字內容必須以 UTF-8 儲存；禁止因字型或編碼問題把多語內容改寫成問號或拼音。

## 預設工作模式

讀取 `templates/prompt-settings.yaml`。預設：

- mode: `reconstruct`
- renderer: `p5-brush`
- canvas: 跟隨參考圖比例；無參考圖則 1024×1024
- seed: 42
- iteration_limit: 4
- coordinate_space: `top-left`
- fidelity_priority: `composition > silhouette > palette > text_layout > local detail > texture`

## 題字模式（Multilingual Lettering）

當使用者要求「題字 / 標題 / caption / label / 簽名 / bilingual / multilingual」時，Agent 必須額外做這幾件事：

1. 擷取或確認每段文字的：
   - `content`
   - `language`
   - `placement`
   - `priority`（主標 / 副標 / 章節標 / 裝飾字 / 註記）
   - `style`（clean / poster / handwriting / brush-calligraphy / stamp / caption）
2. 對每段文字建立獨立 text element。
3. 將文字納入 Scene Plan 與 z-order。
4. 如果是手寫感：
   - 可先以 `p5.text()` 定位，或
   - 轉為 outline/polygon/spline 再用 p5.brush 描線。
5. 如果是 CJK/Thai 等字型要求高的腳本，優先選 **Noto** 字型家族。

### 推薦字型對應

- zh-Hant / zh-TW：`Noto Sans TC`, `Noto Serif TC`
- zh-Hans：`Noto Sans SC`, `Noto Serif SC`
- en：`Inter`, `Noto Sans`, `Noto Serif`
- ja：`Noto Sans JP`, `Noto Serif JP`
- ko：`Noto Sans KR`, `Noto Serif KR`
- th：`Noto Sans Thai`, `Noto Serif Thai`

### 題字渲染策略

#### A. p5-text（預設）
適合：海報標題、說明文字、清楚可讀的 caption。

- 使用 `textFont()`、`textSize()`、`textAlign()`、`textLeading()`。
- 若字型需載入，使用 `preload()` + `loadFont()`，或在 HTML 引入 web font。
- 以單獨 `drawLetteringLayer()` 繪製。

#### B. text-outline
適合：手寫感、筆刷感、需要與整體插畫風格一致。

- 將文字轉為輪廓 path（若環境可取得字形輪廓）。
- 轉成 `polygon` / `spline` 後以 p5.brush 或 p5 primitives 繪製。
- 無法安全取得輪廓時，允許回退到 `p5-text`。

#### C. mixed
主標題用 `text-outline`，小字說明用 `p5-text`。

## 執行流程

### Phase 0 — Intent

判斷輸入屬於：

- `reference-reconstruct`：照參考圖重建。
- `reference-stylize`：保留構圖，改變媒材/風格。
- `text-to-drawing`：文字直接生成圖。
- `edit-existing`：修改既有 sketch。
- `add-lettering`：在現有圖面上加入題字。

如果資訊足夠，不要為小缺項打斷流程；使用合理預設並記錄在 Scene Plan。

### Phase 1 — Image Observation

有圖片時，輸出 `scene-analysis.json`，至少包含：

- source dimensions / aspect ratio
- dominant palette
- background
- major regions
- subjects / objects
- existing visible text (only if legible)
- bounding boxes
- silhouette / contour
- line characteristics
- texture/material
- lighting/shadow
- z-order
- uncertainty

必須使用 `schemas/scene-analysis.schema.json` 的欄位語意。

### Phase 2 — Scene Planning

把觀察結果轉成 renderer-neutral Scene Plan：

- canvas
- palette
- layers[]
- elements[]
- each element: id, semantic role, bbox, anchor, geometry, stroke, fill, texture, zIndex
- **text element**: content, language, font, alignment, lineHeight, letterSpacing, rotation, renderMode
- drawStrategy: primitive / polygon / bezier / spline / repeated-marks / watercolor / hatch / text

先建立大形，再建立小形。不要直接把每個像素都當成獨立圖元。

### Phase 3 — Renderer Selection

#### 使用純 p5.js，當：

- 風格偏 flat/vector/geometric。
- 主要是 rect/circle/ellipse/line/bezier/polygon。
- 需要最大可編輯性與簡單輸出。
- 題字以清晰可讀為主。

#### 使用 p5.brush，當：

- 有鉛筆、炭筆、麥克筆、水彩、手繪輪廓、hatch、自然抖動。
- 需要 `brush.spline()`、`brush.fill()`、`brush.hatch()`、`brush.mass()`、vector field。
- 題字要與畫風融合，具筆刷感或手寫感。

#### 混合模式，當：

- 大色塊/精準幾何用 p5.js。
- 輪廓、陰影、質感、手繪線用 p5.brush。
- 清楚小字用 p5 `text()`，主標則轉 outline 以 p5.brush 描出。

### Phase 4 — Code Generation

生成程式前讀：

- `references/p5-rendering-guide.md`
- `references/p5-brush-agent-guide.md`
- `references/multilingual-lettering.md`

p5.brush 的 p5 build 預設規則：

```js
createCanvas(W, H, WEBGL);
translate(-width / 2, -height / 2);
brush.scaleBrushes(scale);
randomSeed(seed);
noiseSeed(seed);
```

注意 WEBGL 原點位於中心；Scene Plan 使用 top-left 座標時，必須平移回左上角座標系。

生成碼時：

- 每個元素使用穩定 `id` 對應註解。
- 將 palette、canvas、seed、quality 放在頂部 constants。
- 將每個主要 layer 拆成函式，例如 `drawBackground()`, `drawSubject()`, `drawTexture()`, `drawLetteringLayer()`。
- 大量重複元素用 loop/data array，不複製貼上數十行。
- 參數優先從 `scene-plan.json` 讀取或可被局部替換。
- 題字內容一律使用 UTF-8 literal 或可安全的 JSON string。

### Phase 5 — Render Validation

若可渲染：

1. 執行 sketch。
2. 擷取 canvas screenshot。
3. 再次用圖片理解比較 reference 與 render。
4. 輸出 `visual-diff.json`。
5. 每輪只修改最高優先誤差。

比較順序：

1. canvas / aspect ratio
2. composition / margins
3. subject silhouette
4. relative size and position
5. major colors
6. text placement / readability / line breaks
7. contour / stroke character
8. local details
9. texture/noise

### Phase 6 — Acceptance

成功條件：

- 無 runtime error。
- 所有元素 bbox 不越界，除非 Scene Plan 明確標示允許裁切。
- layer zIndex 可排序且 element id 唯一。
- 相同 seed 產生可重現結果。
- p5.brush build 使用方式正確。
- 多語文字在輸出檔中維持正確 Unicode。
- 至少一次視覺驗收（若環境可 screenshot）。
- 最終交付包含程式碼 + Scene Plan + 可選 preview。

## p5.brush Build 選擇規則

### p5 build（本 Skill 預設）

- 需要 p5.js 2.x。
- `createCanvas(w,h,WEBGL)`。
- transforms 使用 p5 的 `push/pop/translate/rotate/scale`。
- seed 使用 `randomSeed()` / `noiseSeed()`。
- 不需要 `brush.render()`。

### standalone build

只有使用者明確要求不用 p5.js 時使用。

- `brush.createCanvas()`。
- transforms 使用 `brush.push/pop/translate/rotate/scale`。
- seed 使用 `brush.seed()` / `brush.noiseSeed()`。
- 每 frame 最後必須 `brush.render()`。

**禁止混用兩套 lifecycle。**

## 自動修正策略

每輪建立錯誤清單：

- `layout_error`
- `scale_error`
- `shape_error`
- `palette_error`
- `text_layout_error`
- `text_legibility_error`
- `stroke_error`
- `texture_error`
- `detail_missing`

依 `impact × confidence` 排序。每輪最多修前三項。

若錯誤來自幾何，不要靠增加 noise 掩蓋。
若錯誤來自筆觸，不要破壞已正確的 geometry。
若錯誤來自字型或斷行，優先修 `font / textSize / bbox / align / leading`，不要先動整體構圖。
若整體已相似，只做 delta edit。

## 輸出檔案建議

```text
output/
  scene-analysis.json
  scene-plan.json
  sketch.js
  preview.png
  visual-diff.json
```
