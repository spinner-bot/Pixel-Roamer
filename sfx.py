"""
零文件音效系统 —— 纯代码合成波形，不依赖任何音频文件。
"""
from __future__ import annotations
import struct, math
import pygame

_initialized = False
_mixer_failed = False       # 混音器初始化失败标记
_mixer_retry_time = 0.0     # 下次重试时间（ms，基于 pygame.time.get_ticks）
_mixer_retry_interval = 60_000  # 重试间隔（毫秒）

_sfx_volume = 0.8           # 音效音量 (0~1)
_music_volume = 0.5         # 音乐音量 (0~1)
_muted = False              # 全局静音标记
_cache: dict = {}           # 缓存已生成的 Sound

RATE = 22050
MAX_AMP = 32767

# ---- 各音效基准音量（与 _sfx_volume 相乘得到最终音量） ----
_BASE_VOLUMES = {
    "jump":       0.38,
    "pickup":     0.25,
    "pickup2":    0.20,
    "hurt":       0.25,
    "death":      0.30,
    "checkpoint": 0.30,
    "win":        0.30,
    "click":      0.06,
}

# ---- 优先级（数值越小越重要） ----
class Priority:
    CRITICAL = 0   # death, win —— 不可抢占
    GAMEPLAY = 1   # jump, hurt, pickup, checkpoint
    UI = 2         # click

# ---- 声道分配（按优先级区间预留） ----
#  区间映射：Priority -> (start_ch, end_ch)  [start_ch, end_ch)
_CHANNEL_TIERS = {
    Priority.CRITICAL: (0, 1),    # 1 个关键声道
    Priority.GAMEPLAY:  (1, 4),   # 3 个玩法声道
    Priority.UI:        (4, 8),   # 4 个 UI 声道
}
_channels: list = []              # [pygame.mixer.Channel or None, ...]


def _ensure_init():
    """惰性初始化混音器 + 声道分配（幂等）。"""
    global _initialized, _mixer_failed, _mixer_retry_time, _channels
    if _mixer_failed:
        now = pygame.time.get_ticks()
        if now < _mixer_retry_time:
            return
        _mixer_failed = False

    if _initialized:
        return

    try:
        current = pygame.mixer.get_init()
        if current is None:
            pygame.mixer.init(frequency=RATE, size=-16, channels=1, buffer=512)
        elif current == (RATE, -16, 1):
            pass
        else:
            pygame.mixer.quit()
            pygame.mixer.init(frequency=RATE, size=-16, channels=1, buffer=512)

        # 分配专用声道
        num_ch = pygame.mixer.get_num_channels()  # 默认 8
        _channels = [None] * num_ch
        for i in range(num_ch):
            _channels[i] = pygame.mixer.Channel(i)

        _initialized = True
    except pygame.error:
        _initialized = True
        _mixer_failed = True
        _mixer_retry_time = pygame.time.get_ticks() + _mixer_retry_interval


def init():
    """公开初始化入口（兼容旧接口），内部幂等。"""
    _ensure_init()


# ===================== 音量 & 静音 =====================
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


def set_mute(on: bool):
    """设置全局静音。"""
    global _muted
    _muted = on


def toggle_mute():
    """切换全局静音状态，返回切换后的状态。"""
    global _muted
    _muted = not _muted
    return _muted


def is_muted() -> bool:
    """返回当前是否静音。"""
    return _muted


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
            raw = _noise_sample(i + int(freq_start * 1000))
        else:
            raw = math.sin(2 * math.pi * freq * t)
        v = int(MAX_AMP * vol * env * raw)
        buf.extend(struct.pack('<h', max(-32768, min(32767, v))))
    return _make(buf, RATE)


