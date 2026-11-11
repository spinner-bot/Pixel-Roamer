"""Check advertised height units against actual motion, cleanup and numeric boundaries."""
from collections import defaultdict
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame
from block_type import BlockType
from block_types_data import BLOCK_TYPES
from jump_height import jump_apex, launch_speed
from scripts.control_session import create_control_session
from world import World

ROOT=Path(__file__).resolve().parents[1]


class JumpHeightTests(unittest.TestCase):
    def test_actual_production_apex_matches_height_claim_across_gravity_drag_and_feather(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'production.json'
            result=subprocess.run([sys.executable,'scripts/audit_leaping_calibration_candidate.py',
                '--production','--quick','--output',str(output)],cwd=ROOT,capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            report=json.loads(output.read_text())
        self.assertEqual(report['errors'],[])
        self.assertEqual(len(report['runs']),72)
        self.assertEqual({r['damping'] for r in report['runs']},{.98,.9965,1.})
        for row in report['runs']:
            with self.subTest(row=row):
                self.assertFalse(row['candidate'])
                self.assertAlmostEqual(row['height_ratio'],row['expected_ratio'],places=8)
                self.assertTrue(row['landed'])
                self.assertEqual(row['respawns'],0)
                self.assertEqual(row['hp'],150)

    def test_near_unit_damping_apex_matches_independent_tick_recurrence(self):
        for gravity in (-.7,-9.8):
            for damping in (0.,1e-6,.98,.9965,.999999,1-1e-12,1-1e-15,1.):
                with self.subTest(gravity=gravity,damping=damping):
                    velocity=11.5
                    rises=[]
                    for _ in range(10000):
                        velocity=(velocity+gravity/120)*damping**.5
                        if velocity<=0:
                            break
                        rises.append(velocity/120)
                    self.assertLess(abs(jump_apex(11.5,gravity,damping)-math.fsum(rises)),1e-10)

    def test_refresh_pause_expiry_clear_and_reset_restore_height_context(self):
        world=World(0,'height lifecycle',30,80,gravity=-9.8,spawn_points=(10.5,5.9))
        for x in range(30):
            world.set_tile(x,4,2)
        world.lives=5
        session=create_control_session(0,world=world)
        actor=session.app.player1
        with patch('pygame.key.get_pressed',return_value=defaultdict(bool)):
            session.advance(1/120)
            actor.apply_buff(4,(),.05)
            actor.refresh_movement_stats()
            speed=actor.v_jump
            self.assertAlmostEqual(jump_apex(speed,-9.8,actor.f_y)/jump_apex(actor._base_v_jump,-9.8,actor.f_y),1.5)
            for _ in range(100):
                actor.refresh_movement_stats()
                self.assertEqual(actor.v_jump,speed)
            session.app.help_open=True
            session.advance(5)
            self.assertTrue(actor.has_buff(4))
            self.assertEqual(actor.v_jump,speed)
            session.app.help_open=False
            session.advance(.1)
            self.assertFalse(actor.has_buff(4))
            self.assertEqual(actor.v_jump,actor._base_v_jump)
            actor.apply_buff(4,(100,),5)
            actor.refresh_movement_stats()
            self.assertGreater(actor.v_jump,actor._base_v_jump)
            actor.clear_buffs()
            actor.refresh_movement_stats()
            self.assertEqual(actor.v_jump,actor._base_v_jump)
            actor.apply_buff(4,(100,),5)
            actor.apply_buff(13,(50,),5)
            actor.refresh_movement_stats()
            actor.take_damage(actor.hp_max*10,0)
            self.assertFalse(actor.alive)
            session.advance(1/120)
            self.assertFalse(actor.has_buff(4))
            self.assertFalse(actor.has_buff(13))
            self.assertEqual(actor.v_jump,actor._base_v_jump)
            self.assertIs(actor._effect_world,world)
            self.assertEqual(session.app._player_lives_left,4)
            self.assertTrue(actor.has_buff(36))

    def test_real_tile_jump_modifier_and_feather_combine_without_repeated_scaling(self):
        def measure(with_leaping):
            source=BlockType(5000,is_solid=False,special='jump',special_data=1.5,
                buff_ids=(13,4) if with_leaping else (13,),
                buff_params_list=((50,),(50,)) if with_leaping else ((50,),),
                buff_durations=(15,15) if with_leaping else (15,))
            world=World(0,'combined jump tile',30,100,gravity=-9.8,spawn_points=(10.5,5.9),
                        block_types={**BLOCK_TYPES,source.id:source})
            for x in range(30):
                world.set_tile(x,4,2)
            world.set_tile(10,5,source.id)
            session=create_control_session(0,world=world)
            actor=session.app.player1
            peak=actor._y
            with patch('pygame.key.get_pressed',return_value=defaultdict(bool)),patch('sfx.play_jump'):
                session.advance(1/120)
                self.assertTrue(actor.has_buff(13))
                self.assertEqual(actor.has_buff(4),with_leaping)
                with patch('pygame.event.get',return_value=[pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE)]):
                    session.app._handle_events()
                for _ in range(15*120):
                    session.advance(1/120)
                    peak=max(peak,actor._y)
                    if actor.on_ground and peak>6:
                        break
                self.assertTrue(actor.on_ground)
                self.assertEqual(actor.hp,150)
            return peak-5.9
        baseline=measure(False)
        boosted=measure(True)
        self.assertAlmostEqual(boosted/baseline,1.5,places=8)

    def test_numeric_fallbacks_large_finite_inputs_and_cache_remain_bounded(self):
        for gravity in (None,0.,1.,-9.8,-1e-300,float('inf'),float('nan')):
            for damping in (0.,.98,1-1e-15,1.):
                for multiplier in (0.,.5,1.,2.,1e100,float('inf'),float('nan')):
                    with self.subTest(gravity=gravity,damping=damping,multiplier=multiplier):
                        speed=launch_speed(11.5,gravity,damping,multiplier)
                        self.assertTrue(math.isfinite(speed))
                        self.assertGreaterEqual(speed,0)
        self.assertEqual(launch_speed(11.5,-9.8,0.,2.),11.5)
        self.assertEqual(launch_speed(11.5,-9.8,1.,0.),0)
        for index in range(512):
            launch_speed(11.5+index/100,None,1.,1.5)
        self.assertEqual(launch_speed.cache_info().maxsize,256)
        self.assertLessEqual(launch_speed.cache_info().currsize,256)
