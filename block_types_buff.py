"""Compatibility view of status block definitions."""
from block_types_data import BLOCK_TYPES

BUFF_BLOCKS = {key: value for key, value in BLOCK_TYPES.items() if key >= 360}
