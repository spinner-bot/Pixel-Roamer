"""Reproducible headless stress audit; results are evidence, not a playability proof."""
import argparse
import inspect
import json
import math
import os
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame
from camera import Camera
from creature import Player
from game_state import resolve_player_death
from maps import get_map, list_maps
from world import World, MAX_CHUNK_SURFACES, MAX_SCALED_CACHE_BYTES
from block_types_data import BLOCK_TYPES
from simulation import FixedStepClock, SIMULATION_HZ


def finite_player(player):
    return all(math.isfinite(value) for value in
               (*player.get_center(), player.v_x, player.v_y, player.hp, player.stamina))


def map_audit(map_id, frames):
    started = time.perf_counter()
    world = get_map(map_id)
    config = world.player_config
    kwargs = {key: value for key, value in config.items()
              if key in inspect.signature(Player).parameters}
    player = Player(0, "audit", *world.spawn_points, {}, **kwargs)
    rect = player.get_game_rect()
    overlaps = [(block.x, block.y, kind.id)
                for block, kind in world.get_nearby_solid_blocks_game(rect)
                if rect.collides(block)]
    score_total = sum(world.block_types[tile.type_id].special_data
                      for tile in world.grid.values()
                      if world.block_types[tile.type_id].special == "score")
    errors = []
    if overlaps:
        errors.append("spawn overlaps solid terrain")
    if world.mode == "score_target" and score_total < world.score_goal:
        errors.append("insufficient score blocks")
    if world.mode == "explore" and not any(
            world.block_types[tile.type_id].special == "end_point" for tile in world.grid.values()):
        errors.append("missing endpoint")
    surface = pygame.Surface((640, 360))
    camera = Camera(640, 360, world)
    physics_ms = []
    draw_ms = []
    respawns = 0
    clock = FixedStepClock()

    def step(dt):
        player.tick_buffs(dt)
        player.refresh_movement_stats()
        player.update_physics(dt, world)
        player.collide_with_world(world, dt)

    for frame in range(frames):
        if not player.alive:
            resolve_player_death(player, 0, True)
            respawns += 1
        start = time.perf_counter()
        player.move(0.35 if (frame // 240) % 2 == 0 else -0.35)
        if frame % 60 == 0:
            player.jump()
        clock.advance(1 / 60, step)
        physics_ms.append((time.perf_counter() - start) * 1000)
        if not finite_player(player):
            errors.append(f"nonfinite player state at frame {frame}")
            break
        if frame % 120 == 0:
            camera.follow(*player.get_center())
            start = time.perf_counter()
            world.draw(surface, camera)
            draw_ms.append((time.perf_counter() - start) * 1000)
            if (len(world._chunk_surfaces) > MAX_CHUNK_SURFACES
                    or world._scaled_chunk_cache_bytes > MAX_SCALED_CACHE_BYTES):
                errors.append(f"render cache exceeded budget at frame {frame}")
    return {
        "id": map_id, "name": world.name, "frames": len(physics_ms),
        "simulated_seconds": len(physics_ms) / 60, "spawn": world.spawn_points,
        "spawn_overlaps": overlaps, "respawns_in_stress_run": respawns,
        "score": player.score, "physics_mean_ms": statistics.mean(physics_ms),
        "physics_p95_ms": sorted(physics_ms)[int(len(physics_ms) * 0.95)],
        "physics_max_ms": max(physics_ms), "draw_max_ms": max(draw_ms),
        "base_chunk_cache_count": len(world._chunk_surfaces),
        "scaled_cache_bytes": world._scaled_chunk_cache_bytes,
        "elapsed_seconds": time.perf_counter() - started, "errors": errors,
    }


def block_audit(frames):
    failures = []
    slowest = {"id": None, "elapsed_ms": 0}
    for tile_id in sorted(BLOCK_TYPES):
        world = World(0, "block", 30, 30, gravity=-6.5, edge_behavior="void")
        world.set_tile(5, 5, tile_id)
        player = Player(0, "block", 5.5, 5.5, {})
        clock = FixedStepClock()

        def step(dt):
            player.tick_buffs(dt)
            player.update_physics(dt, world)
            player.collide_with_world(world, dt)

        started = time.perf_counter()
        try:
            for _ in range(frames):
                clock.advance(1 / 60, step)
                if not finite_player(player):
                    raise AssertionError("nonfinite player state")
                if not player.alive:
                    break
        except Exception as error:
            failures.append({"id": tile_id, "error": repr(error)})
        elapsed = (time.perf_counter() - started) * 1000
        if elapsed > slowest["elapsed_ms"]:
            slowest = {"id": tile_id, "elapsed_ms": elapsed}
    return {"types_checked": len(BLOCK_TYPES), "frames_per_type": frames,
            "failures": failures, "slowest_case": slowest}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=1800)
    parser.add_argument("--block-frames", type=int, default=60)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.frames <= 0 or args.block_frames <= 0:
        parser.error("frame counts must be positive")
    pygame.init()
    random.seed(20261111)
    report = {"python": platform.python_version(), "pygame": pygame.version.ver,
              "simulation_hz": SIMULATION_HZ,
              "video_driver": pygame.display.get_driver(), "seed": 20261111,
              "code_revision": subprocess.check_output(
                  ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "scope": "synthetic input; no assertion of full map completion or real device behavior",
              "maps": []}
    try:
        for map_id in sorted(list_maps()):
            result = map_audit(map_id, args.frames)
            report["maps"].append(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)
        report["blocks"] = block_audit(args.block_frames)
        report["passed"] = (not any(m["errors"] for m in report["maps"])
                            and not report["blocks"]["failures"])
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        print(json.dumps({"passed": report["passed"], "blocks": report["blocks"]}, ensure_ascii=False))
    finally:
        pygame.quit()
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
