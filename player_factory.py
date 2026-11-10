"""Shared production player construction for application, editor and map audits."""
import inspect
from creature import Player
from map_config import validate_config
from resource_catalog import player_defaults

_INPUT_FIELDS = {'player_id', 'player_name', 'spawn_x', 'spawn_y', 'key_bind'}
_PLAYER_FIELDS = set(inspect.signature(Player).parameters) - _INPUT_FIELDS


def world_player_options(world):
    options = player_defaults()
    if set(options) != _PLAYER_FIELDS | {'costume_id'}:
        raise ValueError('player preset must define every production constructor field')
    config = getattr(world, 'player_config', {})
    options.update({key: value for key, value in config.items() if key in options})
    return validate_config({'player': options})['player']


def create_world_player(world, key_bind, *, player_id=0, player_name='玩家1', position=None):
    options = world_player_options(world)
    costume_id = options.pop('costume_id')
    x, y = world.spawn_points if position is None else position
    player = Player(player_id, player_name, float(x), float(y), key_bind, **options)
    player.costume_id = costume_id
    return player
