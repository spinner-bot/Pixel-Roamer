"""Research candidate only: invert the fixed-step damped jump apex, not imported by gameplay."""
from functools import lru_cache
import math

STEP = 1/120


def apex(speed, gravity, damping):
    """Unobstructed downward-gravity apex for v=(v+g*dt)*damping**(60*dt)."""
    speed = max(0.,float(speed))
    q = max(0.,min(1.,damping)) ** (60*STEP)
    if speed == 0 or q == 0:
        return 0.
    if gravity >= 0:
        if gravity == 0 and q < 1:
            return STEP*speed*q/(1-q)
        return math.inf
    if q == 1:
        n = max(0,math.ceil(speed/(-gravity*STEP))-1)
        return max(0.,STEP*(n*speed+gravity*STEP*n*(n+1)/2))
    terminal = q*gravity*STEP/(1-q)
    n = max(0,math.ceil(math.log((-terminal)/(speed-terminal))/math.log(q))-1)
    summed = (speed-terminal)*q*(-math.expm1(n*math.log(q)))/(1-q)+n*terminal
    return max(0.,STEP*summed)


@lru_cache(maxsize=256)
def launch_speed(base_speed, gravity, damping, height_multiplier):
    if height_multiplier == 1:
        return base_speed
    if height_multiplier <= 0:
        return 0.
    target = apex(base_speed,gravity,damping)*height_multiplier
    if not math.isfinite(target) or target == 0:
        return base_speed*math.sqrt(height_multiplier)
    low, high = 0., max(1.,base_speed)*max(1.,height_multiplier)
    while apex(high,gravity,damping) < target:
        high *= 2
    for _ in range(48):
        mid=(low+high)/2
        if apex(mid,gravity,damping) < target:
            low=mid
        else:
            high=mid
    return (low+high)/2
