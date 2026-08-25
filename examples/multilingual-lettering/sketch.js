const CFG = { width: 1000, height: 700, seed: 42, bg: '#f6f1e8' };

function setup() {
  createCanvas(CFG.width, CFG.height, WEBGL);
  randomSeed(CFG.seed);
  noiseSeed(CFG.seed);
  brush.scaleBrushes(3);
  noLoop();
}

function draw() {
  background(CFG.bg);
  translate(-width / 2, -height / 2);
  drawBackground();
  drawFlower();
  drawLetteringLayer();
}

function drawBackground() {
  noStroke();
  fill('#e8dcc6');
  rect(0, 0, width, height);
  brush.set('HB', '#cab99f', 0.5);
  for (let i = 0; i < 20; i++) {
    brush.line(40, 30 + i * 30, width - 40, 20 + i * 30);
  }
}

function drawFlower() {
  push();
  brush.fill('#d36e70', 110);
  brush.fillBleed(0.08);
  brush.noStroke();
  const petals = [
    [420, 300], [500, 220], [580, 300], [500, 380]
  ];
  for (const [x, y] of petals) brush.circle(x, y, 85);
  brush.fill('#f4d26a', 130);
  brush.circle(500, 300, 60);
  brush.set('rotring', '#486244', 0.9);
  brush.line(500, 360, 500, 590);
  pop();
}

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

function drawLetteringLayer() {
  drawTextBlock({
    content: '夏日散步', x: 70, y: 60, w: 400, h: 70,
    fontFamily: 'Noto Sans TC', size: 40, color: '#2d241d'
  });
  drawTextBlock({
    content: 'Summer Walk', x: 72, y: 112, w: 360, h: 40,
    fontFamily: 'Inter', size: 26, color: '#6b5644'
  });
  drawTextBlock({
    content: '夏の散歩', x: 720, y: 70, w: 180, h: 50,
    fontFamily: 'Noto Sans JP', size: 28, color: '#2d241d', align: 'center'
  });
  drawTextBlock({
    content: '여름 산책', x: 720, y: 125, w: 180, h: 50,
    fontFamily: 'Noto Sans KR', size: 26, color: '#2d241d', align: 'center'
  });
  drawTextBlock({
    content: 'เดินเล่นหน้าร้อน', x: 640, y: 180, w: 280, h: 55,
    fontFamily: 'Noto Sans Thai', size: 28, color: '#2d241d', align: 'center'
  });
  brush.set('rotring', '#7b5d48', 0.7);
  brush.line(70, 155, 350, 155);
}
