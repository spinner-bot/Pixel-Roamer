"""Height bonuses calibrated to the fixed-step, damped free-flight trajectory."""
from decimal import Decimal, localcontext
from functools import lru_cache
import math
from simulation import SIMULATION_STEP


def jump_apex(speed, gravity, damping):
    """Unobstructed rise, with gravity then damping then movement each tick."""
    speed=max(0.,float(speed))
    q=max(0.,min(1.,damping)) ** (60*SIMULATION_STEP)
    if speed == 0 or q == 0:
        return 0.
    fall=-gravity*SIMULATION_STEP
    if gravity >= 0 or fall == 0:
        return SIMULATION_STEP*speed*q/(1-q) if gravity <= 0 and q < 1 else math.inf
    if q == 1:
        steps=speed/fall
        if not math.isfinite(steps):
            return math.inf
        n=max(0,math.ceil(steps)-1)
        return max(0.,SIMULATION_STEP*n*(speed-fall*(n+1)/2))
    logq=math.log(q)
    # log(1 + speed*(1-q)/(fall*q)) without overflow or a ratio
    # rounded to one. The root is the last strictly ascending step.
    log_ratio=math.log(speed)+math.log1p(-q)-math.log(fall)-logq
    log_total=(log_ratio+math.log1p(math.exp(-log_ratio)) if log_ratio > 0
               else math.log1p(math.exp(log_ratio)))
    n=max(0,math.ceil(-log_total/logq)-1)
    if q > .99999:
        # Near q=1 the ordinary closed form subtracts two large terms.
        with localcontext() as context:
            context.prec=50
            dq=Decimal.from_float(q)
            ds=Decimal.from_float(speed)
            dg=Decimal.from_float(gravity*SIMULATION_STEP)
            terminal=dq*dg/(1-dq)
            total=(ds-terminal)*dq*(1-dq**n)/(1-dq)+n*terminal
            return max(0.,float(total)*SIMULATION_STEP)
    terminal=-q*fall/(1-q)
    total=(speed-terminal)*q*(-math.expm1(n*logq))/(1-q)+n*terminal
    return max(0.,SIMULATION_STEP*total)


def _safe_scaled_speed(base_speed, scale):
    result=base_speed*scale
    return result if math.isfinite(result) else base_speed


@lru_cache(maxsize=256)
def launch_speed(base_speed, gravity, damping, height_multiplier):
    """Invert the apex; unknown/unbounded gravity uses the energy-law fallback.

    A roof, changing medium, extra forces or a mid-flight Buff change can
    restrict the realized rise. Zero vertical damping permits no jump.
    """
    base_speed=float(base_speed)
    height_multiplier=float(height_multiplier)
    if not math.isfinite(base_speed) or base_speed < 0:
        return 0.
    if not math.isfinite(height_multiplier):
        return base_speed
    if height_multiplier <= 0:
        return 0.
    if height_multiplier == 1 or base_speed == 0:
        return base_speed
    fallback=_safe_scaled_speed(base_speed,math.sqrt(height_multiplier))
    if gravity is None or not math.isfinite(gravity) or not math.isfinite(damping):
        return fallback
    damping=max(0.,min(1.,damping))
    if damping == 0:
        return base_speed
    target=jump_apex(base_speed,gravity,damping)*height_multiplier
    if not math.isfinite(target) or target <= 0:
        return fallback
    low,high=0.,max(1.,base_speed)
    while jump_apex(high,gravity,damping) < target:
        low=high
        high*=2
        if not math.isfinite(high):
            return fallback
    for _ in range(48):
        mid=low+(high-low)/2
        if jump_apex(mid,gravity,damping) < target:
            low=mid
        else:
            high=mid
    return low+(high-low)/2
