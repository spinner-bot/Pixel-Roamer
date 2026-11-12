"""Clip oversized opaque chunk scales without allocating their full destination."""
from collections import OrderedDict
import pygame

MAX_AXIS_CACHE_BYTES = 4 * 1024 * 1024
MAX_AXIS_CACHE_ENTRIES = 32
_axis_cache = OrderedDict()
_axis_cache_bytes = 0


def clear_axis_cache():
    global _axis_cache_bytes
    _axis_cache.clear()
    _axis_cache_bytes = 0


def _axis_strip(source_length, destination_length, vertical):
    global _axis_cache_bytes
    key = source_length, destination_length, vertical
    if key in _axis_cache:
        _axis_cache.move_to_end(key)
        return _axis_cache[key]
    # Oversized programmatic zooms use direct integer sampling, not huge strips.
    if destination_length * 4 > MAX_AXIS_CACHE_BYTES:
        return None
    source_size = (1, source_length) if vertical else (source_length, 1)
    destination_size = (1, destination_length) if vertical else (destination_length, 1)
    source = pygame.Surface(source_size, depth=32)
    for i in range(source_length):
        source.set_at((0, i) if vertical else (i, 0), (i & 255, (i >> 8) & 255, (i >> 16) & 255))
    strip = pygame.transform.scale(source, destination_size)
    size = strip.get_pitch() * strip.get_height()
    _axis_cache[key] = strip
    _axis_cache_bytes += size
    while (_axis_cache_bytes > MAX_AXIS_CACHE_BYTES or len(_axis_cache) > MAX_AXIS_CACHE_ENTRIES):
        _, removed = _axis_cache.popitem(last=False)
        _axis_cache_bytes -= removed.get_pitch() * removed.get_height()
    return strip


def _axis_runs(source_length, destination_length, start, end, vertical):
    strip = _axis_strip(source_length, destination_length, vertical)
    runs = []
    previous = None
    for pixel in range(start, end):
        if strip is None:
            index = pixel * source_length // destination_length
        else:
            color = strip.get_at((0, pixel) if vertical else (pixel, 0))
            index = color.r | color.g << 8 | color.b << 16
        if index == previous:
            runs[-1][2] += 1
        else:
            runs.append([index, pixel, 1])
            previous = index
    return runs


def blit_large_chunk(target, source, rectangle):
    """Match pygame's nearest sampling for opaque terrain in the visible clip."""
    visible = rectangle.clip(target.get_clip())
    if not visible:
        return
    x_runs = _axis_runs(source.get_width(), rectangle.w,
                        visible.left - rectangle.left, visible.right - rectangle.left, False)
    y_runs = _axis_runs(source.get_height(), rectangle.h,
                        visible.top - rectangle.top, visible.bottom - rectangle.top, True)
    for sy, dy, height in y_runs:
        previous = None
        left = width = 0
        for sx, dx, span in x_runs:
            color = source.get_at((sx, sy))
            if color == previous:
                width += span
            else:
                if previous is not None:
                    target.fill(previous, (rectangle.left + left, rectangle.top + dy, width, height))
                previous, left, width = color, dx, span
        if previous is not None:
            target.fill(previous, (rectangle.left + left, rectangle.top + dy, width, height))
