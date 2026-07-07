"""
零文件音乐系统 —— 纯代码合成背景音乐，不依赖任何音频文件。

复用 sfx.py 的波形生成工具，将音乐模式预渲染为 Sound 对象。
使用 Sound.play(loops=-1) 实现无缝循环，Sound.fadeout() 实现淡出过渡。
"""
from __future__ import annotations
import struct, math
import pygame
import sfx

# ---- 音乐专用状态 ----
_music_initialized = False
_current_track: str | None = None     # 当前播放的曲目 key
_current_sound: pygame.mixer.Sound | None = None  # 当前播放的 Sound 对象
_music_volume = 0.5                   # 音乐音量 (0~1)
_music_cache: dict[str, pygame.mixer.Sound] = {}  # 曲目缓存


def _ensure_init():
    """确保混音器和 sfx 已初始化。"""
    global _music_initialized
    if _music_initialized:
        return
    sfx._ensure_init()
    _music_initialized = True


# ===================== 公开 API =====================
def play(track_key: str, fade_in_ms: int = 800, loops: int = -1):
    """
    播放指定曲目（自动缓存、无缝循环、淡入）。
    若已有曲目播放中，先淡出旧曲目。
    """
    global _current_track, _current_sound

    _ensure_init()

    sound = _music_cache.get(track_key)
    if sound is None:
        return  # 曲目尚未渲染（需先调用 register + render）

    # 淡出旧曲目
    if _current_sound is not None and _current_sound is not sound:
        try:
            _current_sound.fadeout(300)
        except pygame.error:
            pass

    # 播放新曲目（Sound.set_volume 影响该 Sound 的所有实例）
    sound.set_volume(_music_volume)
    try:
        sound.play(loops=loops, fade_ms=fade_in_ms)
    except pygame.error:
        pass

    _current_sound = sound
    _current_track = track_key


def stop(fade_out_ms: int = 500):
    """停止当前音乐，可选淡出。"""
    global _current_track, _current_sound
    if _current_sound is not None:
        try:
            if fade_out_ms > 0:
                _current_sound.fadeout(fade_out_ms)
            else:
                _current_sound.stop()
        except pygame.error:
            pass
    _current_sound = None
    _current_track = None


def set_volume(v: float):
    """设置音乐音量 (0~1)，同时更新 sfx 侧以保持设置页同步。"""
    global _music_volume
    _music_volume = max(0.0, min(1.0, v))
    sfx.set_music_volume(_music_volume)
    # 更新当前播放中 Sound 的音量
    if _current_sound is not None:
        try:
            _current_sound.set_volume(_music_volume)
        except pygame.error:
            pass


def get_volume() -> float:
    return _music_volume


def is_playing() -> bool:
    """检查是否有音乐正在播放。"""
    if _current_sound is None:
        return False
    try:
        return _current_sound.get_num_channels() > 0
    except pygame.error:
        return False


def get_current_track() -> str | None:
    return _current_track


def register(key: str, sound: pygame.mixer.Sound):
    """注册一个已渲染的曲目到缓存。"""
    _music_cache[key] = sound


def invalidate_cache():
    """清空音乐缓存。"""
    global _music_cache
    _music_cache.clear()


# ===================== 音符频率表（科学音高记谱法） =====================
# 从 C2 (65.41 Hz) 到 C7 (2093.00 Hz)，覆盖 5 个八度
_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

NOTE_FREQ: dict[str, float] = {}

def _build_note_table():
    """构建音符→频率映射表。A4 = 440 Hz。"""
    for octave in range(2, 8):
        for j, name in enumerate(_NOTE_NAMES):
            # 半音编号：A4 = 440Hz，A4 = 第 4 个八度的第 9 个半音 = (4*12+9) = 57
            semitone = (octave - 4) * 12 + (j - 9)  # relative to A4
            freq = 440.0 * (2 ** (semitone / 12.0))
            key = f"{name}{octave}"
            NOTE_FREQ[key] = round(freq, 2)

_build_note_table()


# ---- 便捷别名 ----
RATE = sfx.RATE
MAX_AMP = sfx.MAX_AMP


# ===================== 音符渲染工具（复用 sfx 波形） =====================
def _freq(note: str) -> float:
    """获取音符频率，支持音名（如 'C4'）或直接 Hz 数值字符串（如 '440'）。"""
    try:
        return float(note)
    except ValueError:
        return NOTE_FREQ.get(note, 440.0)


def _render_note(freq: float, duration_sec: float,
                 wave: str = "sine", vol: float = 0.3,
                 attack: float = 0.01, release: float = 0.05) -> pygame.mixer.Sound:
    """渲染单个音符为 Sound 对象。"""
    n = int(RATE * duration_sec)
    buf = bytearray()
    attack_samples = int(RATE * attack)
    release_samples = int(RATE * release)
    for i in range(n):
        t = i / RATE
        # 包络
        if i < attack_samples:
            env = i / max(1, attack_samples)
        elif i > n - release_samples:
            env = max(0.0, (n - i) / max(1, release_samples))
        else:
            env = 1.0
        # 波形
        if wave == "square":
            raw = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        elif wave == "triangle":
            raw = 2.0 * abs(2.0 * (freq * t - math.floor(freq * t + 0.5))) - 1.0
        elif wave == "noise":
            raw = sfx._noise_sample(i + int(freq * 1000))
        else:
            raw = math.sin(2 * math.pi * freq * t)
        v = int(MAX_AMP * vol * env * raw)
        buf.extend(struct.pack('<h', max(-32768, min(32767, v))))
    return sfx._make(buf, RATE)


