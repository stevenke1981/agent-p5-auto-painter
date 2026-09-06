let prepared;
async function setup() {
  try { prepared = await Painter.prepare('scene-plan.json'); }
  catch (error) { noLoop(); Painter.fail(error); }
}
function draw() {
  if (!prepared || Painter.state.error) return;
  try { Painter.render(prepared); }
  catch (error) { noLoop(); Painter.fail(error); }
}
