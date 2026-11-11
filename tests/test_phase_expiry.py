"""Ending a temporary phase must restore valid collision without a new life."""
from collections import defaultdict
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import pygame
from player_factory import create_world_player
from scripts.control_session import create_control_session
from teleport import can_place, teleport_to
from world import World
from block_type import BlockType


def fixture():
    world = World(0, 'phase lifecycle', 24, 20, gravity=0, spawn_points=(3.5, 5.5))
    world.set_tile(5, 5, 19)
    player = create_world_player(world, {}, position=world.spawn_points)
    return player, world


class PhaseExpiryTests(unittest.TestCase):
    def test_actual_phase_sources_exit_walls_at_three_frame_rates_without_respawn(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'phase.json'
            result = subprocess.run([sys.executable, 'scripts/audit_phase_expiry.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['after']), 24)
        self.assertTrue(all(r['entered_wall'] and not r['first_expired']['clear'] for r in report['before']))
        for run in report['after']:
            with self.subTest(source=run['source'], wall=run['wall'], direction=run['direction'], fps=run['fps']):
                self.assertTrue(run['entered_wall'])
                self.assertTrue(run['first_expired']['clear'])
                self.assertTrue(run['final_clear'])
                self.assertEqual(run['respawns'], 0)
                self.assertEqual(run['first_expired']['hp'], 150)
                self.assertEqual(run['first_expired']['stamina'], 200)
                restored = run['first_expired']['restoration']
                self.assertIsNotNone(restored)
                self.assertTrue(restored['clear'])
                self.assertEqual(restored['target'], run['first_expired']['last_clear'])
                self.assertEqual(restored['target'], restored['anchor'])
                # The session can process this tick's held input after restoring placement.
                for axis in (0, 1):
                    delta = abs(run['first_expired']['position'][axis] - restored['target'][axis])
                    self.assertLessEqual(delta, abs(run['first_expired']['velocity'][axis]) / 120 + 1e-8)

    def test_expiry_after_clearing_wall_preserves_position_and_velocity(self):
        player, world = fixture()
        player.apply_buff(48, (), 1)
        player.collide_with_world(world, 0)
        player._x = 8.5
        player.collide_with_world(world, 0)
        player.remove_buff(48)
        player.v_x = 2
        before = player.get_center()
        player.collide_with_world(world, 0)
        self.assertEqual(player.get_center(), before)
        self.assertEqual(player.v_x, 2)

    def test_dispel_inside_wall_preserves_resources_and_cancels_stale_motion(self):
        player, world = fixture()
        player.apply_buff(48, (), 5)
        player.collide_with_world(world, 0)
        player.hp, player.stamina, player.score = 71, 84, 125
        player._x = 5.5
        player.collide_with_world(world, 0)
        player.v_x, player.v_y = 8, 3
        player.remove_buff(48)
        player.collide_with_world(world, 0)
        self.assertEqual(player.get_center(), world.spawn_points)
        self.assertEqual((player.v_x, player.v_y), (0, 0))
        self.assertEqual((player.hp, player.stamina, player.score), (71, 84, 125))

    def test_remaining_phase_source_prevents_early_rollback(self):
        player, world = fixture()
        player.apply_buff(48, (), 5)
        player.collide_with_world(world, 0)
        player._x = 5.5
        player._phantom_active, player._phantom_timer = True, 2
        player.remove_buff(48)
        player.collide_with_world(world, 0)
        self.assertEqual(player._x, 5.5)
        player._phantom_active = False
        player.collide_with_world(world, 0)
        self.assertTrue(can_place(player, world, *player.get_center()))

    def test_safe_teleport_and_new_life_do_not_reuse_old_phase_anchor(self):
        player, world = fixture()
        player.apply_buff(48, (), 5)
        player.collide_with_world(world, 0)
        player._x = 5.5
        self.assertTrue(teleport_to(player, world, 10.5, 5.5))
        player.remove_buff(48)
        player.collide_with_world(world, 0)
        self.assertEqual(player._x, 10.5)
        player.apply_buff(48, (), 5)
        player.collide_with_world(world, 0)
        player.clear_buffs()
        player.reset(15.5, 5.5)
        player.collide_with_world(world, 0)
        self.assertEqual(player._x, 15.5)

    def test_one_way_crossing_is_not_treated_as_solid_embedding(self):
        from block_types_data import BLOCK_TYPES
        world = World(0, 'one way phase', 24, 20, gravity=0,
                      block_types={**BLOCK_TYPES, 5000: BlockType(5000, is_solid=True, one_way=True)})
        player = create_world_player(world, {}, position=(3.5, 5.5))
        world.set_tile(8, 5, 5000)
        player.apply_buff(48, (), 5)
        player.collide_with_world(world, 0)
        player._x = 8.5
        player.v_y = 1
        player.remove_buff(48)
        player.collide_with_world(world, 0)
        self.assertEqual(player._x, 8.5)
        self.assertEqual(player.v_y, 1)

    def test_invalidated_anchor_falls_back_to_valid_spawn(self):
        player, world = fixture()
        player.apply_buff(48, (), 5)
        player.collide_with_world(world, 0)
        player._x = 4.5
        player.collide_with_world(world, 0)
        world.set_tile(4, 5, 19)
        player._x = 5.5
        player.remove_buff(48)
        player.collide_with_world(world, 0)
        self.assertEqual(player.get_center(), world.spawn_points)

    def test_stunned_phase_expiry_still_resolves_on_next_physics_step(self):
        # A stun deliberately blocks world movement; resolving occurs when physics resumes.
        player, world = fixture()
        session = create_control_session(0, world=world)
        player = session.app.player1
        player.apply_buff(48, (), 1)
        player.collide_with_world(world, 0)
        player._x = 5.5
        player.apply_buff(28, (), 2)
        with patch('pygame.key.get_pressed', return_value=defaultdict(bool)):
            for _ in range(121):
                session.advance(1 / 60)
        self.assertFalse(player.has_buff(28))
        self.assertTrue(can_place(player, world, *player.get_center()))
