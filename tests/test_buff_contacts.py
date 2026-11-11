"""Continuous source contact refreshes duration; separate acquisitions still stack."""
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
from buff_system import BuffInstance
from creature import Player
from scripts.control_session import create_control_session
from world import World

ROOT=Path(__file__).resolve().parents[1]


class BuffContactTests(unittest.TestCase):
    def probe(self,script,*flags):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'report.json'
            result=subprocess.run([sys.executable,script,'--output',str(output),*flags],cwd=ROOT,
                                  capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            return json.loads(output.read_text())

    def test_all_stackable_sources_remain_single_layer_during_continuous_contact(self):
        report=self.probe('scripts/audit_contact_buff_stacks.py')
        self.assertFalse(report['exposure_candidate'])
        self.assertGreaterEqual(report['source_count'],45)
        self.assertEqual(len(report['runs']),3*report['source_count'])
        self.assertEqual(report['multiple_stack_samples'],[])
        for row in report['runs']:
            self.assertEqual([s['step'] for s in row['samples']],[1,2,3,12,60])
            self.assertEqual(row['samples'][0]['source_contact'],True)

    def test_contiguous_same_kind_strips_and_actual_loop_crossings_do_not_add_layers(self):
        report=self.probe('scripts/audit_contact_exposure_cases.py')
        self.assertFalse(report['exposure_candidate'])
        self.assertEqual(len(report['strips']),12)
        for row in report['strips']:
            with self.subTest(row=row):
                self.assertGreater(row['distance'],50)
                self.assertEqual(row['max_cold_stacks'],1)
                self.assertAlmostEqual(row['v_max'],21.9)
                self.assertEqual(row['wraps'],5 if row['loop'] else 0)
        self.assertEqual([r['stacks'] for r in report['placements']],[1,1,1,2,3,1,2,2,2,1,1])

    def test_explicit_refresh_changes_params_duration_source_without_implicit_stacking(self):
        instance=BuffInstance(4,(50,),1)
        for _ in range(100):
            instance.refresh((25,),6,add_stack=False)
        self.assertEqual(instance.stacks,1)
        self.assertEqual(instance.params,(25,))
        self.assertEqual(instance.duration,6)
        instance.refresh((50,),8)
        self.assertEqual(instance.stacks,2)
        instance.refresh((25,),4,add_stack=False)
        self.assertEqual(instance.stacks,2)
        actor=Player(0,'explicit acquisition',0,0,{})
        actor.apply_buff(3,(20,),5,source=5000)
        actor.apply_buff(3,(25,),8,source=5001,add_stack=False)
        self.assertEqual(actor.buffs[0].stacks,1)
        self.assertEqual(actor.buffs[0].source,5001)
        self.assertEqual(actor.buffs[0].params,(25,))
        self.assertEqual(actor.buffs[0].duration,8)
        actor.apply_buff(3,(20,),5,source=5000)
        self.assertEqual(actor.buffs[0].stacks,2)
        self.assertAlmostEqual(actor.get_buff_stat('v_max',10),14)

    def test_pause_actual_respawn_and_flight_reset_exposure_without_losing_api_layers(self):
        world=World(0,'exposure lifecycle',30,32,gravity=-9.8,spawn_points=(5.5,5.9))
        world.lives=5
        for x in range(30):world.set_tile(x,4,373)
        session=create_control_session(0,world=world)
        actor=session.app.player1
        def cold():
            return next(b for b in actor.buffs if b.buff_id==51)
        with patch('pygame.key.get_pressed',return_value=defaultdict(bool)):
            session.advance(1/120)
            self.assertEqual(cold().stacks,1)
            actor.apply_buff(51,(),6)
            session.advance(.1)
            self.assertEqual(cold().stacks,2)
            duration=cold().duration
            session.app.help_open=True
            session.advance(10)
            self.assertEqual(cold().duration,duration)
            self.assertEqual(cold().stacks,2)
            session.app.help_open=False
            actor.take_damage(actor.hp_max*10,0)
            self.assertFalse(actor.alive)
            session.advance(1/120)
            self.assertEqual(session.app._player_lives_left,4)
            self.assertTrue(actor.has_buff(36))
            self.assertEqual(cold().stacks,1)
            self.assertIs(actor._buff_contact_world,world)
            self.assertEqual(actor._buff_contact_kinds,frozenset({373}))
            actor.fly_mode=True
            session.advance(1/120)
            self.assertEqual(actor._buff_contact_kinds,frozenset())
            actor.fly_mode=False
            session.advance(1/120)
            self.assertEqual(cold().stacks,2)
            self.assertLessEqual(len(actor._buff_contact_kinds),1)

    def test_root_immunity_controls_can_leave_each_original_source(self):
        report=self.probe('scripts/audit_rooted_source_escape.py','--immunity-only')
        self.assertFalse(report['single_stack_candidate'])
        self.assertFalse(report['bounded_root_candidate'])
        self.assertEqual(len(report['runs']),36)
        for row in report['runs']:
            with self.subTest(source=row['source'],fps=row['fps'],gravity=row['gravity'],jump=row['jump_input']):
                self.assertTrue(row['immune_api_injection'])
                self.assertFalse(row['root_seen'])
                self.assertTrue(row['escaped'])
                self.assertEqual(row['errors'],[])
