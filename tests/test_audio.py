import os
from pathlib import Path
import tempfile
import unittest
import wave

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame


class FileMusicTests(unittest.TestCase):
    def test_file_music_follows_volume_stop_and_synth_switch(self):
        import music
        pygame.init()
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory) / "test.wav"
            with wave.open(str(filename), "wb") as wav:
                wav.setnchannels(2)
                wav.setsampwidth(2)
                wav.setframerate(22050)
                wav.writeframes(b"\0" * 22050 * 4)
            try:
                music.play_file(str(filename), fade_in_ms=0)
                self.assertTrue(music.is_playing())
                music.set_volume(0.25)
                self.assertAlmostEqual(pygame.mixer.music.get_volume(), 0.25)
                music.stop(fade_out_ms=0)
                self.assertFalse(pygame.mixer.music.get_busy())
                music.play_file(str(filename), fade_in_ms=0)
                music.play("home", fade_in_ms=0)
                self.assertFalse(pygame.mixer.music.get_busy())
            finally:
                music.stop(fade_out_ms=0)
                music.invalidate_cache()
                music.set_volume(0.5)


if __name__ == "__main__":
    unittest.main()
