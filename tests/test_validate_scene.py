import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('validator', ROOT / 'scripts/validate_scene.py')
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.plan = {'canvas': {'width': 100, 'height': 100}, 'seed': 42, 'renderer': 'p5',
                     'layers': [{'id': 'layer', 'zIndex': 0, 'elements': [
                         {'id': 'shape', 'drawStrategy': 'primitive', 'bbox': [0, 0, 1, 1]}]}]}
        self.el = self.plan['layers'][0]['elements'][0]
        self.analysis = {'source': {'width': 100, 'height': 50, 'aspectRatio': 2},
                         'composition': 'landscape', 'palette': ['#ffffff'], 'elements': [
                             {'id': 'sky', 'role': 'background', 'bbox': [0, 0, 1, 1], 'zIndex': 0, 'confidence': 0.9}]}

    def invalid(self): self.assertTrue(v.validate_document(self.plan))
    def text(self):
        self.el.update(type='text', drawStrategy='text', text={'content': '夏日散步', 'language': 'zh-Hant',
                       'font': {'family': ['Noto Sans TC', 'sans-serif'], 'size': 40}})
        return self.el['text']

    def test_valid_plan(self): self.assertEqual(v.validate_document(self.plan), [])
    def test_schema_self_validation(self):
        for kind in ('plan', 'analysis'): v.schema_validator(kind)
    def test_examples(self):
        for path in (ROOT / 'examples').rglob('scene-plan*.json'):
            with self.subTest(path=path): self.assertEqual(v.validate_document(v.read_json(str(path))), [])
    def test_invalid_roots(self):
        for value in (None, [], 'x', 3, True):
            with self.subTest(value=value): self.assertTrue(v.validate_document(value))
    def test_missing_required(self):
        for field in ('canvas', 'seed', 'renderer', 'layers'):
            data = copy.deepcopy(self.plan); del data[field]
            with self.subTest(field=field): self.assertTrue(v.validate_document(data))
    def test_canvas_types(self):
        for value in (0, -1, True, '100', None, 1.5):
            self.plan['canvas']['width'] = value
            with self.subTest(value=value): self.invalid()
    def test_seed_types(self):
        for seed in (-1, 4294967296, True, '42', 1.5, None):
            self.plan['seed'] = seed
            with self.subTest(seed=seed): self.invalid()
    def test_invalid_layer_types(self):
        for value in (None, 'layers', [None], [{}]):
            self.plan['layers'] = value
            with self.subTest(value=value): self.invalid()
    def test_invalid_element_types(self):
        for value in (None, 'elements', [None], [{}]):
            self.plan['layers'][0]['elements'] = value
            with self.subTest(value=value): self.invalid()
    def test_missing_zindex(self): del self.plan['layers'][0]['zIndex']; self.invalid()
    def test_zindex_boolean(self): self.plan['layers'][0]['zIndex'] = True; self.invalid()
    def test_invalid_bbox(self):
        for bbox in ('abcd', {}, [0, 0, 1], [0, 0, 1, 1, 1], [0, 0, 0, 1], [0, 0, -1, 1], [True, 0, 1, 1], [0, 0, '1', 1]):
            self.el['bbox'] = bbox
            with self.subTest(bbox=bbox): self.invalid()
    def test_crop_rejected(self): self.el['bbox'] = [-0.1, 0, 1, 1]; self.invalid()
    def test_explicit_crop(self):
        self.el.update(bbox=[-0.1, 0, 1.2, 1], allowCrop=True)
        self.assertFalse(v.validate_document(self.plan))
    def test_crop_is_boolean(self): self.el['allowCrop'] = 'true'; self.invalid()
    def test_float_boundary_tolerance(self):
        self.el['bbox'] = [0.1, 0, 0.9000000000000001, 1]
        self.assertFalse(v.validate_document(self.plan))
    def test_duplicate_id(self): self.el['id'] = 'layer'; self.invalid()
    def test_duplicate_across_layers(self):
        self.plan['layers'].append(copy.deepcopy(self.plan['layers'][0])); self.invalid()
    def test_blank_id(self): self.el['id'] = '  '; self.invalid()
    def test_unknown_strategy(self): self.el['drawStrategy'] = 'magic'; self.invalid()
    def test_standalone_renderer(self): self.plan['build'] = 'standalone'; self.invalid()
    def test_standalone_brush(self):
        self.plan.update(build='standalone', renderer='p5-brush'); self.assertFalse(v.validate_document(self.plan))
    def test_valid_multilingual(self):
        t = self.text()
        for lang, content in [('zh-Hant', '夏日散步'), ('zh-Hans', '夏日散步'), ('ja', '夏の散歩'), ('ko', '여름 산책'), ('th', 'เดินเล่นหน้าร้อน'), ('en', 'Summer Walk')]:
            t.update(language=lang, content=content)
            with self.subTest(lang=lang): self.assertFalse(v.validate_document(self.plan))
    def test_text_required_fields(self):
        self.text()
        for field in ('content', 'language', 'font'):
            data = copy.deepcopy(self.plan); del data['layers'][0]['elements'][0]['text'][field]
            with self.subTest(field=field): self.assertTrue(v.validate_document(data))
    def test_text_bbox_required(self): self.text(); del self.el['bbox']; self.invalid()
    def test_text_type_mismatch(self): self.text(); self.el['drawStrategy'] = 'polygon'; self.invalid()
    def test_hidden_text_payload(self): self.text(); self.el['type'] = 'shape'; self.invalid()
    def test_empty_text(self): self.text()['content'] = '  '; self.invalid()
    def test_font_family(self):
        t = self.text()
        for family in ([], [''], [4], None, ''):
            t['font']['family'] = family
            with self.subTest(family=family): self.invalid()
    def test_font_size(self): self.text()['font']['size'] = 0; self.invalid()
    def test_optional_extension_is_preserved(self):
        self.plan['agentNotes'] = {'custom': 'preserved'}
        self.plan['layers'][0]['bbox'] = 'not an element bbox'
        before = copy.deepcopy(self.plan)
        self.assertFalse(v.validate_document(self.plan)); self.assertEqual(before, self.plan)
    def test_nonfinite(self):
        for value in (float('nan'), float('inf'), float('-inf')):
            self.el['style'] = {'opacity': value}
            with self.subTest(value=value): self.invalid()
    def test_valid_analysis(self): self.assertFalse(v.validate_document(self.analysis, 'analysis'))
    def test_analysis_ratio(self):
        self.analysis['source']['aspectRatio'] = 3
        self.assertTrue(v.validate_document(self.analysis, 'analysis'))
    def test_analysis_duplicate_and_crop(self):
        self.analysis['elements'].append(copy.deepcopy(self.analysis['elements'][0]))
        self.analysis['elements'][0]['bbox'] = [-1, 0, 1, 1]
        self.assertEqual(len(v.validate_document(self.analysis, 'analysis')), 2)
    def test_analysis_confidence(self):
        self.analysis['elements'][0]['confidence'] = 1.1
        self.assertTrue(v.validate_document(self.analysis, 'analysis'))
    def test_json_pointer(self): self.assertEqual(v.pointer(['x/y', '~key', 0]), '/x~1y/~0key/0')
    def test_cli_stdin(self):
        result = self.cli(json.dumps(self.plan)); self.assertEqual(result.returncode, 0); self.assertTrue(json.loads(result.stdout)['valid'])
    def test_cli_invalid(self):
        result = self.cli('{}'); self.assertEqual(result.returncode, 1); self.assertFalse(json.loads(result.stdout)['valid'])
    def test_cli_bad_json(self):
        for content in ('{', '{"a":1,"a":2}', '{"x":NaN}', '{"x":Infinity}'):
            result = self.cli(content)
            with self.subTest(content=content):
                self.assertEqual(result.returncode, 2); self.assertNotIn('Traceback', result.stderr); json.loads(result.stdout)
    def test_cli_exponent_overflow(self): self.assertEqual(self.cli('{"x":1e999}').returncode, 1)
    def test_cli_missing_file(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/validate_scene.py'), str(ROOT / '__missing__'), '--json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2); self.assertFalse(json.loads(result.stdout)['valid'])
    def test_utf8_bom(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'scene.json'
            self.text(); path.write_text(json.dumps(self.plan, ensure_ascii=False), encoding='utf-8-sig')
            self.assertEqual(v.read_json(str(path)), self.plan)
    def test_invalid_utf8(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'scene.json'; path.write_bytes(b'\xff')
            with self.assertRaises(UnicodeError): v.read_json(str(path))
    def test_size_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'scene.json'; path.write_bytes(b' ' * (v.MAX_BYTES + 1))
            with self.assertRaises(ValueError): v.read_json(str(path))
    def cli(self, text):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/validate_scene.py'), '-', '--json'], input=text, capture_output=True, text=True, encoding='utf-8')


if __name__ == '__main__': unittest.main()
