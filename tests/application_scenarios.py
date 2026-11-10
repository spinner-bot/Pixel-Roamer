"""Drive the real main loop with deterministic SDL events and a fixed clock."""
import inspect
import json
import os
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


def capture(g, name):
    directory = os.environ.get("PIXEL_ROAMER_SCREENSHOT_DIR")
    if directory:
        target = Path(directory)
        target.mkdir(parents=True, exist_ok=True)
        pygame.image.save(g["logic_surface"], str(target / f"{name}.png"))


def scenarios(g):
    assert g["page"] == g["PAGE_INIT"]
    yield []
    assert g["ls"].is_loading_complete(), "startup imposed a fake wait after resources were ready"
    capture(g, "loading")
    yield key(pygame.K_ESCAPE)
    assert g["page"] == g["PAGE_HOME"]
    capture(g, "home")
    yield [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(5, 5))]
    assert g["page"] == g["PAGE_HOME"], "background click activated menu selection"
    yield key(pygame.K_3)
    assert g["page"] == g["PAGE_DEV"] and g["_dev_block_browser"]
    yield key(pygame.K_ESCAPE)
    yield key(pygame.K_ESCAPE)
    assert g["page"] == g["PAGE_HOME"]
    yield [pygame.event.Event(pygame.VIDEORESIZE, w=0, h=0)]
    assert g["scale"] > 0
    yield key(pygame.K_KP_ENTER)
    assert g["page"] == g["PAGE_DEV"]
    capture(g, "maps")
    yield key(pygame.K_b)
    assert g["_dev_block_browser"]
    capture(g, "blocks")
    yield key(pygame.K_RETURN)
    assert g["_dev_block_detail_id"] is not None
    yield key(pygame.K_ESCAPE)
    yield key(pygame.K_TAB)
    yield key(pygame.K_b)
    assert not g["_dev_block_browser"]
    yield key(pygame.K_u)
    assert g["_dev_buff_browser"]
    capture(g, "buffs")
    yield key(pygame.K_RETURN)
    assert g["_dev_buff_detail_id"] is not None
    yield key(pygame.K_ESCAPE)
    yield key(pygame.K_TAB)
    yield key(pygame.K_u)
    assert not g["_dev_buff_browser"]
    map_ids = sorted(g["list_maps"]())
    for map_id in map_ids:
        g["_dev_selected_id"] = map_id
        yield key(pygame.K_RETURN)
        assert g["page"] == g["PAGE_WORLD"], map_id
        if map_id == map_ids[0]:
            actor = g['player1']
            actor.apply_buff(16, (8,), 10)
            duration = actor.buffs[-1].duration
            hp = actor.hp
            paused = g['_game_timer']
            position = actor.get_center()
            g['settings']._drag_row = 2
            yield [pygame.event.Event(pygame.WINDOWFOCUSLOST)] + key(pygame.K_SPACE)
            assert not g['focused'] and not g['jump_pressed']
            assert g['settings']._drag_row is None
            for _ in range(3):
                yield []
                assert g['_game_timer'] == paused and actor.get_center() == position
                assert actor.hp == hp and actor.buffs[-1].duration == duration
            capture(g, 'focus_pause')
            yield [pygame.event.Event(pygame.WINDOWFOCUSGAINED)]
            assert g['focused'] and not g['jump_pressed']
            assert g['_game_timer'] == paused and actor.hp == hp
            yield []
            assert g['_game_timer'] > paused and actor.hp < hp
            actor.remove_buff(16)
            paused_time = g["_game_timer"]
            position = g["player1"].get_center()
            yield key(pygame.K_h)
            assert g["help_open"]
            for _ in range(3):
                yield []
                assert g["_game_timer"] == paused_time
                assert g["player1"].get_center() == position
            capture(g, "help")
            yield key(pygame.K_ESCAPE)
            assert g["page"] == g["PAGE_WORLD"] and not g["help_open"]
        player = g["player1"]
        timer = g["_game_timer"]
        position = player.get_center()
        yield key(pygame.K_SPACE) + key(pygame.K_BACKSPACE)
        assert g["page"] == g["PAGE_SETTING"]
        assert not g["jump_pressed"]
        if map_id == map_ids[0]:
            capture(g, "settings")
        for _ in range(3):
            yield []
            assert g["_game_timer"] == timer
            assert player.get_center() == position
        yield key(pygame.K_ESCAPE)
        assert g["page"] == g["PAGE_WORLD"]
        assert g["player1"] is player
        music = g["music"]
        track = music._requested_track[0] if music._requested_track else music.get_current_track()
        if pygame.mixer.get_init():
            assert track == "adventure", (map_id, track)
        else:
            assert not music.is_playing()
        yield key(pygame.K_ESCAPE)
        assert g["page"] == g["PAGE_DEV"]

    # Existing control inversion must affect input in the actual main loop.
    g["_dev_selected_id"] = 1
    yield key(pygame.K_RETURN)
    player = g["player1"]
    for flying in (False, True):
        player.fly_mode = flying
        player._confused = player._phantom_active = True
        player._confusion_timer = player._phantom_timer = 0.03
        player.can_swim = True
        player.apply_buff(28, (), 0.05 if not flying else 0)
        for _ in range(5):
            yield []
        assert not player._confused and not player._phantom_active
        if flying:
            assert not player.can_swim and not player.can_climb
    player.fly_mode = False
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
    world = g['_current_map']
    for x in range(4, 8):
        for y in range(4, 9):
            world.set_tile(x, y, 0)
    world.set_tile(5, 5, 9)
    player.reset(6.1, 5.7)
    player.collide_with_world(world, 0)
    player.apply_buff(28, (), .2)
    before_x = player._x
    yield key(pygame.K_w)
    assert player._x == before_x and not player.is_climbing, 'stun allowed ladder capture'
    for _ in range(15):
        yield []
    assert not player.has_buff(28) and not player.is_climbing
    assert player._x == before_x, 'blocked climb leaked after stun expiry'
    yield key(pygame.K_w)
    assert player.is_climbing and player._x == 5.5
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
    yield key(pygame.K_e)
    from pixel_roamer.ui.config import _EDITABLE_FIELDS
    fields = _EDITABLE_FIELDS
    g['_dev_edit_field_idx'] = next(i for i, field in enumerate(fields) if field[0] == 'player.f_y')
    g['_dev_edit_config']['player']['f_y'] = .9965
    yield key(pygame.K_KP_ENTER)
    assert g['_dev_inputting'] and g['_dev_input_text'] == '0.9965'
    capture(g, 'editor_value')
    yield [pygame.event.Event(pygame.TEXTINPUT, text='0.9965')]
    yield key(pygame.K_KP_ENTER)
    assert g['_dev_edit_config']['player']['f_y'] == .9965
    original_folder = g['list_maps']()[1]
    yield key(pygame.K_r)
    yield [pygame.event.Event(pygame.TEXTEDITING, text='晨', start=0, length=1)]
    capture(g, 'editor_ime')
    yield key(pygame.K_RETURN)
    assert g['_dev_renaming'], 'IME confirmation submitted the rename prematurely'
    yield [pygame.event.Event(pygame.TEXTINPUT, text='晨光演示')]
    assert g['_dev_input_text'] == '晨光演示'
    yield [pygame.event.Event(pygame.WINDOWFOCUSLOST), pygame.event.Event(pygame.TEXTINPUT, text='应忽略')]
    assert g['_dev_input_text'] == '晨光演示'
    yield [pygame.event.Event(pygame.WINDOWFOCUSGAINED)]
    yield key(pygame.K_ESCAPE)
    assert not g['_dev_renaming'] and not g['_dev_inputting']
    yield key(pygame.K_ESCAPE)
    assert g['list_maps']()[1] == original_folder
    print(json.dumps({"maps_navigated": len(map_ids), "settings_resume": "passed",
                      "terminal_freeze": "passed", "finite_lives": "passed",
                      "confusion_input": "passed", "invalid_editor_save": "passed",
                      "editor_text_input": "passed"}))
    yield [pygame.event.Event(pygame.QUIT)]


driver = None


class AppContext:
    """Expose the live application to the existing scenario assertions."""
    def __init__(self, app):
        self.app = app
        self.module = sys.modules[type(app).__module__]

    def __getitem__(self, key):
        if hasattr(self.app, key):
            return getattr(self.app, key)
        for component in (self.app.map_browser, self.app.references, self.app.hud, self.app.settings):
            if hasattr(component, key):
                return getattr(component, key)
        return getattr(self.module, key)

    def __setitem__(self, key, value):
        setattr(self.app, key, value)


def events():
    global driver
    if driver is None:
        driver = scenarios(AppContext(inspect.currentframe().f_back.f_locals["self"]))
    return next(driver)


with patch.object(pygame.time, "Clock", FixedClock), patch.object(
        pygame.event, "get", events), patch.object(
        pygame.key, "get_pressed", return_value=KeyState()):
    runpy.run_path(str(ROOT / "main.py"), run_name="__main__")
