"""Berserk grants an expiring benefit without accumulating temporary attack stats."""
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
from world import World


class BerserkFunctionTests(unittest.TestCase):
    def test_api_costs_and_both_existing_sources_at_three_frame_rates(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'berserk.json'
            process = subprocess.run([sys.executable, 'scripts/audit_berserk_function.py', '--output', str(output)],
                                     cwd=root, capture_output=True, text=True, timeout=45)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['api']), 9)
        for row in report['api']:
            with self.subTest(base=row['base'], params=row['params']):
                for stat in ('physical', 'magic', 'damage'):
                    self.assertAlmostEqual(row['active'][stat], row['initial'][stat] * 2)
                    self.assertAlmostEqual(row['halfway'][stat], row['active'][stat])
                    self.assertAlmostEqual(row['expired'][stat], row['initial'][stat])
                rate = row['params'][0] if row['params'] else 5
                self.assertAlmostEqual(row['halfway']['hp'], row['initial']['hp'] - rate / 2)
                self.assertAlmostEqual(row['expired']['hp'], row['initial']['hp'] - rate)
                self.assertFalse(row['buff_after'])
        self.assertEqual(len(report['sources']), 12)
        for row in report['sources']:
            with self.subTest(source=row['tile_id'], side=row['side'], fps=row['fps']):
                self.assertTrue(row['completed'])
                self.assertEqual(row['applied']['source'], row['tile_id'])
                self.assertEqual(row['applied']['params'], [])
                self.assertEqual(row['applied']['physical'], 20)
                self.assertEqual(row['final']['physical'], 10)
                self.assertGreater(row['min_hp'], 0)
                self.assertLess(row['min_hp'], 120)
                self.assertEqual(row['respawns'], 0)
                self.assertEqual(row['errors'], [])
                self.assertFalse(row['buff_after'])

    def test_refresh_removal_clear_and_respawn_never_accumulate_attack(self):
        for base in (.1, 1.25, 10):
            actor = Player(0, 'lifecycle', 5.5, 6.9, {}, phys_atk=base, magic_atk=base / 2)
            for _ in range(100):
                actor.apply_buff(47, (0,), 1)
                self.assertEqual(actor.phys_atk, base * 2)
                self.assertEqual(actor.magic_atk, base)
                actor.tick_buffs(.01)
            for cleanup in (lambda: actor.remove_buff(47), actor.clear_buffs,
                            lambda: actor.clear_buffs('positive'), lambda: actor.reset(5.5, 6.9)):
                actor.apply_buff(47, (0,), 1)
                cleanup()
                self.assertEqual(actor.phys_atk, base)
                self.assertEqual(actor.magic_atk, base / 2)

    def test_legacy_altar_multiplier_stays_independent_and_fractional(self):
        world = World(0, 'altar combination', 20, 20, gravity=0)
        world.set_tile(5, 5, 348)
        for base in (.1, 1.25, 10):
            actor = Player(0, 'altar combination', 5.5, 6.9, {}, phys_atk=base, magic_atk=base / 2)
            actor.apply_buff(47, (0,), 2)
            for _ in range(100):
                actor.collide_with_world(world, 0)
                self.assertEqual(actor.phys_atk, base * 2.5 * 2)
                self.assertEqual(actor.magic_atk, base)
            actor._x = 10.5
            actor.collide_with_world(world, 0)
            self.assertEqual(actor.phys_atk, base * 2)
            actor.tick_buffs(2)
            self.assertEqual(actor.phys_atk, base)
            self.assertEqual(actor.magic_atk, base / 2)
