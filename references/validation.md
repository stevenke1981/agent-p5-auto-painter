# Validation and Acceptance

## 三種不同的結果

**Static**：Draft 2020-12 + semantic validator 通過，只代表結構、型別、唯一 ID、normalized bbox、build/renderer 與來源比例等已檢查。自訂 geometry 的所有語意、畫面品質及字形不在這個保證內。

**Runtime**：實際執行對應版本的 p5/brush，沒有 pageerror，canvas 非空、尺寸正確、同 seed 重繪在嚴格像素容差內、PNG 可下載、錯誤路徑有訊息。

**Visual**：實際看過成果，對照原圖/brief，確認構圖、輪廓、色盤、題字、遮擋、筆觸及材質。不能拿測試綠燈替代看圖。

## 指令

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
node --test tests/runtime.test.cjs
python scripts/validate_scene.py examples/basic/scene-plan.json
python scripts/validate_scene.py examples/multilingual-lettering/scene-plan.sample.json
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python scripts/smoke_test.py
```

`--text-only` 是完全不需網路的原生 Canvas2D 對齊測試，不等於 p5、p5.brush、WebGL 或字型下載通過。`--executable` 可選已安裝的 Chromium。完整測試需要允許 localhost HTTP、外部 CDN 與字型連線；受環境限制時記錄 blocked，不能改標 passed。

完整 smoke test 的 screenshot、download PNG 及 `smoke-report.json` 在 artifacts/。GitHub Actions 保存 browser-evidence artifact，並測 Windows/Linux 的 Python/Node。依賴無法下載、渲染錯誤或 non-deterministic redraw 會使 browser job 失敗；字型 fallback 警告記錄在 report，字形覆蓋仍需視覺確認。

## 每次交付應記錄

來源 commit、修改的 element IDs、測試命令與 exit code、依賴版本、環境、實際看過的圖片及限制。若圖層、字型、文字或套件版本改動，重新做相應驗證；禁止沿用不相關 commit 的 CI 綠燈。

## 重繪像素容差

比較 decoded RGBA pixels，不比較 PNG 編碼。最大 channel delta 為 1/255，變動像素最多 0.01%；兩條件都要成立，不能以平均誤差掩蓋明顯局部改變。Chromium 實測曾在多語範例 700,000 像素中出現 7 個像素相差 1 級，其餘完全一致。保留 before/after PNG、redraw.json 與 exact 標記；超過限制一律失敗。容差判定本身有回歸測試。
