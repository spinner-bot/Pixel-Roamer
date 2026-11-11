"""Exercise the production run loop using native X11/XTest input, not posted SDL events.

Requires a private DISPLAY and xdotool; no window manager is needed. Audio uses
SDL's dummy driver unless the caller explicitly chooses another backend.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import home_page
from pixel_roamer.application import GameApp
from pixel_roamer.ui.config import PAGE_DEV, PAGE_HOME, PAGE_INIT, PAGE_SETTING, PAGE_WORLD


def run(output, xdotool):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    result = {"revision": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "display": os.environ.get("DISPLAY"), "pygame": pygame.version.ver,
        "sdl": pygame.get_sdl_version(), "input": "native XTest via xdotool",
        "scope": "virtual X11 desktop, not physical-device acceptance", "steps": [],
        "errors": []}
    app = GameApp()
    result["video_driver"] = pygame.display.get_driver()
    result["mixer"] = pygame.mixer.get_init()
    other = None
    commands = []
    state = {}
    started = time.monotonic()

    def native(*args):
        commands.append(list(map(str, args)))
        return subprocess.check_output([xdotool, *map(str, args)], text=True).strip()

    def window():
        return native("search", "--onlyvisible", "--pid", os.getpid()).splitlines()[0]

    def key(name):
        native("key", "--clearmodifiers", name)

    def require(condition, message):
        if not condition:
            raise AssertionError(message)

    def page(expected):
        require(app.page == expected, f"expected page {expected}, got {app.page}")

    def shot(name):
        target = output.with_name(output.stem + "_" + name + ".png")
        pygame.image.save(app.win_surface, str(target))
        return target.name

    def click(logical_point):
        x, y = logical_point
        native("mousemove", "--window", window(),
               round(x * app.scale + app.draw_offset_x),
               round(y * app.scale + app.draw_offset_y))
        native("click", 1)

    def boot():
        require(result["video_driver"] == "x11", "requires real x11 SDL driver")
        page(PAGE_INIT)
        native("windowfocus", "--sync", window())
        key("Escape")

    def home():
        page(PAGE_HOME)
        state["home_screenshot"] = shot("home")
        click(home_page.menu_layout(1600, 900)[1].center)

    def settings():
        page(PAGE_SETTING)
        key("Escape")

    def resize(width, height):
        native("windowsize", window(), width, height)

    def check_size(width, height):
        actual = app.win_surface.get_size()
        require(actual == (width, height), f"native size {actual} != {(width, height)}")
        require((app.win_w, app.win_h) == actual, "surface/app dimensions disagree")
        require(abs(app.scale - min(width / 1600, height / 900)) < 1e-12,
                "letterbox scale is wrong")
        state.setdefault("sizes", []).append({"size": actual, "scale": app.scale,
            "offset": [app.draw_offset_x, app.draw_offset_y]})

    def home_resized():
        page(PAGE_HOME)
        check_size(800, 600)
        state["resized_screenshot"] = shot("home_800x600")
        click(home_page.menu_layout(1600, 900)[0].center)

    def select():
        page(PAGE_DEV)
        key("Home")
        key("Return")

    def start_move():
        page(PAGE_WORLD)
        require(app._current_map.map_id == 1, "normal first map was not selected")
        state["move_start"] = app.player1.get_center()[0]
        native("keydown", "d")

    def stop_move():
        require(pygame.key.get_pressed()[pygame.K_d], "native held D was not observed")
        state["move_end"] = app.player1.get_center()[0]
        require(state["move_end"] > state["move_start"] + .5, "held D did not move player")
        native("keyup", "d")
        key("h")

    def help_start():
        require(app.help_open, "help did not open")
        state["help_start"] = [app._game_timer, app.player1.get_center()[0], app.player1.get_center()[1]]

    def help_end():
        require(state["help_start"] == [app._game_timer, app.player1.get_center()[0], app.player1.get_center()[1]],
                "help did not freeze game state")
        key("Escape")
        key("BackSpace")

    def pause_start():
        page(PAGE_SETTING)
        state["pause_start"] = [app._game_timer, app.player1.get_center()[0], app.player1.get_center()[1]]

    def pause_end():
        require(state["pause_start"] == [app._game_timer, app.player1.get_center()[0], app.player1.get_center()[1]],
                "settings did not freeze game state")
        key("Escape")
        resize(1000, 500)

    def world_resized():
        page(PAGE_WORLD)
        check_size(1000, 500)
        state["world_screenshot"] = shot("world_1000x500")

    def focus_away():
        nonlocal other
        other = subprocess.Popen(["xmessage", "-name", "pixel-roamer-audit-focus",
                                  "-buttons", "OK", "Private audit focus target"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def lose_focus():
        wid = native("search", "--onlyvisible", "--pid", other.pid).splitlines()[0]
        native("windowfocus", "--sync", wid)

    def unfocused_start():
        require(not app.focused, "native focus loss was not observed")
        state["unfocused_start"] = [app._game_timer, app.player1.get_center()[0], app.player1.get_center()[1]]
        native("key", "space")

    def unfocused_end():
        require(state["unfocused_start"] == [app._game_timer, app.player1.get_center()[0], app.player1.get_center()[1]],
                "unfocused game advanced")
        native("windowfocus", "--sync", window())

    def regain_focus():
        require(app.focused, "native focus gain was not observed")
        require(not app.jump_pressed, "unfocused key leaked into resumed game")
        key("Escape")

    def editor():
        page(PAGE_DEV)
        key("e")

    def begin_number():
        require(app._dev_edit_mode, "editor did not open")
        key("Return")

    def type_number():
        require(app._dev_inputting, "numeric text input did not open")
        native("type", "--clearmodifiers", "--delay", 15, "-12.25")

    def check_number():
        require(app._dev_input_text == "-12.25", f"native TEXTINPUT: {app._dev_input_text!r}")
        state["native_text"] = app._dev_input_text
        # Cancel: this audit must not save or rename the user's maps.
        key("Escape")
        key("Escape")
        resize(200, 100)

    def minimum_size():
        page(PAGE_DEV)
        check_size(320, 180)
        state["minimum_screenshot"] = shot("minimum_320x180")
        key("Escape")

    def finish():
        page(PAGE_HOME)
        key("4")  # Native menu quit exercises the production QUIT branch.

    steps = [("boot", .7, boot), ("home_mouse_settings", .4, home),
        ("settings_return", .4, settings), ("home_resize", .3, lambda: resize(800, 600)),
        ("letterbox_mouse_start", .4, home_resized), ("map_select", .4, select),
        ("held_movement_start", .7, start_move), ("held_movement_end", .8, stop_move),
        ("help_pause_start", .3, help_start), ("help_pause_end", .6, help_end),
        ("settings_pause_start", .3, pause_start), ("settings_pause_end", .6, pause_end),
        ("world_resize", .5, world_resized), ("focus_target", .2, focus_away),
        ("native_focus_loss", .3, lose_focus), ("unfocused_start", .3, unfocused_start),
        ("unfocused_end", .5, unfocused_end), ("native_focus_gain", .3, regain_focus),
        ("editor_open", .4, editor), ("number_begin", .3, begin_number),
        ("number_type", .3, type_number), ("number_check_cancel", .4, check_number),
        ("minimum_size", .4, minimum_size), ("native_quit", .3, finish)]
    next_at = started + steps[0][1]
    index = frames = 0
    present = app._present_frame

    def observe(dt):
        nonlocal next_at, index, frames
        present(dt)
        frames += 1
        now = time.monotonic()
        if now - started > 90:
            raise TimeoutError("native window audit exceeded its own watchdog")
        if index < len(steps) and now >= next_at:
            name, _, action = steps[index]
            result["current_step"] = name
            action()
            result["steps"].append({"name": name, "elapsed": now - started,
                                    "page": app.page, "frame": frames})
            index += 1
            if index < len(steps):
                next_at = time.monotonic() + steps[index][1]

    app._present_frame = observe
    try:
        app.run()
        require(index == len(steps), "game exited before all audit steps")
        result["completed"] = True
    except Exception:
        result["errors"].append(traceback.format_exc())
        result["completed"] = False
    finally:
        if other is not None:
            other.terminate()
            other.wait(timeout=5)
        result.update(state=state, commands=commands, frames=frames,
                      elapsed=time.monotonic() - started)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--xdotool", default="xdotool")
    args = parser.parse_args()
    result = run(args.output, args.xdotool)
    print(json.dumps({key: result[key] for key in
                     ("completed", "video_driver", "frames", "elapsed", "errors")}, indent=2))
    raise SystemExit(0 if result["completed"] else 1)
