"""Capture actual source-detail polarity text from production ReferenceBrowser."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from block_types_data import BLOCK_TYPES
from pixel_roamer.application import GameApp
from pixel_roamer.ui.theme import PALETTE


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    app, rows = GameApp(), []
    for block_id in (403, 411):
        app.logic_surface.fill(PALETTE['background'])
        app.references._draw_detail('block', app.logic_surface, BLOCK_TYPES[block_id])
        path = output / f'A84_block_{block_id}.png'
        pygame.image.save(app.logic_surface, str(path))
        rows.append({'block_id': block_id, 'lines': app.references._block_lines(BLOCK_TYPES[block_id]),
                     'image': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)})
    pygame.quit()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'actual ReferenceBrowser detail rendering under SDL dummy; no physical-device or navigation acceptance claim',
              'sources': rows}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(rows, ensure_ascii=False))
