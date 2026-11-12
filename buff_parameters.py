"""Shared primary defaults for effect consumers and their displayed descriptions.

An empty parameter list uses these defaults; an explicit zero remains zero.
Context-specific secondary behavior (for example chilled friction) keeps its
own default rather than silently changing the primary parameter's meaning.
"""

import math


DEFAULT_PARAMETERS = {
    'regen': 3, 'shield_regen': 2, 'swiftness': 30, 'leaping': 50,
    'vigor': 50, 'endurance': 30, 'fortify': 30, 'thornmail': 30,
    'lifesteal': 15, 'cleansing': 5, 'feather': 50, 'burning': 5,
    'bleeding': 1, 'weakened': 2, 'fatigue': 50, 'grievous_wound': 50,
    'slowed': 50, 'narrow_vision': 5, 'slick': 85, 'sticky': 80,
    'drowsy': 4, 'electrified': 8, 'berserk': 5, 'chilled': 40,
    'wind_walk': .5, 'anchored': 100, 'parasitic': 3, 'magnetized': 1,
}


def magnetic_response(params):
    """Signed susceptibility: default +1, zero neutral, magnitude bounded to 4."""
    value = float(params[0]) if params else DEFAULT_PARAMETERS['magnetized']
    return max(-4., min(4., value)) if math.isfinite(value) else 0.
