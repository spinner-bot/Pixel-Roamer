"""Compare actual launch, editor and map-audit presets without loading a map."""
import argparse
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from creature import Player
from world import World
from player_factory import create_world_player
from resource_catalog import player_defaults
LEGACY_REF = 'f887d96'


def legacy_module(path, name):
    source = subprocess.check_output(['git', 'show', f'{LEGACY_REF}:{path}'], cwd=ROOT, text=True)
    module = ModuleType(name)
    module.__file__ = str(ROOT / path)
    sys.modules[name] = module
    exec(compile(source, f'git:{LEGACY_REF}:{path}', 'exec'), module.__dict__)
    return module


def snapshot(player):
    return {key: getattr(player, {'w': '_w', 'h': '_h'}.get(key, key)) for key in player_defaults()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--legacy', action='store_true')
    args = parser.parse_args()
    if args.legacy:
        application = legacy_module('pixel_roamer/application.py', 'legacy_preset_application')
        editor_module = legacy_module('pixel_roamer/ui/map_browser.py', 'legacy_preset_editor')
    else:
        application = importlib.import_module('pixel_roamer.application')
        editor_module = importlib.import_module('pixel_roamer.ui.map_browser')
    world = World(0, 'presets', 30, 30, spawn_points=(5.5, 5.5))
    app = application.GameApp.__new__(application.GameApp)
    app.p1_keys = {}
    app._play_world_music = lambda _: None
    with patch.object(application, 'get_map', return_value=world):
        app.launch_world(0)
    with patch.object(editor_module, 'get_map', return_value=world), \
         patch.object(editor_module, 'load_map_config', return_value={}):
        editor = editor_module.MapBrowser(SimpleNamespace())._get_edit_config(0)['player']
    audit_player = (Player(0, 'audit', *world.spawn_points, {}) if args.legacy
                    else create_world_player(world, {}, player_name='audit'))
    actual = snapshot(app.player1)
    audit = snapshot(audit_player)
    report = {'application_revision': LEGACY_REF if args.legacy else subprocess.check_output(
              ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'application': actual, 'editor': editor, 'map_audit': audit,
              'editor_differences': [key for key in actual if actual[key] != editor[key]],
              'audit_differences': [key for key in actual if actual[key] != audit[key]]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ('editor_differences', 'audit_differences')}))


if __name__ == '__main__':
    main()
