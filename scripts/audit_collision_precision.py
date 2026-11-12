"""Compare a previous Player implementation with current contact invariants."""
import argparse
import itertools
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import types

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from creature import Player
from world import World


def contact_matrix(player_type):
    worlds = {}
    failures, samples = 0, []
    max_reverse = 0.0
    cases = itertools.product((5, 8, 16, 32, 64, 128), (2, 4, 5),
                              (5.5, 5.9, 6.0), (1.5, 1.8, 2.0),
                              ("exact", "nextafter", "1e-12", "1e-9"),
                              (30, 60, 144), (-1, 1))
    count = 0
    for top, tile_id, x, height, perturbation, fps, direction in cases:
        key = top, tile_id
        if key not in worlds:
            world = World(0, "precision", 100, 160, edge_behavior="void")
            world.begin_bulk_load()
            for gx in range(2, 40):
                world.set_tile(gx, top - 1, tile_id)
            world.end_bulk_load()
            worlds[key] = world
        y = top + height / 2
        if perturbation == "nextafter":
            y = math.nextafter(y, -math.inf)
        elif perturbation not in ("exact",):
            y -= float(perturbation)
        player = player_type(0, "precision", x, y, {}, h=height)
        player.v_x, player.v_y = direction * 2, -0.1
        player.collide_with_world(worlds[key], 1 / fps)
        dx = player._x - x
        reverse = max(0, -dx * direction)
        max_reverse = max(max_reverse, reverse)
        failed = (reverse > 1e-8 or abs(dx) > 2 / fps + 1e-8
                  or abs(player.get_game_rect().y - top) > 1e-8
                  or player.on_wall_left or player.on_wall_right)
        if failed:
            failures += 1
            if len(samples) < 8:
                samples.append({"top": top, "tile_id": tile_id, "start": [x, y],
                                "height": height, "fps": fps, "direction": direction,
                                "perturbation": perturbation, "end": player.get_center(), "dx": dx})
        count += 1
    return {"cases": count, "failed": failures, "max_reverse_distance": max_reverse,
            "failure_samples": samples}


def passive_ice(player_type):
    results = []
    for tile_id in (3, 75, 86):
        world = World(0, "ice", 200, 30, gravity=-6.5, edge_behavior="void")
        world.begin_bulk_load()
        for x in range(1, 199):
            world.set_tile(x, 4, tile_id)
        world.end_bulk_load()
        player = player_type(0, "ice", 10, 5.9, {})
        player.v_x = 2
        player.collide_with_world(world, 0)
        for _ in range(60):
            player.update_physics(1 / 60, world)
            player.collide_with_world(world, 1 / 60)
        results.append({"tile_id": tile_id, "initial_speed": 2, "final_speed": player.v_x})
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-ref", default="f030083")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # Execute only the historical local Player module in an isolated namespace;
    # no checkout, merge or modification of the working tree is involved.
    source = subprocess.check_output(["git", "show", f"{args.baseline_ref}:creature.py"],
                                     cwd=ROOT, text=True)
    legacy = types.ModuleType("precision_baseline")
    exec(compile(source, f"git:{args.baseline_ref}:creature.py", "exec"), legacy.__dict__)
    report = {"baseline_ref": args.baseline_ref,
              "current_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "scope": "historical/current Player; shared unchanged World queries; deterministic face contacts",
              "before": {"contacts": contact_matrix(legacy.Player), "ice": passive_ice(legacy.Player)},
              "after": {"contacts": contact_matrix(Player), "ice": passive_ice(Player)}}
    report["passed"] = (report["after"]["contacts"]["failed"] == 0 and
                        all(abs(case["final_speed"]) <= 2 + 1e-8 for case in report["after"]["ice"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
