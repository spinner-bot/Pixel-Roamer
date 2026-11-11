"""Normal input targets for the existing two-step west hub departure."""


def west_departure(player, stage):
    if (stage == 0 and player.on_ground and abs(player._x - 21.5) < .2
            and abs(player._y - 18.9) < .1):
        stage = 1
    done = (stage == 1 and player.on_ground and player._x < 20.4
            and abs(player._y - 22.9) < .05)
    return stage, 21.5 if stage == 0 else 19.5, player.on_ground and not done, done
