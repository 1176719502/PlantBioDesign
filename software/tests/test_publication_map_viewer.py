"""Execute the shipped viewer JS against controlled DOM geometry (Node required).

These checks complement real-browser layout/screenshots; they do not emulate SVG
text measurement or the browser Fullscreen API.
"""
import re
import shutil
import subprocess
import unittest

from services.publication_map_viewer import build_publication_map_viewer_html


HARNESS = r"""
const assert = require('node:assert/strict');
const vm = require('node:vm');
let source = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => source += chunk);
process.stdin.on('end', () => {
  const events = {}, buttons = {}, frames = new Map();
  let serial = 0, observer, fontReady;
  const classes = {add(){}, remove(){}, toggle(){}};
  const viewport = {
    clientWidth: 1038, clientHeight: 473, classList: classes,
    addEventListener(type, cb){events['viewport:' + type] = cb;},
    setPointerCapture(){}, getBoundingClientRect(){return {left:0, top:0};}
  };
  // Deliberately larger than the canvas; external labels must be included.
  const box = {x:-200, y:100, width:2400, height:3000};
  const svg = {
    viewBox:{baseVal:{width:5000, height:5000}},
    querySelectorAll(selector){return selector.includes('data-') ? [] : [background, feature];}
  };
  const background = {parentNode:svg, tagName:'rect',
    getAttribute(){return '100%';}, getBBox(){return {x:0,y:0,width:5000,height:5000};}};
  const feature = {parentNode:svg, tagName:'text', getAttribute(){return null;},
    getBBox(){return {...box};}};
  const stage = {style:{}, querySelector(){return svg;}};
  const output = {};
  const root = {dataset:{}, querySelector(selector){
    if (selector === '.map-viewer-viewport') return viewport;
    if (selector === '.map-viewer-stage') return stage;
    if (selector === '.map-viewer-scale') return output;
    return buttons[selector] ||= {classList:classes};
  }};
  const document = {getElementById(){return root;},
    addEventListener(type, cb){events['document:' + type] = cb;},
    fonts:{ready:{then(cb){fontReady = cb;}}}};
  vm.runInNewContext(source, {
    document, window:{addEventListener(type, cb){events['window:' + type] = cb;}},
    ResizeObserver: class {constructor(cb){observer = cb;} observe(n){assert.equal(n,viewport);}},
    requestAnimationFrame(cb){frames.set(++serial, cb); return serial;},
    cancelAnimationFrame(id){frames.delete(id);}
  });
  const flush = () => {const callbacks = [...frames.values()]; frames.clear(); callbacks.forEach(cb => cb());};
  const click = action => buttons['[data-action=' + action + ']'].onclick();
  const close = (actual, expected) => {
    for (const key of Object.keys(expected)) assert(Math.abs(actual[key]-expected[key]) < 1e-9, key);
  };
  const state = () => {
    const m = stage.style.transform.match(/translate\(([^p]+)px,([^p]+)px\) scale\(([^)]+)\)/);
    return {x:+m[1], y:+m[2], scale:+m[3]};
  };
  const contained = () => {
    const {x,y,scale} = state();
    assert(x + box.x*scale >= 11.999);
    assert(y + box.y*scale >= 11.999);
    assert(x + (box.x+box.width)*scale <= viewport.clientWidth-11.999);
    assert(y + (box.y+box.height)*scale <= viewport.clientHeight-11.999);
  };
  flush(); contained();
  assert(state().scale < .2, 'initial fit must work below both old scale floors');
  const initial = state();
  click('zoom-in'); assert(state().scale > initial.scale);
  click('zoom-out'); close(state(), initial);
  click('zoom-out'); close(state(), initial); // must not jump up to 20%
  click('zoom-in'); click('pan');
  events['viewport:pointerdown']({pointerId:1, clientX:10, clientY:10});
  events['viewport:pointermove']({pointerId:1, clientX:110, clientY:60});
  close(state(), {x:initial.x-(viewport.clientWidth/2-initial.x)*.25+100});
  events['viewport:pointerup'](); click('reset'); contained();
  assert.deepEqual(state(), initial, 'reset must restore complete fit');
  // Container-only resize (sidebar/tab), browser resize, and fullscreen transition.
  viewport.clientWidth = 600; observer(); observer();
  assert.equal(frames.size,1, 'coalesce repeated resize events');
  flush(); contained();
  viewport.clientWidth = 1920; viewport.clientHeight = 1035;
  events['document:fullscreenchange'](); flush(); contained();
  viewport.clientHeight = 473; events['window:resize'](); flush(); contained();
  // Hidden tabs cannot fit until they have geometry; showing the tab triggers fit.
  const visible = state(); viewport.clientWidth = 0; observer(); flush();
  assert.deepEqual(state(),visible);
  viewport.clientWidth = 1038; observer(); flush(); contained();
  box.width = 6000; fontReady(); flush(); contained();
  click('zoom-in'); click('fit'); contained();
  assert(state().scale > (viewport.clientHeight-24)/5000,
    'full-canvas background must not create unnecessary whitespace');
  console.log('Viewer geometry, controls, resize, fullscreen event and font checks passed');
});
"""


class PublicationMapViewerTests(unittest.TestCase):
    def test_source_svg_is_preserved(self):
        svg = '<svg viewBox="0 0 1800 1200"><text x="-10">ALB &amp; label</text></svg>'
        self.assertIn(svg, build_publication_map_viewer_html(svg, viewer_id='test'))

    @unittest.skipUnless(shutil.which('node'), 'Node.js required for viewer JS execution')
    def test_geometry_and_interaction(self):
        html = build_publication_map_viewer_html('<svg></svg>', viewer_id='test')
        script = re.search(r'<script>([\s\S]*?)</script>', html).group(1)
        result = subprocess.run([shutil.which('node'), '-e', HARNESS],
                                input=script, text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
