"""Air charges renew on real support, without allowing extra midair jumps."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import pygame
from scripts.audit_air_jump_cycles import ability_session, advance, keydown, spend_air_jump


class AirJumpCycleTests(unittest.TestCase):
    def test_ground_cloud_and_climb_cycles_restore_ability_at_three_frame_rates(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'air.json'
            result = subprocess.run([sys.executable, 'scripts/audit_air_jump_cycles.py',
                                     '--output', str(output)], cwd=root,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['after']), 9)
        self.assertTrue(all(not run['succeeded'] for run in report['before']))
        for run in report['after']:
            with self.subTest(kind=run['kind'], fps=run['fps']):
                self.assertEqual(run['spent']['air_used'], 1)
                self.assertFalse(run['spent']['ground'])
                self.assertEqual(run['support']['air_used'], 0)
                self.assertTrue(run['support']['climbing'] if run['kind'] == 'climb_release' else run['support']['ground'])
                self.assertFalse(run['before_retry']['ground'])
                self.assertFalse(run['before_retry']['climbing'])
                self.assertTrue(run['before_retry']['ability_active'])
                self.assertTrue(run['succeeded'])
                self.assertEqual(run['after_retry']['air_used'], 1)

    def test_touching_ladder_without_grabbing_does_not_grant_a_third_jump(self):
        session = ability_session(ladder=True)
        player = session.app.player1
        spend_air_jump(session, 60)
        self.assertTrue(player.can_climb)
        self.assertFalse(player.is_climbing)
        before = player.v_y
        stamina = player.stamina
        keydown(session, pygame.K_SPACE)
        advance(session, 60, 3)
        self.assertEqual(player._air_jumps_used, 1)
        self.assertLess(player.v_y, before)
        self.assertGreaterEqual(player.stamina, stamina)

    def test_blocked_climb_does_not_recharge_but_valid_iron_will_grip_does(self):
        session = ability_session(ladder=True)
        player = session.app.player1
        spend_air_jump(session, 60)
        player.apply_buff(28, (), 1)
        keydown(session, pygame.K_w)
        self.assertFalse(player.is_climbing)
        self.assertEqual(player._air_jumps_used, 1)
        player.apply_buff(40, (), 10)
        keydown(session, pygame.K_w)
        self.assertTrue(player.is_climbing)
        self.assertEqual(player._air_jumps_used, 0)

    def test_regranting_buff_without_support_does_not_refresh_air_charge(self):
        session = ability_session()
        player = session.app.player1
        spend_air_jump(session, 60)
        player.clear_buffs()
        player.apply_buff(37, (), 30)
        before = player.v_y
        keydown(session, pygame.K_SPACE)
        advance(session, 60, 3)
        self.assertEqual(player._air_jumps_used, 1)
        self.assertLess(player.v_y, before)

    def test_ceiling_collision_does_not_recharge_air_charge(self):
        session = ability_session(ceiling=True)
        player = session.app.player1
        spend_air_jump(session, 60)
        for _ in range(240):
            advance(session, 120)
            if player.on_ceiling:
                break
        self.assertTrue(player.on_ceiling)
        self.assertFalse(player.on_ground)
        self.assertEqual(player._air_jumps_used, 1)
        keydown(session, pygame.K_SPACE)
        advance(session, 60, 3)
        self.assertLess(player.v_y, 0)
        self.assertEqual(player._air_jumps_used, 1)

    def test_landing_recharges_before_catapult_immediately_launches_again(self):
        session = ability_session()
        player, world = session.app.player1, session.app._current_map
        world.set_tile(2, 0, 433)
        player._y, player.v_y = 2.0, -12
        player.on_ground = False
        player._air_jumps_used = 1
        advance(session, 120)
        self.assertGreater(player.v_y, 30)
        self.assertFalse(player.on_ground)
        self.assertEqual(player._air_jumps_used, 0)
