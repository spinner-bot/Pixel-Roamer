"""Phase through existing anchors, then verify the next real respawn is legal."""
from collections import defaultdict
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from creature import Player
from scripts.control_session import create_control_session
from teleport import can_place
from world import World


def measure(player_class, anchor_id, source, fps):
    spawn = 4.4 if source == 'phantom_gate' else 3.5
    world = World(0, 'checkpoint phase fixture', 64, 15, gravity=0, spawn_points=(spawn, 5.5))
    world.set_tile(5, 5, anchor_id)
    if source == 'phantom_gate':
        world.set_tile(3, 5, 349)
    with patch('player_factory.Player', player_class):
        session = create_control_session(0, world=world)
    player = session.app.player1
    if source == 'ghost_buff':
        player.apply_buff(48, (), 1)
    keys = defaultdict(bool, {pygame.K_d: True})
    with patch('pygame.key.get_pressed', return_value=keys), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for _ in range(4 * fps):
            session.advance(1 / fps)
        saved = {'position': player.spawn_pos, 'clear': can_place(player, world, *player.spawn_pos),
                 'actor_position': player.get_center(), 'actor_clear': can_place(player, world, *player.get_center())}
        # An explicit lethal test hit exercises the normal WorldSession death transition.
        keys.clear()
        player.clear_buffs()
        player.take_raw_damage(1e9)
        for _ in range(3):
            session.advance(1 / fps)
            if player.alive:
                break
        result = {'anchor_id': anchor_id, 'source': source, 'fps': fps, 'saved': saved,
                  'respawn': {'position': player.get_center(), 'clear': can_place(player, world, *player.get_center()),
                              'alive': player.alive, 'count': reset.call_count}}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    module = ModuleType('legacy_checkpoint_player')
    module.__file__ = str(ROOT / 'creature.py')
    source = subprocess.check_output(['git', 'show', 'f783e7c:creature.py'], cwd=ROOT, text=True)
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    cases = [(anchor, source, fps) for anchor in (302, 350, 367)
             for source in ('ghost_buff', 'phantom_gate') for fps in (30, 60, 144)]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'legacy_revision': 'f783e7c',
              'scope': 'isolated existing anchor/ability fixture, real controls and real death recovery; lethal hit deliberately injected',
              'before': [measure(module.Player, *case) for case in cases],
              'after': [measure(Player, *case) for case in cases]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: sum(r['respawn']['clear'] for r in report[name]) for name in ('before', 'after')}))


if __name__ == '__main__':
    main()
