"""Capture actual source detail pages and ghost traversal in GameApp/WorldView."""
from collections import defaultdict
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from block_types_data import BLOCK_TYPES
from pixel_roamer.application import GameApp
from pixel_roamer.ui.config import PAGE_WORLD
from pixel_roamer.ui.theme import PALETTE
from world import World


def capture(output):
    output = output.resolve()
    def image_ref(path):
        return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    app = GameApp()
    result = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'SDL dummy actual ReferenceBrowser and GameApp/WorldView; explicit authored fixture, no physical-device or original-map route claim',
              'details': [], 'traversal': {}}
    output.mkdir(parents=True, exist_ok=True)
    for tile_id in (363, 364, 384):
        app.logic_surface.fill(PALETTE['background'])
        app.references._draw_detail('block', app.logic_surface, BLOCK_TYPES[tile_id])
        path = output / f'A81_block_{tile_id}.png'
        pygame.image.save(app.logic_surface, str(path))
        result['details'].append({'block_id': tile_id, 'lines': app.references._block_lines(BLOCK_TYPES[tile_id]),
                                  'image': image_ref(path)})
    world = World(0, '幽灵墙接触审计', 36, 18, gravity=-9.8, spawn_points=(6.5, 5.9))
    for x in range(2, 34):
        world.set_tile(x, 4, 2)
    for y in range(5, 10):
        world.set_tile(10, y, 384)
    with patch('pixel_roamer.application.get_map', return_value=world):
        app.set_page(PAGE_WORLD, map_id=0)
    actor, session = app.player1, app.session
    keys = defaultdict(bool, {pygame.K_d: True})
    shots, min_foot = {}, actor._y - actor._h / 2
    def picture(label):
        app.world_view.draw(0)
        path = output / f'A81_ghost_{label}.png'
        pygame.image.save(app.logic_surface, str(path))
        buff = next((b for b in actor.buffs if b.buff_id == 48), None)
        shots[label] = {'time': app._game_timer, 'position': actor.get_center(),
                        'source': buff.source if buff else None,
                        'description': buff.format_desc() if buff else None,
                        'image': image_ref(path)}
    picture('before')
    with patch('pygame.key.get_pressed', return_value=keys), patch.object(actor, 'reset', wraps=actor.reset) as reset:
        for _ in range(3 * 60):
            session.advance(1 / 60)
            min_foot = min(min_foot, actor._y - actor._h / 2)
            if actor.has_buff(48) and actor._x + actor._w / 2 > 10 and actor._x - actor._w / 2 < 11:
                if 'inside' not in shots:
                    picture('inside')
            if actor._x - actor._w / 2 >= 11:
                picture('after')
                break
        respawns = reset.call_count
    result['traversal'] = {'shots': shots, 'crossed': 'after' in shots,
                           'min_foot_y': min_foot, 'hp': actor.hp, 'respawns': respawns}
    pygame.quit()
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = capture(args.output_dir)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'details': len(result['details']), 'traversal': result['traversal']['crossed']}))
