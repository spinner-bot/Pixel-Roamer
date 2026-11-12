"""Render-only freeze feedback must be local, legible and bounded at any zoom."""
import os
import unittest
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame
from camera import Camera
from creature import Player
from pixel_roamer.frozen_feedback import draw_frozen_feedback
from world import World


class FrozenFeedbackTests(unittest.TestCase):
    def setUp(self):
        self.actor=Player(0,'feedback',20,16,{})
        self.world=World(0,'feedback fixture',40,32,view_blocks_h=12)
        self.camera=Camera(320,180,self.world)
        self.camera.follow(20,16)
        self.surface=pygame.Surface((320,180),pygame.SRCALPHA)
        self.surface.fill((61,49,37,255))

    def state(self):
        a=self.actor
        return (a.get_center(),a.v_x,a.v_y,a.a_x,a.a_y,a.hp,a.stamina,
                [(b.buff_id,b.params,b.duration,b.stacks,b.source) for b in a.buffs])

    def test_unaffected_cold_expired_dead_and_offscreen_actors_do_not_draw(self):
        original=pygame.image.tobytes(self.surface,'RGBA')
        self.assertIsNone(draw_frozen_feedback(self.surface,self.actor,self.camera))
        self.actor.apply_buff(51,(),5)
        self.assertIsNone(draw_frozen_feedback(self.surface,self.actor,self.camera))
        self.actor.apply_buff(59,(),0)
        self.assertIsNone(draw_frozen_feedback(self.surface,self.actor,self.camera))
        self.actor.apply_buff(59,(),4)
        self.actor.alive=False
        self.assertIsNone(draw_frozen_feedback(self.surface,self.actor,self.camera))
        self.actor.alive=True
        self.camera.x=self.camera.y=0
        self.assertIsNone(draw_frozen_feedback(self.surface,self.actor,self.camera))
        self.assertEqual(pygame.image.tobytes(self.surface,'RGBA'),original)

    def test_active_cue_changes_only_actor_and_label_region_and_preserves_all_simulation(self):
        self.actor.apply_buff(59,(),3.45)
        body=self.camera.game_rect_to_screen_rect(self.actor.get_game_rect())
        pygame.draw.rect(self.surface,(180,70,55),body)
        before=self.surface.copy()
        state=self.state()
        result=draw_frozen_feedback(self.surface,self.actor,self.camera)
        self.assertEqual(result['text'],'冻结 3.5s')
        self.assertEqual(self.state(),state)
        region=result['body'].union(result['label'])
        differences=[(x,y) for y in range(180) for x in range(320)
                     if before.get_at((x,y))!=self.surface.get_at((x,y))]
        self.assertGreater(len(differences),100)
        self.assertTrue(all(region.collidepoint(point) for point in differences))
        self.assertGreater(self.surface.get_at(body.center).r,130)

    def test_countdown_pause_permanence_and_iron_will_follow_actual_buff_lifecycle(self):
        self.actor.apply_buff(59,(),.008)
        first=draw_frozen_feedback(self.surface,self.actor,self.camera)
        self.assertEqual(first['text'],'冻结 0.1s')
        frame=pygame.image.tobytes(self.surface,'RGBA')
        self.surface.fill((61,49,37,255))
        second=draw_frozen_feedback(self.surface,self.actor,self.camera)
        self.assertEqual(first,second)
        self.assertEqual(pygame.image.tobytes(self.surface,'RGBA'),frame)
        self.actor.apply_buff(8,(),5)
        self.assertIsNotNone(draw_frozen_feedback(self.surface,self.actor,self.camera))
        self.actor.apply_buff(40,(),5)
        self.assertIsNone(draw_frozen_feedback(self.surface,self.actor,self.camera))
        self.actor.clear_buffs()
        self.actor.apply_buff(59,(),None)
        self.assertEqual(draw_frozen_feedback(self.surface,self.actor,self.camera)['text'],'冻结')
        self.actor.apply_buff(59,(),10**400)
        self.assertEqual(draw_frozen_feedback(self.surface,self.actor,self.camera)['text'],'冻结 999+s')

    def test_extreme_zoom_allocates_only_visible_body_and_small_label(self):
        self.actor.apply_buff(59,(),4)
        self.camera.scale=1e8
        original=pygame.Surface
        sizes=[]
        def create(size,*args,**kwargs):
            sizes.append(size)
            return original(size,*args,**kwargs)
        with patch('pygame.Surface',new=create):
            result=draw_frozen_feedback(self.surface,self.actor,self.camera)
        self.assertIsNotNone(result)
        self.assertTrue(sizes)
        self.assertTrue(all(w<=320 and h<=180 for w,h in sizes))
