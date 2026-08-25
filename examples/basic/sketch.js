const CFG = {
  width: 720,
  height: 480,
  seed: 42,
  background: '#f3ead7',
};

function setup() {
  createCanvas(CFG.width, CFG.height, WEBGL);
  randomSeed(CFG.seed);
  noiseSeed(CFG.seed);
  brush.scaleBrushes(3.2);
  noLoop();
}

function draw() {
  background(CFG.background);
  translate(-width / 2, -height / 2);
  drawWash();
  drawLandscape();
  drawInk();
}

function drawWash() {
  brush.noStroke();
  brush.fill('#a8c5d1', 85);
  brush.fillBleed(0.12);
  brush.polygon([[0,0],[720,0],[720,300],[0,310]]);
}

function drawLandscape() {
  brush.noStroke();
  brush.fill('#71876b', 115);
  brush.fillBleed(0.08);
  brush.polygon([[0,310],[120,240],[235,305],[360,210],[505,300],[620,245],[720,300],[720,480],[0,480]]);
}

function drawInk() {
  brush.set('HB', '#28302c', 0.9);
  brush.spline([[0,310],[120,240],[235,305],[360,210],[505,300],[620,245],[720,300]], 0.35);

  brush.set('HB', '#51453d', 0.55);
  for (let i = 0; i < 80; i++) {
    const x = random(20, 700);
    const y = random(330, 465);
    brush.line(x, y, x + random(-6, 6), y - random(4, 15));
  }
}
