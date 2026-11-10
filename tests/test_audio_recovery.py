"""PCM format and real mixer failure/recovery regressions."""
import os
from pathlib import Path
import struct
import subprocess
import sys
import unittest
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import pygame
import sfx
import music


class AudioRecoveryTests(unittest.TestCase):
    def setUp(self):
        pygame.mixer.quit()
        sfx._mixer_failed = False
        sfx._initialized = False
        sfx.set_mute(False)
        music.invalidate_cache()

    def test_mono_synthesis_preserves_duration_pitch_and_identical_channels(self):
        sound = music._render_note(440, 1.0)
        self.assertAlmostEqual(sound.get_length(), 1, places=5)
        samples = struct.unpack('<' + 'h' * (len(sound.get_raw()) // 2), sound.get_raw())
        left, right = samples[0::2], samples[1::2]
        self.assertEqual(left, right)
        rising = sum(a <= 0 < b for a, b in zip(left, left[1:]))
        self.assertLessEqual(abs(rising - 440), 1)
        renderer = music._render_pattern_steps(music.MusicPattern(120, 2, []))
        while True:
            try:
                next(renderer)
            except StopIteration as result:
                self.assertAlmostEqual(result.value.get_length(), 1, places=5)
                break

    def test_failed_mixer_retries_after_backoff_and_after_external_recovery(self):
        with patch('pygame.mixer.init', side_effect=pygame.error('unavailable')) as init:
            self.assertFalse(sfx._ensure_init())
            sfx.play_jump()
            self.assertEqual(init.call_count, 1)
        with patch('pygame.time.get_ticks', return_value=sfx._mixer_retry_time):
            self.assertTrue(sfx._ensure_init())
        sfx.play_jump()
        self.assertIn('jump', sfx._cache)
        pygame.mixer.quit()
        with patch('pygame.mixer.init', side_effect=pygame.error('lost')):
            self.assertFalse(sfx._ensure_init())
        pygame.mixer.init(frequency=sfx.RATE, size=-16, channels=2)
        self.assertTrue(sfx._ensure_init())
        self.assertFalse(sfx._mixer_failed)
        sfx.play_click()

    def test_no_audio_device_survives_every_public_sound_and_music_call(self):
        env = {**os.environ, 'SDL_VIDEODRIVER': 'dummy', 'SDL_AUDIODRIVER': 'not_available'}
        code = '''import pygame,sfx,music
pygame.init()
for _ in range(3):
 for name in ('jump','pickup','hurt','death','checkpoint','win','click'):
  getattr(sfx,'play_'+name)()
 music.play('home');music.update();music.set_volume(.5);music.stop()
assert pygame.mixer.get_init() is None
assert not sfx._cache
assert not music._pending_tracks
'''
        result = subprocess.run([sys.executable, '-c', code], env=env,
                                cwd=Path(__file__).resolve().parents[1],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_critical_effects_cannot_steal_music_and_repeated_play_does_not_stack(self):
        self.assertTrue(sfx._ensure_init())
        sfx.play_death()
        first = music._render_note(220, 1)
        second = music._render_note(330, 1)
        music._music_cache.update(probe=first, other=second)
        try:
            music.play('probe', fade_in_ms=0)
            channel_id = music._current_channel_id
            self.assertIn(channel_id, sfx.MUSIC_CHANNEL_IDS)
            sfx.play_death()
            self.assertEqual(first.get_num_channels(), 1)
            for _ in range(4):
                music.play('probe', fade_in_ms=0)
            self.assertEqual(first.get_num_channels(), 1)
            music.play('other', fade_in_ms=0)
            self.assertNotEqual(channel_id, music._current_channel_id)
            self.assertIs(pygame.mixer.Channel(music._current_channel_id).get_sound(), second)
            sfx.play_win()
            self.assertEqual(second.get_num_channels(), 1)
        finally:
            music.stop(0)