def _pop_sound(freq: float, duration: float = 0.06, vol: float = 0.3) -> pygame.mixer.Sound:
    """短促单音（带快速衰减 + 1ms 淡入防噼啪声）。"""
    n = int(RATE * duration)
    buf = bytearray()
    fade_in_samples = int(RATE * 0.001)  # 1ms 淡入
    for i in range(n):
        t = i / RATE
        attack = min(1.0, i / max(1, fade_in_samples)) if fade_in_samples > 0 else 1.0
        decay = max(0, 1.0 - i / max(1, n - 1)) ** 1.5
        env = attack * decay
        v = int(MAX_AMP * vol * env * math.sin(2 * math.pi * freq * t))
        buf.extend(struct.pack('<h', max(-32768, min(32767, v))))
    return _make(buf, RATE)


# ---- 确定性噪声生成器（LCG，替代 hash()） ----
_NOISE_SEED = 42


def _noise_sample(step: int) -> float:
    """确定性 PRNG 噪声采样，返回 [-1, 1]。"""
    global _NOISE_SEED
    s = (_NOISE_SEED + step * 2654435761) & 0xFFFFFFFF
    s = (s ^ (s >> 13)) & 0xFFFFFFFF
    s = (s * 1103515245 + 12345) & 0x7FFFFFFF
    return (s / 0x7FFFFFFF) * 2.0 - 1.0


def _envelope(i: int, n: int) -> float:
    """ADSR简易包络：快起→保持→衰减→1ms淡出防噼啪声。"""
    attack = int(RATE * 0.005)
    release = int(RATE * 0.03)
    fade_out = int(RATE * 0.001)
    if i < attack:
        return i / attack
    elif i > n - release:
        r = max(0, (n - i) / release)
        if i > n - fade_out:
            r *= (n - i) / fade_out
        return r
    return 1.0


# ===================== 音效缓存工厂 =====================
def _cached(key: str, factory) -> pygame.mixer.Sound:
    if key not in _cache:
        _cache[key] = factory()
    return _cache[key]


def invalidate_cache():
    """清空音效缓存（切换音频设备后使用）。"""
    global _cache
    _cache.clear()


# ===================== 音效池化（防止瞬间大量播放导致爆音） =====================
# 每个优先级的最大并发数（基于声道区间大小）
_MAX_CONCURRENT = {
    Priority.CRITICAL: 2,   # 关键音效最多 2 个同时
    Priority.GAMEPLAY:  3,  # 玩法音效最多 3 个同时
    Priority.UI:        2,  # UI 音效最多 2 个同时
}
# 每个优先级的播放时间戳队列（ms，基于 pygame.time.get_ticks）
_play_timestamps: dict[int, list[int]] = {
    Priority.CRITICAL: [],
    Priority.GAMEPLAY:  [],
    Priority.UI:        [],
}
# 各优先级时间窗口（ms）：超过此时间的记录视为过期
_POOL_WINDOW_MS = {
    Priority.CRITICAL: 800,   # death/win 持续时间较长
    Priority.GAMEPLAY:  400,  # jump/hurt/pickup/checkpoint
    Priority.UI:        100,  # click 极短
}
# 错误抑制：每种错误类型只记录一次（避免刷屏）
_error_once: set[str] = set()


def _check_pool(priority: int) -> bool:
    """检查音效池是否允许播放。清理过期记录后，若未达上限则记录并返回 True。"""
    now = pygame.time.get_ticks()
    window = _POOL_WINDOW_MS.get(priority, 300)
    cap = _MAX_CONCURRENT.get(priority, 3)
    stamps = _play_timestamps.get(priority)
    if stamps is None:
        return True  # 未知优先级，允许通过

    # 清理过期
    cutoff = now - window
    while stamps and stamps[0] < cutoff:
        stamps.pop(0)

    if len(stamps) >= cap:
        return False  # 池满，丢弃

    stamps.append(now)
    return True


