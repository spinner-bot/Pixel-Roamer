"""A shared simulation clock independent of presentation frame rate."""
import math

SIMULATION_HZ = 120
SIMULATION_STEP = 1 / SIMULATION_HZ


class FixedStepClock:
    def __init__(self):
        self.remainder = 0.0

    def advance(self, elapsed, step):
        if not math.isfinite(elapsed) or elapsed < 0:
            raise ValueError('elapsed time must be finite and nonnegative')
        total = self.remainder + elapsed
        count = int((total + 1e-12) / SIMULATION_STEP)
        self.remainder = max(0.0, total - count * SIMULATION_STEP)
        for _ in range(count):
            step(SIMULATION_STEP)
        return count
