"""Walk from the original spawn to a polarity source and back, without state injection."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.audit_grand_routes import run
import pygame
import magnetized_field
from teleport import can_place


def continue_from_hall(app, session, keys, fps):
    actor = app.player1
    start = app._game_timer
    phase = 'ladder_align'
    trace, errors = [], []
    force_samples, positive_force_samples = [], []
    sources = Counter()
    reverse_seen, positive_seen = False, False
    returned = False
    min_hp, min_stamina = actor.hp, actor.stamina
    real_force = magnetized_field.apply_field

    def observed_force(creature, world, *args, **kwargs):
        buff = next((b for b in creature.buffs if b.buff_id == 49), None)
        before = creature.v_x
        result = real_force(creature, world, *args, **kwargs)
        if buff is not None:
            sources[str(buff.source)] += 1
            if buff.params and buff.params[0] < 0 and abs(creature.v_x - before) > 1e-8:
                if len(force_samples) < 12:
                    force_samples.append({'position': creature.get_center(), 'source': buff.source,
                                          'params': list(buff.params), 'delta_vx': creature.v_x - before})
        if buff is not None and buff.source == 403 and buff.params and buff.params[0] > 0:
            if abs(creature.v_x - before) > 1e-8 and len(positive_force_samples) < 12:
                positive_force_samples.append({'position': creature.get_center(), 'source': buff.source,
                                               'params': list(buff.params), 'delta_vx': creature.v_x - before})
        return result

    with patch.object(magnetized_field, 'apply_field', side_effect=observed_force):
        for frame in range(120 * fps):
            events = []
            for key in tuple(keys):
                keys[key] = False
            tx = 2993.5
            if phase == 'ladder_align':
                if abs(actor._x - tx) < .15 and abs(actor.v_x) < .5 and actor.stamina >= 85:
                    phase = 'climb'
            if phase == 'climb':
                keys[pygame.K_w] = True
                if actor.can_climb and not actor.is_climbing:
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))
                if actor.is_climbing and actor._y >= 84.05:
                    phase = 'source'
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s))
            if phase == 'source':
                keys[pygame.K_w] = False
                tx = 2982.5
                if any(b.buff_id == 49 and b.params and b.params[0] < 0 for b in actor.buffs):
                    reverse_seen = True
                    phase = 'observe'
                    observe_until = frame + fps // 2
            if phase == 'observe':
                tx = actor._x
                if frame >= observe_until:
                    phase = 'positive_source'
            if phase == 'positive_source':
                tx = 2980.5
                if any(b.buff_id == 49 and b.source == 403 and b.params and b.params[0] > 0 for b in actor.buffs):
                    positive_seen = True
                    phase = 'positive_observe'
                    positive_until = frame + fps // 2
            if phase == 'positive_observe':
                tx = actor._x
                if frame >= positive_until:
                    phase = 'return_ladder'
                    tx = 2993.5
            if phase == 'return_ladder':
                if abs(actor._x - tx) < .15 and abs(actor.v_x) < .5:
                    phase = 'descend'
            if phase == 'descend':
                keys[pygame.K_s] = True
                if actor._y < 77.1:
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s))
                    phase = 'hall'
            if phase in ('hall', 'expire'):
                tx = 3002.5
                if actor.on_ground and abs(actor._x - tx) < .4 and abs(actor._y - 76.9) < .1:
                    phase = 'expire'
                    if not actor.has_buff(23) and not actor.has_buff(49):
                        returned = True
                        break
            desired = max(-4, min(4, (tx - actor._x) * 3))
            error = desired - actor.v_x
            right, left = error > .3, error < -.3
            if actor.has_buff(23) and not actor.has_buff(8) and not actor.has_buff(40):
                right, left = left, right
            keys[pygame.K_d], keys[pygame.K_a] = right, left
            if phase in ('observe', 'positive_observe'):
                keys[pygame.K_d] = keys[pygame.K_a] = False
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            min_hp, min_stamina = min(min_hp, actor.hp), min(min_stamina, actor.stamina)
            if not can_place(actor, app._current_map, *actor.get_center()):
                errors.append({'reason': 'terrain_overlap', 'position': actor.get_center()})
                break
            if app._player_lives_left != 5 or app._game_over or actor.fly_mode:
                errors.append({'reason': 'life_or_debug_state', 'lives': app._player_lives_left})
                break
            if frame % fps == 0:
                trace.append({'seconds': frame / fps, 'phase': phase, 'position': actor.get_center(),
                              'hp': actor.hp, 'stamina': actor.stamina,
                              'buffs': {str(i): {'params': list(b.params), 'source': b.source} for b in actor.buffs for i in (b.buff_id,)}})
    if not returned:
        errors.append({'reason': 'route_incomplete', 'phase': phase, 'position': actor.get_center()})
    if not force_samples:
        errors.append({'reason': 'no_observed_reverse_force'})
    if not positive_force_samples:
        errors.append({'reason': 'no_observed_positive_source_force'})
    return {'positive_seen': positive_seen, 'positive_force_samples': positive_force_samples, 'returned': returned, 'reverse_seen': reverse_seen, 'seconds': app._game_timer - start,
            'phase': phase, 'position': actor.get_center(), 'min_hp': min_hp, 'min_stamina': min_stamina,
            'force_samples': force_samples, 'source_calls': dict(sources), 'errors': errors, 'trace': trace}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--fps', type=int, nargs='+', default=[30, 60, 144])
    args = parser.parse_args()
    revision = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    rows = [run(fps, upper=True, hall_hook=continue_from_hall) for fps in args.fps]
    report = {'code_revision': revision, 'scope': 'original spawn and presets, production input/session, no Buff injection or position transfer; polarity observation calls original field unchanged', 'runs': rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps([{'fps':r['fps'],'route_failure':r['failure'],'gallery':{k:v for k,v in r['hall_extension'].items() if k not in ('trace','force_samples','positive_force_samples')}} for r in rows],ensure_ascii=False))
    return 0 if all(r['failure'] is None and not r['hall_extension']['errors'] for r in rows) else 1


if __name__ == '__main__':
    raise SystemExit(main())
