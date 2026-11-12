"""Local wind/jump timing samples; initialized at temple entrance, not a full route."""
import os, sys, json, argparse, subprocess
from pathlib import Path
from types import ModuleType
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from collections import defaultdict
from types import SimpleNamespace
from unittest.mock import patch
import pygame
from maps import get_map, _apply_config
from camera import Camera
from player_factory import create_world_player
from pixel_roamer.world_session import WorldSession
parser = argparse.ArgumentParser()
parser.add_argument('--legacy', action='store_true')
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
if args.legacy:
    module = ModuleType('legacy_cove_wind')
    module.__file__ = str(ROOT / 'maps/adventure_cove/map.py')
    source = subprocess.check_output(['git', 'show', '956158f:maps/adventure_cove/map.py'], cwd=ROOT, text=True, encoding='utf-8')
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    w = module.world
    _apply_config(w, 'adventure_cove')
else:
    w = get_map(21)
runs = []
for takeoff in (354, 354.2, 354.4, 354.6, 354.8, 355, 355.2, 355.4, 355.6, 356, 357):
    bindings = dict(left=pygame.K_a, right=pygame.K_d, up=pygame.K_w, down=pygame.K_s, jump=pygame.K_SPACE, fly=pygame.K_f)
    p = create_world_player(w, bindings, position=(354, 77.9))
    app = SimpleNamespace(_current_map=w, player1=p, help_open=False, jump_pressed=False, _game_over=False, _game_win=False, _game_timer=0, _player_lives_left=3, _infinite_lives=False, camera=Camera(640, 360, w), _stamina_flash_timer=0, _stamina_flash_duration=0.6)
    session = WorldSession(app)
    keys = defaultdict(bool)
    maxy = p._y
    maxx = p._x
    jumps = 0
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'):
        for frame in range(120 * 15):
            keys[pygame.K_d] = p._x < 359.5
            keys[pygame.K_a] = p._x > 360
            if p._x >= takeoff and p.on_ground:
                app.jump_pressed = True
                jumps += 1
            session.advance(1 / 120)
            maxy = max(maxy, p._y)
            maxx = max(maxx, p._x)
    runs.append(dict(takeoff=takeoff, max_x=maxx, max_y=maxy, jump_requests=jumps, final=p.get_center(), cleared=maxx > 359 and maxy >= 88.9))
report = {'scope': 'isolated temple entrance jump timing samples; no global reachability proof', 'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'legacy_map': args.legacy, 'runs': runs}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'samples': len(runs), 'cleared': sum((run['cleared'] for run in runs))}))
