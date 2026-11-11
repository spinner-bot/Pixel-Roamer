"""Wind-walk boosts actual intent and keeps its charge, momentum and lifecycle contract."""
from collections import defaultdict
import json
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
from creature import Player
from scripts.control_session import create_control_session
from world import World

ROOT=Path(__file__).resolve().parents[1]


class WindWalkTests(unittest.TestCase):
    def probe(self,*flags):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'wind.json'
            result=subprocess.run([sys.executable,'scripts/audit_wind_walk_controls.py','--output',str(output),*flags],
                cwd=ROOT,capture_output=True,text=True,timeout=90)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            return json.loads(output.read_text())

    def test_actual_source_reverses_at_three_rates_and_retains_release_momentum(self):
        report=self.probe()
        self.assertFalse(report['direction_candidate'])
        self.assertEqual(report['api_control_buffs'],[])
        self.assertEqual(len(report['runs']),48)
        for row in report['runs']:
            with self.subTest(fps=row['fps'],direction=row['direction'],source=row['with_source'],continuous=row['continuous_source'],response=row['response']):
                self.assertEqual(row['hp'],150)
                self.assertLessEqual(abs(row['start_velocity']),36.5)
                self.assertLessEqual(abs(row['final_velocity']),36.5)
                if row['response']=='reverse':
                    self.assertIsNotNone(row['seconds_to_reverse'])
                    self.assertLess(row['seconds_to_reverse'],1.5)
                    self.assertLess(row['final_velocity']*row['direction'],0)
                else:
                    self.assertIsNone(row['seconds_to_reverse'])
                    self.assertGreater(row['final_velocity']*row['direction'],0)
                if row['with_source']:
                    self.assertTrue(any(t['buff53'] and t['buff53']['source']==394 for t in row['trace']))

    def test_actual_effective_direction_after_reverse_clarity_and_iron_will(self):
        for controls in ((23,),(23,8),(23,40)):
            report=self.probe('--fps','60','--control-buffs',*(str(i) for i in controls))
            self.assertFalse(report['direction_candidate'])
            self.assertEqual(report['api_control_buffs'],list(controls))
            self.assertEqual(len(report['runs']),16)
            for row in report['runs']:
                with self.subTest(controls=controls,row=row):
                    expected_sign=-1 if controls==(23,) else 1
                    self.assertGreater(row['start_velocity']*row['direction']*expected_sign,0)
                    if row['response']=='reverse':
                        self.assertIsNotNone(row['seconds_to_reverse'])
                        self.assertLess(row['seconds_to_reverse'],1.5)

    def test_impulse_direction_zero_parameter_and_final_velocity_cap(self):
        world=World(0,'wind impulse',40,32,gravity=0)
        dt=1/120
        for velocity,acceleration,expected_sign in ((20,-10,-1),(-20,10,1),(20,10,1),(-20,-10,-1),(20,0,1),(-20,0,-1)):
            actor=Player(0,'wind direction',0,0,{})
            actor.apply_buff(53,(),5)
            actor.v_x,actor.a_x=velocity,acceleration
            actor._wind_walk_timer=16
            actor.update_physics(dt,world)
            base=velocity+acceleration*dt
            impulse=(16+dt)*.5*dt*3
            self.assertAlmostEqual(actor.v_x-base,expected_sign*impulse)
        actor=Player(0,'zero wind',0,0,{})
        actor.apply_buff(53,(0,),5)
        actor.v_x,actor.a_x=20,-10
        actor._wind_walk_timer=16
        actor.update_physics(dt,world)
        self.assertAlmostEqual(actor.v_x,20-10*dt)
        actor.remove_buff(53)
        actor.update_physics(dt,world)
        self.assertEqual(actor._wind_walk_timer,0)
        for sign in (-1,1):
            actor=Player(0,'bounded boost',0,0,{})
            actor.apply_buff(53,(1000,),5)
            actor.v_x,actor.a_x=sign*35,sign
            actor._wind_walk_timer=1000
            actor.update_physics(dt,world)
            self.assertEqual(actor.v_x,sign*actor.v_max)

    def test_pause_expiry_and_real_respawn_keep_charge_local_to_active_motion(self):
        world=World(0,'wind lifecycle',128,32,gravity=-9.8,spawn_points=(10.5,5.9))
        world.lives=5
        for x in range(128):world.set_tile(x,4,2)
        world.set_tile(10,5,394)
        session=create_control_session(0,world=world)
        actor=session.app.player1
        keys=defaultdict(bool)
        with patch('pygame.key.get_pressed',return_value=keys):
            session.advance(1/120)
            self.assertTrue(actor.has_buff(53))
            keys[pygame.K_d]=True
            session.advance(3)
            self.assertGreater(actor._wind_walk_timer,2.9)
            timer=actor._wind_walk_timer
            remaining=next(b.duration for b in actor.buffs if b.buff_id==53)
            session.app.help_open=True
            session.advance(10)
            self.assertEqual(actor._wind_walk_timer,timer)
            self.assertEqual(next(b.duration for b in actor.buffs if b.buff_id==53),remaining)
            session.app.help_open=False
            keys[pygame.K_d]=False
            actor.apply_buff(53,(),.01)
            session.advance(.05)
            self.assertFalse(actor.has_buff(53))
            self.assertEqual(actor._wind_walk_timer,0)
            actor.apply_buff(53,(),5)
            keys[pygame.K_d]=True
            session.advance(1)
            self.assertGreater(actor._wind_walk_timer,.9)
            keys[pygame.K_d]=False
            actor.take_damage(actor.hp_max*10,0)
            self.assertFalse(actor.alive)
            session.advance(1/120)
            self.assertEqual(session.app._player_lives_left,4)
            self.assertTrue(actor.has_buff(36))
            self.assertTrue(actor.has_buff(53))
            self.assertEqual(actor._wind_walk_timer,0)
