# Multilingual Lettering Guide

保留使用者 exact text 與 UTF-8，不擅自繁簡轉換、翻譯或用拼音代替缺字。圖片上無法辨識的文字列入 uncertainty，不猜測重建。

## 字型策略

| language | Sans | Serif |
|---|---|---|
| zh-Hant | Noto Sans TC | Noto Serif TC |
| zh-Hans | Noto Sans SC | Noto Serif SC |
| en | Inter / Noto Sans | Noto Serif |
| ja | Noto Sans JP | Noto Serif JP |
| ko | Noto Sans KR | Noto Serif KR |
| th | Noto Sans Thai | Noto Serif Thai |

可以使用使用者合法提供的其他字型。本庫不分發字型檔，也不保證系統已有 Noto。web fonts 需要網路；離線使用須準備合法字型資產及正確 @font-face。

## 正確渲染方式

WEBGL 的 textFont 不能直接依賴 CSS 字型名稱；使用 loadFont 所得物件，或在 P2D / Canvas2D 圖層繪製後合成。範例使用後者，保留瀏覽器對泰文與 combining marks 的 shaping。

不要只等待 document.fonts.ready：未請求的 font face 可能尚未下載。先對每個文字區塊呼叫 `document.fonts.load(fontSpec, content)`，以內容觸發 Google Fonts unicode-range 子集載入。範例最多等待 8 秒，載入失敗、逾時或只使用系統 fallback 會在狀態列警告。

字型載入成功不代表每個字形都有覆蓋；仍須實際檢查中文字形、韓文、日文及泰文上下標。fallback 可能讓構圖或寬度改變，最終畫面不能只憑 API 回傳值判定。

`Painter.drawTextBlock()` 使用整行 fillText 與 metrics；水平 align / 垂直 verticalAlign 各算一次。font.weight、font.style、lineHeight、rotation、letterSpacing 從 Scene Plan 讀取。瀏覽器不支援 native letterSpacing 時明確報錯，不能拆散泰文來模擬。明確換行才斷行；字級縮小會留下 warning，不能默默改文字內容。

## 輪廓文字與手寫

`text-outline` 適合已取得輪廓且需要筆刷外框的標題；outline 不等於筆順。中文書寫筆順與泰文 shaping 不能靠任意拆字或字形描邊推定。`mixed` 應拆為可分別驗證的文字區塊。

shared demo runtime 只實作 p5-text。Agent 使用輪廓工具、進階排版或自訂 renderer 後，必須驗證產物；沒有實作就明示 fallback，不把 enum 存在當成可執行能力。

## 驗收

逐項確認原文、繁簡、缺字、baseline、換行、bbox、旋轉後邊界、對比與主體遮擋。視覺相似度與字形正確性是人工/視覺模型檢查；靜態測試只保證結構與部分排版計算。

官方文件：https://p5js.org/reference/p5/textFont/ 、https://developer.mozilla.org/en-US/docs/Web/API/FontFaceSet/load