# ===================== 声道管理 + 播放 =====================
def _acquire_channel(priority: int) -> pygame.mixer.Channel | None:
    """在指定优先级区间内找一个空闲声道。CRITICAL 可抢占，其他优先级不抢占（由池化控制并发）。"""
    if not _channels:
        return None
    start, end = _CHANNEL_TIERS.get(priority, (0, len(_channels)))
    end = min(end, len(_channels))
    start = max(0, min(start, end - 1))

    # 1) 优先找空闲声道
    for i in range(start, end):
        ch = _channels[i]
        if ch is not None and not ch.get_busy():
            return ch

    # 2) CRITICAL：可以抢占 GAMEPLAY 区间
    if priority == Priority.CRITICAL:
        gs, ge = _CHANNEL_TIERS[Priority.GAMEPLAY]
        for i in range(gs, min(ge, len(_channels))):
            ch = _channels[i]
            if ch is not None:
                ch.stop()
                return ch
        # 最后手段：任意可用声道
        for ch in _channels:
            if ch is not None:
                return ch
        return None

    # 3) GAMEPLAY / UI：不抢占，由 _check_pool 控制已有上限
    return None


def _play_sfx_at(sound: pygame.mixer.Sound, volume: float, priority: int):
    """通过声道管理播放一个音效，含池化限制和错误恢复。"""
    if _muted or _mixer_failed:
        return
    _ensure_init()

    # 池化检查：同一优先级并发过多则丢弃（CRITICAL 始终放行）
    if priority != Priority.CRITICAL and not _check_pool(priority):
        return

    ch = _acquire_channel(priority)
    if ch is None:
        return
    try:
        ch.set_volume(volume)
        ch.play(sound)
    except pygame.error as e:
        # 记录一次错误类型，抑制重复日志
        err_key = str(e)[:80]
        if err_key not in _error_once:
            _error_once.add(err_key)
            # 静默降级，不打印到 stdout；调试时可取消注释：
            # print(f"[sfx] play error: {e}")
    except Exception:
        pass  # 防御性兜底


def _play_sfx(sound: pygame.mixer.Sound, volume: float, priority: int):
    """便捷封装（兼容 _play_sfx 旧签名 + 新增 priority）。"""
    _play_sfx_at(sound, volume, priority)


# ===================== 游戏音效 =====================
def play_jump():
    """跳跃：短上升滑音。"""
    s = _cached("jump", lambda: _slide_sound(250, 650, 0.10, 0.18))
    _play_sfx(s, _sfx_volume * _BASE_VOLUMES["jump"], Priority.GAMEPLAY)


def play_pickup():
    """拾取积分：双音和弦。"""
    s = _cached("pickup", lambda: _pop_sound(880, 0.06, 0.25))
    s2 = _cached("pickup2", lambda: _pop_sound(1320, 0.08, 0.2))
    _play_sfx(s, _sfx_volume * _BASE_VOLUMES["pickup"], Priority.GAMEPLAY)
    _play_sfx(s2, _sfx_volume * _BASE_VOLUMES["pickup2"], Priority.GAMEPLAY)


def play_hurt():
    """受伤：低频脉冲。"""
    s = _cached("hurt", lambda: _slide_sound(120, 60, 0.15, 0.25, "square"))
    _play_sfx(s, _sfx_volume * _BASE_VOLUMES["hurt"], Priority.GAMEPLAY)


def play_death():
    """死亡：下降滑音。"""
    s = _cached("death", lambda: _slide_sound(400, 50, 0.35, 0.30))
    _play_sfx(s, _sfx_volume * _BASE_VOLUMES["death"], Priority.CRITICAL)


def play_checkpoint():
    """检查点：三连上行音。"""
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
    _play_sfx(s, _sfx_volume * _BASE_VOLUMES["checkpoint"], Priority.GAMEPLAY)


def play_win():
    """通关：四音上行琶音。"""
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
    _play_sfx(s, _sfx_volume * _BASE_VOLUMES["win"], Priority.CRITICAL)


def play_click():
    """UI点击：极短高频。"""
    s = _cached("click", lambda: _pop_sound(1000, 0.03, 0.12))
    _play_sfx(s, _sfx_volume * _BASE_VOLUMES["click"], Priority.UI)
