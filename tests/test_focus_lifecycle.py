"""Exercise actual window events and drawing with long restoration elapsed time."""
import os
from pathlib import Path
import subprocess
import sys
import unittest


class FocusLifecycleTests(unittest.TestCase):
    def test_loss_discards_input_damage_and_slider_drag_and_restore_discards_old_elapsed(self):
        root = Path(__file__).resolve().parents[1]
        code = '''import pygame
from pixel_roamer.application import GameApp
from pixel_roamer.ui.config import PAGE_WORLD
app=GameApp()
app.launch_world(1001)
app.page=PAGE_WORLD
actor=app.player1
actor.apply_buff(16,(8,),10)
app.settings._drag_row=2
pygame.event.post(pygame.event.Event(pygame.WINDOWFOCUSLOST))
pygame.event.post(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE))
app._handle_events()
assert not app.focused and not app.jump_pressed
assert app.settings._drag_row is None
for _ in range(3): app._draw_current_page(.25)
assert app._game_timer == 0 and actor.hp == 150 and actor.buffs[-1].duration == 10
pygame.event.post(pygame.event.Event(pygame.WINDOWFOCUSGAINED))
app._handle_events()
app._draw_current_page(60)
assert app.focused and app._game_timer == 0 and actor.hp == 150
app._draw_current_page(1/60)
assert app._game_timer > 0 and actor.hp < 150
pygame.quit()
'''
        env = {**os.environ, 'SDL_VIDEODRIVER': 'dummy', 'SDL_AUDIODRIVER': 'dummy'}
        result = subprocess.run([sys.executable, '-c', code], cwd=root, env=env,
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
