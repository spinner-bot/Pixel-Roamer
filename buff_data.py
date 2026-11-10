"""Register status definitions loaded from data/catalogs/buffs.json."""
from buff_system import BUFF_TYPES
from resource_catalog import load_buffs

BUFF_TYPES.update(load_buffs())