# ===================== 音乐模式数据结构 =====================
class MusicPattern:
    """一段音乐的模式定义（纯数据，无音频）。"""
    __slots__ = ("tempo_bpm", "total_beats", "tracks")
    def __init__(self, tempo_bpm: float, total_beats: float, tracks: list):
        self.tempo_bpm = tempo_bpm        # 每分钟节拍数
        self.total_beats = total_beats    # 总节拍数（决定循环长度）
        self.tracks = tracks              # list[list[MusicEvent]]
        # 每个 track 是 MusicEvent 列表
        # MusicEvent = (beat_offset, note, duration_beats, wave, velocity)

    @property
    def duration_sec(self) -> float:
        """整个循环的时长（秒）。"""
        return self.total_beats * 60.0 / self.tempo_bpm


# ===================== 模式 → 音频预渲染引擎 =====================
def _render_track_to_buffer(track: list, tempo_bpm: float, total_beats: float,
                            master_vol: float = 0.3) -> bytearray | None:
    """
    将单条轨道渲染为 PCM 字节缓冲区。
    轨道元素格式：(beat_offset, note, duration_beats, wave, velocity)
      - note: 音名字符串 "C4" 或休止符 "R"
      - velocity: 0~1 力度
    """
    if not track:
        return None

    duration_sec = total_beats * 60.0 / tempo_bpm
    total_samples = int(RATE * duration_sec)
    if total_samples <= 0:
        return None

    # 16-bit mono PCM 混合缓冲区（int 类型，累加后钳位）
    mix = [0] * total_samples

    beat_dur = 60.0 / tempo_bpm  # 每拍秒数

    for evt in track:
        beat_offset = evt[0]
        note = evt[1]
        duration_beats = evt[2]
        wave = evt[3] if len(evt) > 3 else "sine"
        velocity = evt[4] if len(evt) > 4 else 0.7

        if note == "R" or note == "":
            continue  # 休止符

        freq = _freq(note)
        note_dur = duration_beats * beat_dur
        start_sample = int(beat_offset * beat_dur * RATE)
        note_samples = int(note_dur * RATE)
        end_sample = min(start_sample + note_samples, total_samples)

        if start_sample >= total_samples:
            continue

        attack_samples = int(RATE * 0.008)  # 8ms fast attack
        release_samples = int(RATE * 0.04)  # 40ms release

        for i in range(start_sample, end_sample):
            j = i - start_sample
            t = i / RATE

            # 包络
            if j < attack_samples:
                env = j / max(1, attack_samples)
            elif j > note_samples - release_samples:
                env = max(0.0, (note_samples - j) / max(1, release_samples))
            else:
                env = 1.0

            # 波形
            if wave == "square":
                raw = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
            elif wave == "triangle":
                raw = 2.0 * abs(2.0 * (freq * t - math.floor(freq * t + 0.5))) - 1.0
            elif wave == "noise":
                raw = sfx._noise_sample(i + int(freq * 1000))
            elif wave == "saw":
                raw = 2.0 * (freq * t - math.floor(freq * t + 0.5))
            else:
                raw = math.sin(2 * math.pi * freq * t)

            mix[i] += int(MAX_AMP * master_vol * velocity * env * raw)

    # 钳位到 16-bit 范围
    buf = bytearray()
    for v in mix:
        v = max(-32768, min(32767, v))
        buf.extend(struct.pack('<h', v))
    return buf


def _render_pattern(pattern: MusicPattern, master_vol: float = 0.5) -> pygame.mixer.Sound:
    """
    将 MusicPattern 预渲染为单个可循环 Sound。
    多轨并行混合到单个缓冲区。
    """
    total_samples = int(RATE * pattern.duration_sec)
    if total_samples <= 0:
        return pygame.mixer.Sound(buffer=bytes(0))

    # 多轨累计混合
    mix = [0] * total_samples
    beat_dur = 60.0 / pattern.tempo_bpm

    for track in pattern.tracks:
        for evt in track:
            beat_offset = evt[0]
            note = evt[1]
            duration_beats = evt[2]
            wave = evt[3] if len(evt) > 3 else "sine"
            velocity = evt[4] if len(evt) > 4 else 0.7

            if note == "R" or note == "":
                continue

            freq = _freq(note)
            note_dur = duration_beats * beat_dur
            start_sample = int(beat_offset * beat_dur * RATE)
            note_samples = int(note_dur * RATE)
            end_sample = min(start_sample + note_samples, total_samples)

            if start_sample >= total_samples:
                continue

            attack_samples = int(RATE * 0.008)
            release_samples = int(RATE * min(0.06, note_dur * 0.3))

            for i in range(start_sample, end_sample):
                j = i - start_sample
                t = i / RATE

                if j < attack_samples:
                    env = j / max(1, attack_samples)
                elif j > note_samples - release_samples:
                    env = max(0.0, (note_samples - j) / max(1, release_samples))
                else:
                    env = 1.0

                if wave == "square":
                    raw = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
                elif wave == "triangle":
                    raw = 2.0 * abs(2.0 * (freq * t - math.floor(freq * t + 0.5))) - 1.0
                elif wave == "noise":
                    raw = sfx._noise_sample(i + int(freq * 1000))
                elif wave == "saw":
                    raw = 2.0 * (freq * t - math.floor(freq * t + 0.5))
                else:
                    raw = math.sin(2 * math.pi * freq * t)

                mix[i] += int(MAX_AMP * master_vol * velocity * env * raw)

    # 钳位 + 输出
    buf = bytearray()
    for v in mix:
        v = max(-32768, min(32767, v))
        buf.extend(struct.pack('<h', v))
    return sfx._make(buf, RATE)


def _render_and_register(key: str, pattern: MusicPattern, master_vol: float = 0.5):
    """渲染模式并注册到缓存。"""
    sound = _render_pattern(pattern, master_vol)
    register(key, sound)
    return sound
