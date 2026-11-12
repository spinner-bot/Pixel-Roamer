"""Existing source blocks must deliver numerical effects, with API zero preserved."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from creature import Player


class BuffSourceDefaultTests(unittest.TestCase):
    def test_all_forty_source_consumer_probes_have_the_claimed_direction(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'defaults.json'
            process = subprocess.run([sys.executable, 'scripts/audit_buff_source_defaults.py', '--output', str(output)],
                                     cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            rows = json.loads(output.read_text())['rows']
        self.assertEqual(len(rows), 40)
        self.assertEqual(len({r['buff_id'] for r in rows}), 13)
        for row in rows:
            with self.subTest(tile=row['tile_id'], buff=row['buff_id']):
                active, control = row['active']['value'], row['control']['value']
                self.assertTrue(row['different'])
                if row['buff_id'] in (6, 7, 13, 43, 51):
                    self.assertLess(active, control)
                else:
                    self.assertGreater(active, control)
                if row['buff_id'] == 44:
                    self.assertEqual(row['active']['opportunities_first_half_second'], 0)
                    self.assertEqual(active, 2 if row['tile_id'] == 432 else 1)

    def test_explicit_zero_numeric_parameters_are_not_globally_reinterpreted(self):
        for buff_id, stat in ((5, 'stamina_recovery'), (6, 'stamina_cost'), (7, 'damage_taken'),
                              (13, 'gravity'), (51, 'v_max'), (54, 'gravity')):
            with self.subTest(buff=buff_id):
                actor = Player(0, 'explicit zero', 0, 0, {})
                actor.apply_buff(buff_id, (0,), 1)
                self.assertEqual(actor.get_buff_stat(stat, 10), 10)
        for buff_id in (47, 55):
            actor = Player(0, 'explicit zero cost', 0, 0, {})
            actor.apply_buff(buff_id, (0,), 1)
            actor.tick_buffs(.5)
            self.assertEqual(actor.hp, actor.hp_max)
