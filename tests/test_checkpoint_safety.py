"""Checkpoint contact must never replace a valid respawn with an embedded pose."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from game_state import resolve_player_death
from player_factory import create_world_player
from teleport import can_place
from world import World


def anchor_world(anchor_id):
    world = World(0, 'anchor safety', 20, 15, gravity=0, spawn_points=(3.5, 5.5))
    world.set_tile(5, 5, anchor_id)
    return world


class CheckpointSafetyTests(unittest.TestCase):
    def test_phase_contact_and_real_respawn_at_three_frame_rates(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'checkpoint.json'
            result = subprocess.run([sys.executable, 'scripts/audit_checkpoint_safety.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['after']), 18)
        # Ghost cases expose the bug; these particular phantom trajectories already save clear poses.
        self.assertEqual(sum(not r['respawn']['clear'] for r in report['before']), 9)
        for run in report['after']:
            with self.subTest(anchor_id=run['anchor_id'], source=run['source'], fps=run['fps']):
                self.assertTrue(run['saved']['actor_clear'])
                self.assertTrue(run['saved']['clear'])
                self.assertTrue(run['respawn']['clear'])
                self.assertTrue(run['respawn']['alive'])
                self.assertEqual(run['respawn']['count'], 1)

    def test_invalid_contact_does_not_consume_anchor_cooldown_and_later_valid_contact_records(self):
        for anchor_id in (302, 350, 367):
            with self.subTest(anchor_id=anchor_id):
                world = anchor_world(anchor_id)
                player = create_world_player(world, {})
                player.apply_buff(48, (), 5)
                player.collide_with_world(world, 0)
                original = player.spawn_pos
                player._x = 5.5
                player.collide_with_world(world, 0)
                self.assertEqual(player.spawn_pos, original)
                self.assertNotIn('set_spawn', player._special_cooldowns)
                player._y = 6.9
                player.remove_buff(48)
                player.collide_with_world(world, 0)
                self.assertEqual(player.spawn_pos, (5.5, 6.9))
                if anchor_id != 302:
                    self.assertEqual(player._special_cooldowns['set_spawn'], 3)

    def test_normal_standing_contact_still_records_and_preserves_score_on_respawn(self):
        for anchor_id in (302, 350, 367):
            with self.subTest(anchor_id=anchor_id):
                world = anchor_world(anchor_id)
                player = create_world_player(world, {}, position=(5.5, 6.9))
                player.spawn_pos = world.spawn_points
                player.collide_with_world(world, 0)
                self.assertEqual(player.spawn_pos, (5.5, 6.9))
                player.score = 125
                player.take_raw_damage(1e9)
                lives, over = resolve_player_death(player, 1, False)
                self.assertEqual((lives, over), (0, False))
                self.assertEqual(player.score, 125)
                self.assertEqual(player.get_center(), player.spawn_pos)
                self.assertTrue(can_place(player, world, *player.get_center()))

    def test_loop_seam_contact_can_store_a_legal_negative_coordinate(self):
        world = World(0, 'loop anchor', 10, 15, loop_x=True, gravity=0, spawn_points=(5.5, 5.5))
        world.set_tile(0, 5, 302)
        player = create_world_player(world, {}, position=(-.4, 6.9))
        player.spawn_pos = world.spawn_points
        player.collide_with_world(world, 0)
        self.assertEqual(player.spawn_pos, (-.4, 6.9))
        self.assertTrue(can_place(player, world, *player.spawn_pos))
