"""Declared cleanup relations work in both orders and only accepted acquisitions act."""
from collections import defaultdict
from dataclasses import replace
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
from buff_system import BUFF_TYPES,BuffType,BuffInstance,CAT_NEGATIVE,CAT_NEUTRAL,CAT_POSITIVE
from creature import Player
from scripts.control_session import create_control_session
from world import World

ROOT=Path(__file__).resolve().parents[1]


def types():
    return {5000:BuffType(5000,name='test_target',category=CAT_NEGATIVE,cleanup_by=(5001,),on_remove='target_removed'),
            5001:BuffType(5001,name='test_counter',category=CAT_POSITIVE),
            5002:BuffType(5002,name='test_blocker',category=CAT_NEUTRAL),
            5003:BuffType(5003,name='test_other',category=CAT_NEGATIVE,cleanup_by=(5001,),on_remove='other_removed')}


class BuffCleanupTests(unittest.TestCase):
    def test_declared_orders_and_real_water_steam_sources_clear_and_restore_fire_damage(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'cleanup.json'
            result=subprocess.run([sys.executable,'scripts/audit_buff_cleanup_relations.py','--output',str(output)],
                                  cwd=ROOT,capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            report=json.loads(output.read_text())
        self.assertEqual(len(report['edges']),2)
        self.assertEqual(len(report['api']),4)
        self.assertTrue(all(r['relation_satisfied'] for r in report['api']))
        self.assertEqual(len(report['sources']),24)
        for row in report['sources']:
            with self.subTest(target=row['target_api_injection'],source=row['actual_counter_source'],fps=row['fps'],counter_first=row['counter_first']):
                self.assertGreaterEqual(row['physics_time'],1/120)
                self.assertTrue(row['wet_observed'])
                self.assertTrue(row['relation_satisfied'])
                self.assertFalse(row['target_remains'])
                if row['target_api_injection']==9:
                    self.assertEqual(row['post_water_api_fire_loss'],20 if row['actual_counter_source']==426 else 10)

    def test_rejected_acquisitions_do_not_clear_conflicts_or_reverse_relations(self):
        definitions=types()
        definitions[5001]=replace(definitions[5001],conflicts=(5000,),cleanup_by=(5002,),on_remove='counter_removed')
        with patch.dict(BUFF_TYPES,definitions):
            actor=Player(0,'counter blocked',0,0,{})
            actor.apply_buff(5000,(),5)
            actor.apply_buff(5002,(),5)
            with patch.object(actor,'_dispatch_buff_callback') as callback:
                actor.apply_buff(5001,(),5)
                self.assertTrue(actor.has_buff(5000))
                self.assertFalse(actor.has_buff(5001))
                callback.assert_not_called()
            actor=Player(0,'cursed counter',0,0,{})
            actor.apply_buff(5000,(),5)
            actor.apply_buff(57,(),5)
            with patch.object(actor,'_dispatch_buff_callback') as callback:
                actor.apply_buff(5001,(),5)
                self.assertTrue(actor.has_buff(5000))
                self.assertFalse(actor.has_buff(5001))
                callback.assert_not_called()
        definitions=types()
        definitions[5000]=replace(definitions[5000],cleanup_by=(21,))
        with patch.dict(BUFF_TYPES,definitions):
            actor=Player(0,'immune counter',0,0,{})
            actor.apply_buff(5000,(),5)
            actor.apply_buff(40,(),5)
            with patch.object(actor,'_dispatch_buff_callback') as callback:
                actor.apply_buff(21,(),5)
                self.assertTrue(actor.has_buff(5000))
                self.assertFalse(actor.has_buff(21))
                callback.assert_not_called()

    def test_refresh_redundant_conflicts_and_callback_side_effects_remove_each_active_effect_once(self):
        for explicit_conflict in (False,True):
            definitions=types()
            if explicit_conflict:definitions[5001]=replace(definitions[5001],conflicts=(5000,))
            with patch.dict(BUFF_TYPES,definitions):
                actor=Player(0,'one removal',0,0,{})
                actor.apply_buff(5000,(),5)
                with patch.object(actor,'_dispatch_buff_callback') as callback:
                    actor.apply_buff(5001,(),5)
                    callback.assert_called_once_with('target_removed',buff_id=5000)
                    self.assertFalse(actor.has_buff(5000))
                    self.assertTrue(actor.has_buff(5001))
                actor=Player(0,'absent conflict',0,0,{})
                with patch.object(actor,'_dispatch_buff_callback') as callback:
                    actor.apply_buff(5001,(),5)
                    callback.assert_not_called()
        with patch.dict(BUFF_TYPES,types()):
            actor=Player(0,'legacy mixed state',0,0,{})
            actor.apply_buff(5001,(),5)
            actor.buffs.append(BuffInstance(5000,(),5))  # Explicit legacy-state fixture.
            with patch.object(actor,'_dispatch_buff_callback') as callback:
                actor.apply_buff(5001,(),10,add_stack=False)
                callback.assert_called_once_with('target_removed',buff_id=5000)
                self.assertFalse(actor.has_buff(5000))
                self.assertEqual(next(b.duration for b in actor.buffs if b.buff_id==5001),10)
            actor=Player(0,'callback chain',0,0,{})
            actor.apply_buff(5000,(),5)
            actor.apply_buff(5003,(),5)
            calls=[]
            def dispatch(name,b=None,buff_id=None):
                calls.append(name)
                if name=='target_removed':actor.remove_buff(5003)
            with patch.object(actor,'_dispatch_buff_callback',side_effect=dispatch):
                actor.apply_buff(5001,(),5)
            self.assertEqual(calls,['target_removed','other_removed'])
            self.assertFalse(actor.has_buff(5000))
            self.assertFalse(actor.has_buff(5003))

    def test_wet_expiry_reacquisition_pause_and_real_respawn_keep_cleanup_consistent(self):
        world=World(0,'wet cleanup lifecycle',32,32,gravity=-9.8,spawn_points=(10.5,5.9))
        world.lives=5
        for x in range(32):world.set_tile(x,4,2)
        world.set_tile(10,5,7)
        session=create_control_session(0,world=world)
        actor=session.app.player1
        with patch('pygame.key.get_pressed',return_value=defaultdict(bool)):
            actor.apply_buff(9,(),5)
            session.advance(1/120)
            self.assertTrue(actor.has_buff(15))
            self.assertFalse(actor.has_buff(9))
            duration=next(b.duration for b in actor.buffs if b.buff_id==15)
            session.app.help_open=True
            session.advance(10)
            self.assertEqual(next(b.duration for b in actor.buffs if b.buff_id==15),duration)
            session.app.help_open=False
            actor._x=15.5;actor.collide_with_world(world,0)  # API contact isolation.
            session.advance(1.02)
            self.assertFalse(actor.has_buff(15))
            actor.apply_buff(9,(),5)
            self.assertTrue(actor.has_buff(9))
            actor._x=10.5;actor.collide_with_world(world,0)
            self.assertTrue(actor.has_buff(15))
            self.assertFalse(actor.has_buff(9))
            actor.take_damage(actor.hp_max*10,0)
            self.assertFalse(actor.alive)
            session.advance(1/120)
            self.assertEqual(session.app._player_lives_left,4)
            self.assertTrue(actor.has_buff(36))
            self.assertTrue(actor.has_buff(15))
            self.assertFalse(actor.has_buff(9))
