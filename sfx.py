"""
零文件音效系统 —— 纯代码合成波形，不依赖任何音频文件。
"""
from __future__ import annotations
import struct, math
import pygame

_initialized = False
_sfx_volume = 0.8      # 音效音量 (0~1)
_music_volume = 0.5    # 音乐音量 (0~1) — 预留
_cache: dict = {}       # 缓存已生成的 Sound

RATE = 22050
MAX_AMP = 32767


def init():
    """初始化混音器。"""
    global _initialized
    if not _initialized:
        try:
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            pygame.mixer.init(frequency=RATE, size=-16, channels=1, buffer=512)
            _initialized = True
        except pygame.error:
            # 音频设备不可用，静默失败
            _initialized = True  # 避免反复重试


def set_sfx_volume(v: float):
    global _sfx_volume
    _sfx_volume = max(0.0, min(1.0, v))


def set_music_volume(v: float):
    global _music_volume
    _music_volume = max(0.0, min(1.0, v))


def get_sfx_volume() -> float:
    return _sfx_volume


def get_music_volume() -> float:
    return _music_volume


# ===================== 波形生成工具 =====================
def _gen(buf: bytearray, t: float, vol: float, freq: float):
    """向buf写入t时刻、指定频率的16位PCM采样。"""
    v = int(MAX_AMP * vol * math.sin(2 * math.pi * freq * t))
    buf.extend(struct.pack('<h', max(-32768, min(32767, v))))


def _make(buf: bytearray, rate: int) -> pygame.mixer.Sound:
    return pygame.mixer.Sound(buffer=bytes(buf))


def _slide_sound(freq_start: float, freq_end: float, duration: float,
                  vol: float = 0.35, wave: str = "sine") -> pygame.mixer.Sound:
    """频率滑音（正弦/方波/三角波可选）。"""
    n = int(RATE * duration)
    buf = bytearray()
    for i in range(n):
        t = i / RATE
        progress = i / max(1, n - 1)
        freq = freq_start + (freq_end - freq_start) * progress
        env = _envelope(i, n)
        if wave == "square":
            raw = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        elif wave == "triangle":
            raw = 2.0 * abs(2.0 * (freq * t - math.floor(freq * t + 0.5))) - 1.0
        elif wave == "noise":
            raw = (hash((int(t * RATE), freq_start)) % 2000 - 1000) / 1000.0
        else:
            raw = math.sin(2 * math.pi * freq * t)
        v = int(MAX_AMP * vol * env * raw)
        buf.extend(struct.pack('<h', max(-32768, min(32767, v))))
    return _make(buf, RATE)


def _pop_sound(freq: float, duration: float = 0.06, vol: float = 0.3) -> pygame.mixer.Sound:
    """短促单音（带快速衰减）。"""
    n = int(RATE * duration)
    buf = bytearray()
    for i in range(n):
        t = i / RATE
        env = max(0, 1.0 - i / max(1, n - 1)) ** 1.5
        v = int(MAX_AMP * vol * env * math.sin(2 * math.pi * freq * t))
        buf.extend(struct.pack('<h', max(-32768, min(32767, v))))
    return _make(buf, RATE)


def _envelope(i: int, n: int) -> float:
    """ADSR简易包络：快起→保持→衰减。"""
    attack = int(RATE * 0.005)
    release = int(RATE * 0.03)
    if i < attack:
        return i / attack
    elif i > n - release:
        return max(0, (n - i) / release)
    return 1.0


# ===================== 音效缓存工厂 =====================
def _cached(key: str, factory) -> pygame.mixer.Sound:
    if key not in _cache:
        _cache[key] = factory()
    return _cache[key]


# ===================== 游戏音效 =====================
def play_jump():
    """跳跃：短上升滑音。"""
    init()
    s = _cached("jump", lambda: _slide_sound(250, 650, 0.10, 0.18))
    s.set_volume(_sfx_volume * 0.7)
    s.play()


def play_pickup():
    """拾取积分：双音和弦。"""
    init()
    s = _cached("pickup", lambda: _pop_sound(880, 0.06, 0.25))
    s2 = _cached("pickup2", lambda: _pop_sound(1320, 0.08, 0.2))
    s.set_volume(_sfx_volume)
    s2.set_volume(_sfx_volume * 0.8)
    s.play()
    s2.play()


def play_hurt():
    """受伤：低频脉冲。"""
    init()
    s = _cached("hurt", lambda: _slide_sound(120, 60, 0.15, 0.25, "square"))
    s.set_volume(_sfx_volume)
    s.play()


def play_death():
    """死亡：下降滑音。"""
    init()
    s = _cached("death", lambda: _slide_sound(400, 50, 0.35, 0.30))
    s.set_volume(_sfx_volume)
    s.play()


def play_checkpoint():
    """检查点：三连上行音。"""
    init()
    def _cp():
        n = int(RATE * 0.25)
        buf = bytearray()
        freqs = [523, 659, 784]  # C5 E5 G5
        for j, f in enumerate(freqs):
            start = j * n // 3
            end = (j + 1) * n // 3
            for i in range(start, end):
                t = i / RATE
                env = _envelope(i - start, end - start) * 0.3
                v = int(MAX_AMP * env * math.sin(2 * math.pi * f * t))
                buf.extend(struct.pack('<h', max(-32768, min(32767, v))))
        return _make(buf, RATE)
    s = _cached("checkpoint", _cp)
    s.set_volume(_sfx_volume)
    s.play()


def play_win():
    """通关：四音上行琶音。"""
    init()
    def _win():
        n = int(RATE * 0.5)
        buf = bytearray()
        freqs = [523, 659, 784, 1047]  # C5 E5 G5 C6
        for j, f in enumerate(freqs):
            start = j * n // 4
            end = (j + 1) * n // 4
            for i in range(start, end):
                t = i / RATE
                env = _envelope(i - start, end - start) * 0.3
                v = int(MAX_AMP * env * math.sin(2 * math.pi * f * t))
                buf.extend(struct.pack('<h', max(-32768, min(32767, v))))
        return _make(buf, RATE)
    s = _cached("win", _win)
    s.set_volume(_sfx_volume)
    s.play()


def play_click():
    """UI点击：极短高频。"""
    init()
    s = _cached("click", lambda: _pop_sound(1000, 0.03, 0.12))
    s.set_volume(_sfx_volume * 0.5)
    s.play()
