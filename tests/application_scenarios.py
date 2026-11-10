"""Drive the real main loop with deterministic SDL events and a fixed clock."""
import inspect
import json
from pathlib import Path
import runpy
import sys
from unittest.mock import patch

import pygame

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
held_keys = set()


class FixedClock:
    def tick(self, fps=0):
        return 16

    def get_fps(self):
        return 62.5


class KeyState:
    def __getitem__(self, key):
        return key in held_keys


def key(code):
    return [pygame.event.Event(pygame.KEYDOWN, key=code, unicode="", mod=0)]


def scenarios(g):
    assert g["page"] == g["PAGE_INIT"]
    yield key(pygame.K_ESCAPE)
    assert g["page"] == g["PAGE_HOME"]
    yield [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(5, 5))]
    assert g["page"] == g["PAGE_HOME"], "background click activated menu selection"
    yield [pygame.event.Event(pygame.VIDEORESIZE, w=0, h=0)]
    assert g["scale"] > 0
    yield key(pygame.K_RETURN)
    assert g["page"] == g["PAGE_DEV"]
    map_ids = sorted(g["list_maps"]())
    for map_id in map_ids:
        g["_dev_selected_id"] = map_id
        yield key(pygame.K_RETURN)
        assert g["page"] == g["PAGE_WORLD"], map_id
        player = g["player1"]
        timer = g["_game_timer"]
        position = player.get_center()
        yield key(pygame.K_SPACE) + key(pygame.K_BACKSPACE)
        assert g["page"] == g["PAGE_SETTING"]
        assert not g["jump_pressed"]
        for _ in range(3):
            yield []
            assert g["_game_timer"] == timer
            assert player.get_center() == position
        yield key(pygame.K_ESCAPE)
        assert g["page"] == g["PAGE_WORLD"]
        assert g["player1"] is player
        music = g["music"]
        track = music._requested_track[0] if music._requested_track else music.get_current_track()
        assert track == "adventure", (map_id, track)
        yield key(pygame.K_ESCAPE)
        assert g["page"] == g["PAGE_DEV"]

    # Existing control inversion must affect input in the actual main loop.
    g["_dev_selected_id"] = 1
    yield key(pygame.K_RETURN)
    player = g["player1"]
    player._confused = True
    player._confusion_timer = 2
    held_keys.add(pygame.K_d)
    yield []
    assert player.a_x < 0, "confusion did not reverse input"
    held_keys.clear()
    player._confused = False
    player.apply_buff(27, (), 0.05)
    yield key(pygame.K_SPACE)
    for _ in range(5):
        yield []
    assert not g["jump_pressed"] and player.v_y <= 0, "blocked jump leaked into a later frame"
    yield key(pygame.K_ESCAPE)

    # Timed failure and target victory must freeze damage-over-time effects.
    for map_id, terminal in ((8, "_game_over"), (9, "_game_win")):
        g["_dev_selected_id"] = map_id
        yield key(pygame.K_RETURN)
        assert not g["_win_played"] and not g["_death_played"]
        player = g["player1"]
        if map_id == 8:
            g["_game_timer"] = g["_current_map"].time_limit
        else:
            player.score = g["_current_map"].score_goal
        yield []
        assert g[terminal]
        player.apply_buff(16, (20,), 10)
        hp, position = player.hp, player.get_center()
        for _ in range(20):
            yield []
        assert player.hp == hp, "terminal screen still ticks damage"
        assert player.get_center() == position
        yield key(pygame.K_ESCAPE)

    # Finite lives resolve through the real game loop.
    g["_dev_selected_id"] = 7
    yield key(pygame.K_RETURN)
    for remaining in (2, 1, 0):
        player = g["player1"]
        player.clear_buffs()
        player.take_raw_damage(player.hp + player.shield)
        yield []
        assert player.alive and g["_player_lives_left"] == remaining
    player.clear_buffs()
    player.take_raw_damage(player.hp + player.shield)
    yield []
    assert g["_game_over"] and not player.alive
    yield key(pygame.K_ESCAPE)

    # Invalid editor input must remain editable and must not overwrite a file.
    assert g["_get_edit_config"](20)["world"]["fill_color"] == "20,15,30"
    g["_dev_selected_id"] = 1
    g["_dev_edit_config"] = g["_get_edit_config"](1)
    g["_dev_edit_config"]["world"]["gravity"] = float("nan")
    g["_dev_edit_mode"] = True
    g["_dev_edit_dirty"] = True
    yield key(pygame.K_s)
    assert g["_dev_error"] and g["_dev_edit_dirty"]
    yield key(pygame.K_ESCAPE)
    print(json.dumps({"maps_navigated": len(map_ids), "settings_resume": "passed",
                      "terminal_freeze": "passed", "finite_lives": "passed",
                      "confusion_input": "passed", "invalid_editor_save": "passed"}))
    yield [pygame.event.Event(pygame.QUIT)]


driver = None


def events():
    global driver
    if driver is None:
        driver = scenarios(inspect.currentframe().f_back.f_globals)
    return next(driver)


with patch.object(pygame.time, "Clock", FixedClock), patch.object(
        pygame.event, "get", events), patch.object(
        pygame.key, "get_pressed", return_value=KeyState()):
    runpy.run_path(str(ROOT / "main.py"), run_name="__main__")
