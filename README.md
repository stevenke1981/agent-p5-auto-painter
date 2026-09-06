# Agent p5 Auto Painter Skill

「圖片觀察 → Scene Plan → p5.js / p5.brush 程式繪圖 → 視覺驗收 → 局部迭代」的 Agent 技能包，支援 reconstruct、stylize、text-to-drawing、edit-existing 與多語題字。

**這是技能包與可執行範例，不是自帶 AI 模型的圖片轉換服務。** 圖片理解、輪廓提取與進階程式生成由使用此 Skill 的 Agent 完成；範例 runtime 不會將任意圖片自動轉成畫作。

## 開始使用

將整個 repository 放在 Agent 可讀取的 skills 目錄，入口為 [SKILL.md](SKILL.md)，不要只複製單一檔案。向 Agent 提供參考圖及精確題字，例如：

> 使用 agent-p5-auto-painter，把這張圖片重建成可編輯的 p5.brush 程式。右上角加入「夏日散步」與英文副標「Summer Walk」。先對齊構圖與輪廓，再處理水彩質感，最多迭代 4 輪。保留原始檔，將成果另存。

有參考圖時先產出 `scene-analysis.json`；所有模式都要有 `scene-plan.json`、可執行程式及驗證結果。繁體中文不得擅自轉成簡體，文字內容不得為了字型而改寫。

## 執行範例

需要 Python 3.10+、可使用 WebGL2 的瀏覽器，以及網路連線載入固定版本的 p5.js / p5.brush。驗證工具另外需要 `jsonschema`。

```sh
python -m pip install -r requirements.txt
python scripts/validate_scene.py examples/basic/scene-plan.json
python scripts/validate_scene.py examples/multilingual-lettering/scene-plan.sample.json
python -m http.server 8000 --bind 127.0.0.1
```

在專案根目錄執行 server，再開啟：

- 基本水彩風景：`http://127.0.0.1:8000/examples/basic/`
- 中、英、日、韓、泰題字：`http://127.0.0.1:8000/examples/multilingual-lettering/`

Windows 也可使用以上指令；若 Python launcher 是 `py`，將 `python` 換成 `py -3`。不要直接雙擊 HTML：範例需要以 HTTP 讀取 Scene Plan。

修改範例旁的 JSON 後重新整理即可。畫布尺寸、背景、seed、圖層、幾何及題字都從 Scene Plan 讀取，不必在 sketch 重複改一份。繪製完成後按「下載 PNG」；載入失敗會顯示原因，不會假裝成功。

## 驗證與自動化

```sh
# Scene Plan：預設模式，保留既有指令用法
python scripts/validate_scene.py scene-plan.json
# 參考圖片分析
python scripts/validate_scene.py scene-analysis.json --kind analysis
# Agent 可讀取 JSON 診斷；path 為 - 時從 stdin 讀取
python scripts/validate_scene.py scene-plan.json --json
# 不需要 npm install 的回歸測試；需要 Node.js 22+
python -m unittest discover -s tests -v
node --test tests/runtime.test.cjs
```

驗證器只讀取檔案，使用 JSON Schema Draft 2020-12，再檢查跨圖層 ID、bbox 邊界、build/renderer 組合與來源長寬比。UTF-8 BOM 可讀取；重複 JSON key、非有限數值、錯誤型別與不合法 Unicode 編碼會報錯。exit code：`0` 通過、`1` 結構/語意不合格、`2` 檔案/JSON/環境錯誤。`--json` 會以 ASCII escape 輸出，JSON 解碼後文字不變，適用 Windows console。

### Chromium 實測

```sh
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python scripts/smoke_test.py
# 僅測原生 Canvas2D 題字對齊，不代表完整 p5 / WebGL 驗證
python scripts/smoke_test.py --text-only
```

完整 smoke test 檢查兩個範例、同 seed 重繪誤差、非空畫布、題字層、PNG 下載及 Scene Plan 404 錯誤提示；報告與截圖存於 `artifacts/`。`--executable` 可指定已安裝的 Chromium。重繪比較 decoded RGBA pixels：單一色階差最多 1/255，且變動像素不得超過 0.01%；報告會記錄是否完全相同、差異像素數與最大色階差。GitHub Actions 執行 Windows/Linux 驗證，以及 Linux Chromium 實測並保存證據。

## 多語題字與支援界線

字型依語言使用 Noto TC / SC / JP / KR / Thai，英文可用 Inter；支援 `zh-Hant`、`zh-Hans`、`en`、`ja`、`ko`、`th`。範例先等待 web fonts，再於 P2D / Canvas2D 文字層繪製並合成到 WebGL 畫布，避免直接在 WebGL 使用 CSS 字型名稱。

字型逾時或失敗會顯示 fallback 警告；**字型載入成功不等於每個字形都已人工確認**。泰文與結合字保持完整字串交由瀏覽器 shaping，不做逐字拆分。字級超出 bbox 時縮小並顯示警告；請在交付前檢查文字、斷行、缺字與對比。本庫不附帶字型檔；商用與重新散布請另行確認授權。

範例 runtime 支援 `primitive`（rect/circle）、`polygon`、`watercolor`、`spline`、`repeated-marks` 和最上層 `p5-text`；資料規格見 [rendering guide](references/p5-rendering-guide.md)。完整 Schema 仍可描述 bezier、freehand、hatch、mass、standalone 與 text-outline，這些需要 Agent 另外生成程式。範例遇到未實作策略會明確報錯，不會靜默略過。

固定 `seed` 及固定套件版本有助於同環境重現，但跨 GPU、作業系統或字型版本不保證逐像素一致。靜態驗證通過不代表視覺相似度或任意進階 geometry 均正確。

## 上游與授權

- https://github.com/jackbdu/p5-code-painter — 可編輯圖形模型的設計參考，MIT。
- https://github.com/acamposuribe/p5.brush — 自然媒材繪圖，MIT。
- https://p5js.org/ — p5.js 官方文件與授權資訊。

本包未複製上游 library 或字型原始碼；範例使用 CDN 的 `p5@2.2.0`、`p5.brush@2.2.2` 與 Google Fonts。離線使用需自行準備相同版本資產並調整載入路徑。上游授權不會自動授權本 repository；本次未替作者新增或變更授權條款。
