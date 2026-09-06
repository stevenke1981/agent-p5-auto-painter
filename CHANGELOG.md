# Changelog

## 1.2.0 — 2026-09-07

- 使用 JSON Schema Draft 2020-12，並增加 analysis 模式、JSON diagnostics、stdin 與明確 exit codes。
- 拒絕錯誤型別、重複 JSON key/element IDs、非有限數字、非法 bbox、缺漏題字與不相容 build；支援 UTF-8 BOM。
- 兩個範例以 Scene Plan 驅動，加入共用 runtime、固定 CDN 版本、狀態列、可用性文字與 PNG 下載。
- 修正 WEBGL/CSS font 題字路徑、文字重複置中、字型載入時序與 redraw seed 重設。
- 補齊多語範例的五種語言與實際幾何資料；未實作的進階策略明確報錯。
- 新增 Python/Node 回歸測試、Chromium smoke test、Windows/Linux CI 與可下載驗證證據。
- 明確區分 static、runtime、visual 驗收及字型、跨 GPU、進階 geometry 的能力界線。

## 1.1.0

- 原始公開版本：圖片觀察、Scene Plan、p5/brush 參考文件、多語題字範例與初版靜態驗證。
