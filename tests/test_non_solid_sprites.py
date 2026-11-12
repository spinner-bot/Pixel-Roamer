"""Background sprites and real consumed pickups keep the terrain beneath them."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from scripts.audit_decoration_compositing import scene
from scripts.non_solid_art import SPRITE_IDS


class NonSolidSpriteTests(unittest.TestCase):
    def test_variants_web_and_pickup_states_blend_on_all_three_backgrounds(self):
        for background in (0, 11, 12):
            result = scene(background, decorations=SPRITE_IDS)
            self.assertTrue(result['opaque_black_preserved'])
            for entry in result['decorations']:
                with self.subTest(background=background, block_id=entry['block_id']):
                    self.assertTrue(entry['composites_on_background'], entry)

    def test_real_pickup_return_scores_once_and_repaints_consumed_marker(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'pickups.json'
            result = subprocess.run(
                [sys.executable, 'scripts/audit_pickup_compositing.py', '--output', str(output)],
                cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['runs']), 30)
        for run in report['runs']:
            with self.subTest(block_id=run['block_id'], background=run['background']):
                self.assertTrue(run['reached_and_returned'])
                self.assertIsNone(run['failure'])
                self.assertEqual(run['respawns'], 0)
                self.assertEqual(run['score'], run['expected_score'])
                self.assertEqual(run['tile_after'], run['expected_consumed_id'])
                self.assertTrue(run['before']['composites'], run)
                self.assertTrue(run['after']['composites'], run)
                self.assertEqual(run['hp'], 150)
                self.assertEqual(run['stamina'], 200)
