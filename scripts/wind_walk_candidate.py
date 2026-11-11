"""Research-only one-branch directional change; production never imports this file."""
from contextlib import contextmanager
import inspect
import textwrap
from unittest.mock import patch
from creature import Creature


@contextmanager
def directional_candidate():
    original=Creature.update_physics
    source=textwrap.dedent(inspect.getsource(original))
    old='direction = 1.0 if self.v_x > 0 else -1.0'
    new='direction_basis = self.a_x if self.a_x != 0 else self.v_x\n            direction = 1.0 if direction_basis > 0 else -1.0'
    if source.count(old)!=1:
        raise RuntimeError('candidate requires the matching pre-directional physics revision')
    namespace=dict(original.__globals__)
    exec(compile(source.replace(old,new),'<isolated directional wind candidate>','exec'),namespace)
    with patch.object(Creature,'update_physics',namespace['update_physics']):
        yield
