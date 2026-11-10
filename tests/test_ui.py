import os
from pathlib import Path
import subprocess
import sys
import unittest


class ApplicationFlowTests(unittest.TestCase):
    def test_real_main_loop_navigation_and_game_rules(self):
        root = Path(__file__).resolve().parents[1]
        env = {**os.environ, "SDL_VIDEODRIVER": "dummy", "SDL_AUDIODRIVER": "dummy"}
        result = subprocess.run([sys.executable, str(root / "tests/application_scenarios.py")],
                                cwd=root, env=env, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"maps_navigated": 12', result.stdout)


if __name__ == "__main__":
    unittest.main()
