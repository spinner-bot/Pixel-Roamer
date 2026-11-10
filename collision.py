"""Axis sweeps with one shared tolerance for contact geometry (world units)."""

CONTACT_EPSILON = 1e-8


def spans_overlap(start, size, other_start, other_size):
    """A rounding-sized contact is not overlap on the perpendicular axis."""
    return min(start + size, other_start + other_size) - max(start, other_start) > CONTACT_EPSILON


def sweep_axis(rect, displacement, blocks, horizontal):
    """Move to the nearest crossed face; return whether that face blocked motion.

    Compare each face against the original position. This prevents a floor's
    tiny vertical overlap from becoming a lateral push, and makes the result
    independent of the candidate block iteration order.
    """
    if displacement == 0:
        return False
    position = rect.x if horizontal else rect.y
    size = rect.w if horizontal else rect.h
    allowed = displacement
    blocked = False
    for block, kind in blocks:
        if kind.one_way and (horizontal or displacement > 0):
            continue
        if horizontal:
            if not spans_overlap(rect.y, rect.h, block.y, block.h):
                continue
            block_start, block_size = block.x, block.w
        else:
            if not spans_overlap(rect.x, rect.w, block.x, block.w):
                continue
            block_start, block_size = block.y, block.h
        if displacement > 0:
            gap = block_start - (position + size)
            if -CONTACT_EPSILON <= gap <= allowed + CONTACT_EPSILON:
                allowed = min(allowed, gap)
                blocked = True
        else:
            gap = block_start + block_size - position
            if allowed - CONTACT_EPSILON <= gap <= CONTACT_EPSILON:
                allowed = max(allowed, gap)
                blocked = True
    if horizontal:
        rect.x = position + allowed
    else:
        rect.y = position + allowed
    return blocked
