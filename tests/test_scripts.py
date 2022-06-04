import unittest
from pathlib import Path

from src.main import run_file


CURRENT_DIR = Path(__file__).parent
SCRIPT_DIR = CURRENT_DIR / 'scripts'

class TestScripts(unittest.TestCase):

    def setUp(self):
        self.scripts = SCRIPT_DIR.glob('*.lox')

    def test_script(self):
        for script in self.scripts:
            with self.subTest(script=script):
                run_file(script)

if __name__ == '__main__':
    unittest.main()
