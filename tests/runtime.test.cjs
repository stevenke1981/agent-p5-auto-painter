const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const P = require('../examples/shared/painter.js');
const basic = () => JSON.parse(fs.readFileSync(path.join(__dirname, '../examples/basic/scene-plan.json'), 'utf8'));
const multilingual = () => JSON.parse(fs.readFileSync(path.join(__dirname, '../examples/multilingual-lettering/scene-plan.sample.json'), 'utf8'));
test('normalized boxes become pixels', () => assert.deepEqual(P.pixelBox([.1,.2,.3,.4],1000,700),[100,140,300,280]));
test('invalid boxes fail instead of coercing', () => {
  for (const bbox of [null, 'abcd', [0,0,'1',1], [0,0,0,1], [0,0,Infinity,1]]) assert.throws(() => P.pixelBox(bbox,100,100));
});
test('stable z-order without mutation', () => {
  const plan = { layers: [{id:'b',zIndex:2,elements:[{id:'c',zIndex:3},{id:'b',zIndex:1}]},{id:'a',zIndex:1,elements:[{id:'a'}]}] };
  const before = JSON.stringify(plan);
  assert.deepEqual(P.orderedElements(plan).map(e=>e.id), ['a','b','c']); assert.equal(JSON.stringify(plan),before);
});
test('centered text anchor is applied exactly once', () => assert.deepEqual(P.textAnchor([100,50,200,60],'center','middle',20,15), [200,85]));
test('right and bottom anchors', () => assert.deepEqual(P.textAnchor([100,50,200,60],'right','bottom',20,15), [300,105]));
test('left and top anchors', () => assert.deepEqual(P.textAnchor([100,50,200,60],'left','top',20,15), [100,65]));
test('font CSS quotes named families and preserves fallback', () => assert.equal(P.fontSpec({family:['Noto Sans TC','sans-serif'],size:40,weight:700}), 'normal 700 40px "Noto Sans TC", sans-serif'));
test('both examples pass demo preflight', () => { P.validateDemo(basic()); P.validateDemo(multilingual()); });
test('all five demo languages have exact plan text', () => assert.deepEqual(P.orderedElements(multilingual()).filter(e=>e.text).map(e=>e.text.content), ['夏日散步','Summer Walk','夏の散歩','여름 산책','เดินเล่นหน้าร้อน']));
test('standalone and unknown renderers are rejected', () => {
  let plan=basic(); plan.build='standalone'; assert.throws(()=>P.validateDemo(plan));
  plan=basic(); plan.renderer='canvas'; assert.throws(()=>P.validateDemo(plan));
});
test('demo allocation is bounded', () => {
  const plan=basic(); plan.canvas.width=8192; plan.canvas.height=8192; assert.throws(()=>P.validateDemo(plan));
});
test('unsupported advanced strategies do not silently disappear', () => {
  const plan=basic(); plan.layers[0].elements[0].drawStrategy='mass'; assert.throws(()=>P.validateDemo(plan));
});
test('outline conversion is never claimed by demo', () => {
  const plan=multilingual(); plan.layers.at(-1).elements[0].text.renderMode='text-outline'; assert.throws(()=>P.validateDemo(plan));
});
test('interleaved text is rejected explicitly', () => {
  const plan=multilingual(); plan.layers.push({...basic().layers[0],zIndex:99}); assert.throws(()=>P.validateDemo(plan));
});
test('invalid points fail before brush rendering', () => {
  for (const points of [[], [[0,0]], [[0,0],[1,1],[NaN,0]], [[0,0],[1,1],['0',0]]]) {
    const plan=basic(); plan.layers[0].elements[0].geometry.points=points; assert.throws(()=>P.validateDemo(plan));
  }
});
test('mark count is bounded', () => {
  const plan=basic(); plan.layers.at(-1).elements.at(-1).geometry.count=10001; assert.throws(()=>P.validateDemo(plan));
});
test('HTML pins full library versions and loads shared runtime first', () => {
  for (const dir of ['basic','multilingual-lettering']) {
    const html=fs.readFileSync(path.join(__dirname,'../examples',dir,'index.html'),'utf8');
    assert.match(html,/p5@2\.2\.0\/lib\/p5\.min\.js/); assert.match(html,/p5\.brush@2\.2\.2\/dist\/p5\.brush\.js/);
    assert.doesNotMatch(html,/@latest/); assert.ok(html.indexOf('../shared/painter.js')<html.indexOf('p5@2.2.0'));
  }
});
test('PNG export receives HTMLCanvasElement and reports synchronous export errors', async () => {
  const vm = require('node:vm');
  const button = {}, status = {}, element = { setAttribute() {} };
  const canvas = { elt: element, parent() {} };
  const scene = { canvas: { width: 64, height: 64 }, seed: 42, renderer: 'p5', layers: [] };
  let saved;
  const context = {
    location: { protocol: 'http:' }, setTimeout, clearTimeout,
    document: { fonts: { load: async () => [] }, getElementById: id => id === 'download' ? button : status },
    fetch: async () => ({ ok: true, json: async () => scene }),
    pixelDensity() {}, noLoop() {}, createCanvas: () => canvas,
    createGraphics: () => ({ pixelDensity() {} }),
    saveCanvas: (...args) => { saved = args; }, P2D: 'p2d'
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../examples/shared/painter.js'), 'utf8'), context);
  await context.Painter.prepare('scene-plan.json');
  button.onclick();
  assert.equal(saved[0], element);
  assert.deepEqual(saved.slice(1), ['agent-p5-painting', 'png']);
  context.saveCanvas = () => { throw Error('export failed'); };
  button.onclick();
  assert.equal(context.Painter.state.error, 'export failed');
  assert.equal(button.disabled, true);
});
