#!/usr/bin/env python3
"""Real Chromium checks. --text-only needs no network and does not test p5/WebGL."""
from __future__ import annotations
import argparse
import functools
import hashlib
import http.server
import json
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def text_probe(browser, output):
    page = browser.new_page(viewport={'width': 720, 'height': 480})
    try:
        page.set_content('<canvas id="probe" width="720" height="480"></canvas>')
        page.add_script_tag(path=str(ROOT / 'examples/shared/painter.js'))
        results = page.evaluate('''() => {
          const canvas = document.querySelector('canvas'), ctx = canvas.getContext('2d');
          const results = [];
          for (const align of ['left','center','right']) {
            for (const verticalAlign of ['top','middle','bottom']) {
              ctx.clearRect(0,0,720,480);
              Painter.drawTextBlock({drawingContext:ctx}, {id:'probe',bbox:[.1,.1,.8,.8],text:{
                content:'Summer Walk',font:{family:'sans-serif',size:48},align,verticalAlign
              }}, {canvas:{width:720,height:480}});
              const pixels=ctx.getImageData(0,0,720,480).data;
              let minX=720,minY=480,maxX=-1,maxY=-1;
              for(let y=0;y<480;y++) for(let x=0;x<720;x++) if(pixels[(y*720+x)*4+3]) {
                minX=Math.min(minX,x); maxX=Math.max(maxX,x); minY=Math.min(minY,y); maxY=Math.max(maxY,y);
              }
              if(maxX<minX || minX<70 || maxX>650 || minY<46 || maxY>434) throw Error('text overflow/empty');
              if(align==='center' && Math.abs((minX+maxX)/2-360)>4) throw Error('double center offset');
              results.push({align,verticalAlign,bounds:[minX,minY,maxX,maxY]});
            }
          }
          return results;
        }''')
        page.screenshot(path=str(output / 'text-layout.png'))
        return {'mode': 'text-only', 'checks': len(results), 'details': results,
                'scope': 'Native Canvas2D layout; not p5, brush, downloadable fonts, or glyph coverage'}
    finally:
        page.close()


def full_probe(browser, base, output):
    results = []
    for name in ('basic', 'multilingual-lettering'):
        page = browser.new_page(viewport={'width': 1200, 'height': 950}, device_scale_factor=1)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_default_timeout(60000)
        try:
            page.goto(f'{base}/examples/{name}/', wait_until='load')
            page.wait_for_function('window.__PAINTER__ && (__PAINTER__.ready || __PAINTER__.error)')
            state = page.evaluate('window.__PAINTER__')
            if state['error'] or errors:
                raise AssertionError(f'{name}: {state["error"] or errors}')
            canvas = page.locator('#artwork canvas')
            canvas.screenshot(path=str(output / f'{name}.png'))
            before = canvas.evaluate('(el) => el.toDataURL()')
            # p5 must reproduce the identical framebuffer on an explicit redraw.
            page.evaluate('async () => { Painter.state.ready = false; await redraw(); }')
            page.wait_for_function('window.__PAINTER__.ready || window.__PAINTER__.error')
            if page.evaluate('window.__PAINTER__.error'):
                raise AssertionError('redraw reported an error')
            after = canvas.evaluate('(el) => el.toDataURL()')
            if before != after:
                raise AssertionError(f'{name}: fixed-seed redraw differs')
            stats = canvas.evaluate('''el => {
              const c=document.createElement('canvas'); c.width=el.width; c.height=el.height;
              const g=c.getContext('2d'); g.drawImage(el,0,0); const a=g.getImageData(0,0,c.width,c.height).data;
              const colors=new Set(); for(let i=0;i<a.length;i+=64) colors.add(`${a[i]},${a[i+1]},${a[i+2]}`);
              return {width:c.width,height:c.height,colors:colors.size};
            }''')
            if stats['colors'] < 8: raise AssertionError(f'{name}: blank/near-empty canvas')
            if name == 'multilingual-lettering':
                count = page.evaluate('''() => {
                  const g=prepared.text, a=g.drawingContext.getImageData(0,0,g.width,g.height).data;
                  let n=0; for(let i=3;i<a.length;i+=4) if(a[i]) n++; return n;
                }''')
                if count < 100: raise AssertionError('lettering layer is empty')
            with page.expect_download() as download:
                page.get_by_role('button', name='下載 PNG').click()
            saved = output / f'{name}-download.png'
            download.value.save_as(saved)
            if saved.read_bytes()[:8] != b'\x89PNG\r\n\x1a\n': raise AssertionError('download is not PNG')
            results.append({'example': name, 'stats': stats, 'deterministicRedraw': True,
                            'download': True, 'warnings': state['warnings'],
                            'sha256': hashlib.sha256(saved.read_bytes()).hexdigest()})
        finally:
            page.close()
    # A missing Scene Plan must surface as an error, not an endlessly blank page.
    page = browser.new_page()
    try:
        page.route('**/scene-plan.json', lambda route: route.fulfill(status=404, body='missing'))
        page.goto(f'{base}/examples/basic/', wait_until='load')
        page.wait_for_function('window.__PAINTER__ && __PAINTER__.error')
        assert '404' in page.locator('#status').inner_text()
        assert page.locator('#download').is_disabled()
    finally:
        page.close()
    return {'mode': 'full', 'examples': results, 'missingPlanError': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--text-only', action='store_true')
    parser.add_argument('--executable', help='Optional installed Chromium executable')
    parser.add_argument('--output', type=Path, default=ROOT / 'artifacts')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    from playwright.sync_api import sync_playwright
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    report = {'passed': False}
    try:
        with sync_playwright() as p:
            options = {'headless': True, 'args': ['--use-angle=swiftshader', '--enable-unsafe-swiftshader']}
            if args.executable: options['executable_path'] = args.executable
            browser = p.chromium.launch(**options)
            try:
                report['text'] = text_probe(browser, args.output)
                if not args.text_only:
                    report['render'] = full_probe(browser, f'http://127.0.0.1:{server.server_port}', args.output)
                report['passed'] = True
            finally:
                browser.close()
    except Exception as exc:
        report['error'] = str(exc)
    finally:
        server.shutdown(); server.server_close()
        (args.output / 'smoke-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__': raise SystemExit(main())
