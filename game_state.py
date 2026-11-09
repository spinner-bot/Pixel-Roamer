"""Small, testable state transitions shared by the game loop."""


def resolve_player_death(player, lives_left: int, infinite_lives: bool) -> tuple[int, bool]:
    """Resolve a pending player death; return (lives_left, game_over)."""
    if player.alive:
        return lives_left, False

    if not infinite_lives and lives_left <= 0:
        return 0, True

    if not infinite_lives:
        lives_left -= 1

    saved_score = player.score
    player.clear_buffs()
    player.reset(*player.spawn_pos)
    player.score = saved_score
    player.stamina = player.stamina_max
    player.apply_buff(36, (), 3.0)
    return lives_left, False
