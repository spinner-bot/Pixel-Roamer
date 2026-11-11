"""Immutable startup-loaded Buff behavior rules, independent of source blocks."""
from dataclasses import dataclass
import json
from pathlib import Path
from types import MappingProxyType


@dataclass(frozen=True)
class BuffBehavior:
    contact_trigger: str='refresh'
    stat_stacking: str='linear'


DEFAULT_BEHAVIOR=BuffBehavior()
BEHAVIOR_PATH=Path(__file__).resolve().parent/'data/rules/buff_behavior.json'


def load_behaviors(path=BEHAVIOR_PATH,*,known_ids=None):
    document=json.loads(Path(path).read_text(encoding='utf-8'))
    if (not isinstance(document,dict) or set(document)!={'schema_version','kind','entries'}
            or type(document['schema_version']) is not int or document['schema_version']!=1
            or document['kind']!='buff_behavior' or not isinstance(document['entries'],list)):
        raise ValueError('invalid Buff behavior header')
    if known_ids is None:
        from resource_catalog import load_buffs
        known_ids=load_buffs().keys()
    result={}
    for entry in document['entries']:
        if (not isinstance(entry,dict) or set(entry)-{'buff_id','contact_trigger','stat_stacking'}
                or type(entry.get('buff_id')) is not int or entry['buff_id'] not in known_ids
                or entry['buff_id'] in result):
            raise ValueError('unknown, duplicate or invalid Buff behavior entry')
        contact=entry.get('contact_trigger','refresh')
        stacking=entry.get('stat_stacking','linear')
        if contact not in ('refresh','entry') or stacking not in ('linear','multiplicative'):
            raise ValueError('unsupported Buff behavior policy')
        result[entry['buff_id']]=BuffBehavior(contact,stacking)
    return MappingProxyType(result)


BEHAVIORS=load_behaviors()

def behavior_for(buff_id):
    return BEHAVIORS.get(buff_id,DEFAULT_BEHAVIOR)
