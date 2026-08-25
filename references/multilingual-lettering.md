# Multilingual Lettering Guide

## 目標

讓 Agent 可以在圖畫上加入 **中、英、日、韓、泰文** 題字，同時兼顧：

- 可讀性
- 版面一致性
- 與插畫風格的融合
- 正確字型 fallback
- 安全 Unicode/UTF-8 輸出

## 基本流程

1. 取得文字內容與語言。
2. 決定文字角色：主標 / 副標 / 標籤 / 註記 / 簽名。
3. 決定放置區域與 bbox。
4. 選擇字型家族。
5. 選擇渲染模式：`p5-text`、`text-outline` 或 `mixed`。
6. 渲染後檢查：
   - 是否溢出 bbox
   - 是否斷行錯誤
   - 是否字體 fallback 到不合適的字
   - 是否和底圖對比太弱

## 語言與字型建議

| Language | Preferred Sans | Preferred Serif |
|---|---|---|
| zh-Hant | Noto Sans TC | Noto Serif TC |
| zh-Hans | Noto Sans SC | Noto Serif SC |
| en | Inter / Noto Sans | Noto Serif |
| ja | Noto Sans JP | Noto Serif JP |
| ko | Noto Sans KR | Noto Serif KR |
| th | Noto Sans Thai | Noto Serif Thai |

## 建議的 HTML 字型載入

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Noto+Sans+JP:wght@400;700&family=Noto+Sans+KR:wght@400;700&family=Noto+Sans+TC:wght@400;700&family=Noto+Sans+Thai:wght@400;700&display=swap" rel="stylesheet">
```

若需襯線，也可改載 Noto Serif 系列。

## p5 文字實作範例

```js
function drawTextBlock({content, x, y, w, h, fontFamily, size, color, align='left', valign='top', lineHeight=1.2}) {
  push();
  textFont(fontFamily);
  textSize(size);
  textLeading(size * lineHeight);
  fill(color);
  noStroke();

  const hAlign = align === 'center' ? CENTER : align === 'right' ? RIGHT : LEFT;
  const vAlign = valign === 'middle' ? CENTER : valign === 'bottom' ? BOTTOM : TOP;
  textAlign(hAlign, vAlign);

  const tx = align === 'center' ? x + w / 2 : align === 'right' ? x + w : x;
  const ty = valign === 'middle' ? y + h / 2 : valign === 'bottom' ? y + h : y;
  text(content, tx, ty, w, h);
  pop();
}
```

## 何時使用 text-outline

使用 `text-outline` 當：

- 使用者明確要求手寫感 / 書法感 / 筆刷字。
- 標題必須與插圖筆觸一致。
- 文字本身是畫面主體的一部分。

不要在以下情況優先用 outline：

- 小字說明
- 泰文小字
- 高密度資訊文字
- 必須極高可讀性且時間有限

## 多語混排建議

- 不同語言可各自成為獨立 text block，不一定硬塞進同一個 `text()`。
- 主標與副標可分兩層：例如中文主標 + 英文副標。
- 若同一區塊混排，需檢查 baseline 與 line height。
- 泰文避免過小字級；常比同級英文略大 5–10%。
- 日文 / 中文標題可使用較緊的 tracking；英文全大寫時可略增 letter spacing。

## 驗收檢查表

- 文字內容與使用者要求完全一致。
- 無亂碼、問號、缺字。
- 語言標記正確。
- 字型 fallback 合理。
- 題字位置不遮擋關鍵主體（除非使用者要求）。
- 對比足夠，仍可讀。
- 如果是雙語或多語，層級清楚。
