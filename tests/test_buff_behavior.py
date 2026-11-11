"""Buff rules must drive actual source behavior and preserve timer/control boundaries."""
from collections import defaultdict
from copy import deepcopy
from dataclasses import FrozenInstanceError
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
from buff_behavior import BEHAVIORS,BEHAVIOR_PATH,DEFAULT_BEHAVIOR,behavior_for,load_behaviors
from resource_catalog import load_buffs
from scripts.control_session import create_control_session
from world import World
import pygame

ROOT=Path(__file__).resolve().parents[1]


class BuffBehaviorTests(unittest.TestCase):
    def probe(self,script,*flags):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'report.json'
            result=subprocess.run([sys.executable,script,'--output',str(output),*flags],cwd=ROOT,
                                  capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            return json.loads(output.read_text())

    def session(self):
        world=World(0,'contact rule lifecycle',30,32,gravity=-9.8,spawn_points=(5.5,5.9))
        world.lives=5
        for x in range(30):world.set_tile(x,4,2)
        world.set_tile(5,5,410)
        world.set_tile(6,5,370)
        return create_control_session(0,world=world),world

    def test_every_original_trap_escapes_with_and_without_immunity_at_three_rates(self):
        report=self.probe('scripts/audit_rooted_source_escape.py')
        self.assertFalse(report['single_stack_candidate'])
        self.assertFalse(report['bounded_root_candidate'])
        self.assertFalse(report['compound_slow_candidate'])
        self.assertIsNone(report['behavior_rules_candidate'])
        self.assertEqual(len(report['runs']),72)
        for row in report['runs']:
            with self.subTest(source=row['source'],fps=row['fps'],gravity=row['gravity'],jump=row['jump_input'],immune=row['immune_api_injection']):
                self.assertTrue(row['escaped'])
                self.assertEqual(row['errors'],[])
                self.assertLess(row['seconds'],20)
                self.assertEqual(row['root_seen'],not row['immune_api_injection'])
                if not row['immune_api_injection']:
                    self.assertTrue(any(b['id']==21 and b['source']==row['source'] for b in row['contact_buffs']))

    def test_actual_stat_api_matches_partial_full_and_zero_reductions_without_mutation(self):
        report=self.probe('scripts/audit_buff_behavior_numeric.py','--production')
        self.assertTrue(report['production'])
        self.assertEqual(report['errors'],[])
        self.assertEqual(len(report['pairs']),36)
        self.assertEqual(len(report['unchanged_controls']),4)
        for row in report['pairs']:
            self.assertAlmostEqual(row['production']['value'],row['expected'])
            self.assertTrue(row['production']['stacks_preserved'])
        for buff_id,expected in ((22,12.5),(51,21.6)):
            row=next(r for r in report['pairs'] if r['production']['buff']==buff_id
                     and r['production']['params']==[] and r['production']['stacks']==3)
            self.assertAlmostEqual(row['production']['value'],expected)

    def test_startup_rules_are_valid_immutable_and_explicit_files_do_not_change_them(self):
        self.assertLessEqual(set(BEHAVIORS),set(load_buffs()))
        self.assertEqual(behavior_for(21).contact_trigger,'entry')
        for buff_id in (22,51):self.assertEqual(behavior_for(buff_id).stat_stacking,'multiplicative')
        self.assertIs(behavior_for(4),DEFAULT_BEHAVIOR)
        with self.assertRaises(TypeError):BEHAVIORS[21]=DEFAULT_BEHAVIOR
        with self.assertRaises(FrozenInstanceError):behavior_for(21).contact_trigger='refresh'
        base=json.loads(BEHAVIOR_PATH.read_text())
        mutations={
            'duplicate':lambda d:d['entries'].append(deepcopy(d['entries'][0])),
            'unknown':lambda d:d['entries'][0].update(buff_id=9999),
            'bool_id':lambda d:d['entries'][0].update(buff_id=True),
            'contact':lambda d:d['entries'][0].update(contact_trigger='forever'),
            'stacking':lambda d:d['entries'][0].update(stat_stacking='squared'),
            'extra_field':lambda d:d['entries'][0].update(radius=2),
            'bool_version':lambda d:d.update(schema_version=True),
            'kind':lambda d:d.update(kind='blocks'),
            'entries':lambda d:d.update(entries={}),
            'extra_header':lambda d:d.update(ignored=True),
        }
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'rules.json'
            for name,mutate in mutations.items():
                with self.subTest(name=name):
                    document=deepcopy(base);mutate(document);path.write_text(json.dumps(document))
                    with self.assertRaises(ValueError):load_behaviors(path)
            path.write_text(json.dumps({'schema_version':1,'kind':'buff_behavior','entries':[{'buff_id':22}]}))
            custom=load_behaviors(path)
            self.assertEqual(custom[22],DEFAULT_BEHAVIOR)
            self.assertEqual(behavior_for(22).stat_stacking,'multiplicative')

    def test_root_does_not_refresh_on_stay_or_active_new_source_and_rearms_after_exit(self):
        session,world=self.session()
        actor=session.app.player1
        with patch('pygame.key.get_pressed',return_value=defaultdict(bool)):
            session.advance(1/120)
            root=next(b for b in actor.buffs if b.buff_id==21)
            self.assertEqual(root.duration,5)
            session.advance(2)
            self.assertAlmostEqual(root.duration,3,places=8)
            remaining=root.duration
            actor._x=6.5  # Explicit API placement isolates a second source, not a route claim.
            actor.collide_with_world(world,0)
            self.assertEqual(root.duration,remaining)
            self.assertEqual(root.source,410)
            session.advance(3.02)
            self.assertFalse(actor.has_buff(21))
            session.advance(.2)
            self.assertFalse(actor.has_buff(21))
            actor._x=15.5;actor.collide_with_world(world,0)
            actor._x=5.5;actor.collide_with_world(world,0)
            new=next(b for b in actor.buffs if b.buff_id==21)
            self.assertIsNot(new,root)
            self.assertEqual(new.duration,5)
            actor.remove_buff(21)
            session.advance(1/120)
            self.assertFalse(actor.has_buff(21))
            other=world.create_session()
            actor.collide_with_world(other,0)
            self.assertTrue(actor.has_buff(21))
            self.assertIs(actor._buff_contact_world,other)

    def test_immunity_consumes_entry_and_explicit_api_root_still_refreshes(self):
        session,world=self.session()
        actor=session.app.player1
        with patch('pygame.key.get_pressed',return_value=defaultdict(bool)):
            actor.apply_buff(40,(),.1)
            session.advance(1/120)
            self.assertFalse(actor.has_buff(21))
            session.advance(.2)
            self.assertFalse(actor.has_buff(40))
            self.assertFalse(actor.has_buff(21))
            actor._x=15.5;actor.collide_with_world(world,0)
            actor._x=5.5;actor.collide_with_world(world,0)
            self.assertTrue(actor.has_buff(21))
            actor.apply_buff(21,(),7,source=9999)
            session.advance(.1)
            root=next(b for b in actor.buffs if b.buff_id==21)
            self.assertAlmostEqual(root.duration,6.9,places=8)
            self.assertEqual(root.source,9999)
            actor.apply_buff(40,(),1)
            before=root.duration
            session.advance(.1)
            self.assertLess(root.duration,before)

    def test_pause_and_real_death_preserve_then_rearm_a_fresh_source_timer(self):
        session,world=self.session()
        actor=session.app.player1
        with patch('pygame.key.get_pressed',return_value=defaultdict(bool)):
            session.advance(1/120)
            root=next(b for b in actor.buffs if b.buff_id==21)
            session.app.help_open=True
            session.advance(10)
            self.assertEqual(root.duration,5)
            session.app.help_open=False
            session.advance(.2)
            self.assertAlmostEqual(root.duration,4.8,places=8)
            actor.take_damage(actor.hp_max*10,0)
            self.assertFalse(actor.alive)
            session.advance(1/120)
            current=next(b for b in actor.buffs if b.buff_id==21)
            self.assertIsNot(current,root)
            self.assertEqual(current.duration,5)
            self.assertEqual(current.source,410)
            self.assertEqual(session.app._player_lives_left,4)
            self.assertTrue(actor.has_buff(36))
            self.assertIs(actor._buff_contact_world,world)
