"""Reproduce editor IME loss and numeric confirmation rounding without file writes."""
import argparse
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from pixel_roamer.ui.config import _EDITABLE_FIELDS
LEGACY_REF = '5e6a165'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--legacy', action='store_true')
    args = parser.parse_args()
    pygame.init()
    if args.legacy:
        source = subprocess.check_output(['git', 'show', f'{LEGACY_REF}:pixel_roamer/ui/map_browser.py'],
                                         cwd=ROOT, text=True)
        module = ModuleType('legacy_editor_input_audit')
        sys.modules[module.__name__] = module
        exec(compile(source, f'git:{LEGACY_REF}:map_browser.py', 'exec'), module.__dict__)
    else:
        module = importlib.import_module('pixel_roamer.ui.map_browser')
    app = SimpleNamespace(_dev_edit_mode=True, _dev_block_browser=False, _dev_buff_browser=False,
        _dev_inputting=False, _dev_renaming=True, _dev_selected_id=1, _dev_input_text='',
        _dev_edit_field_idx=0, _dev_error='', _dev_edit_dirty=False, _init_dev_selection=Mock(),
        _dev_edit_config={'world': {'gravity': -6.5}, 'player': {'f_y': .9965}},
        scale=1, draw_offset_x=0, draw_offset_y=0)
    browser = module.MapBrowser(app)
    browser.handle_dev_input(pygame.event.Event(pygame.TEXTINPUT, text='晨光林径'))
    unicode_text = app._dev_input_text
    app._dev_renaming = False
    app._dev_edit_field_idx = next(i for i, field in enumerate(_EDITABLE_FIELDS) if field[0] == 'player.f_y')
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode='', mod=0)
    browser.handle_dev_input(event)
    browser.handle_dev_input(event)
    damping = app._dev_edit_config['player']['f_y']
    app._dev_edit_field_idx = 0
    app._dev_inputting = True
    app._dev_input_text = '--'
    app._dev_error = ''
    browser.handle_dev_input(event)
    report = {'editor_revision': LEGACY_REF if args.legacy else subprocess.check_output(
              ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'committed_unicode': unicode_text, 'damping_before': .9965, 'damping_confirmed': damping,
              'invalid_input_remains_editable': app._dev_inputting, 'invalid_input_error': app._dev_error}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))
    pygame.quit()


if __name__ == '__main__':
    main()
