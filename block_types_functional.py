"""Compatibility view of functional block definitions."""
from block_types_data import BLOCK_TYPES

FUNCTIONAL_BLOCKS = {key: value for key, value in BLOCK_TYPES.items() if 330 <= key < 360}
