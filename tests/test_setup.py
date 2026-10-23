from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SETUP_PATH = Path(__file__).resolve().parents[1] / 'setup.py'


class SetupVersionTests(unittest.TestCase):
    def assert_package_version(self, declaration, expected):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(SETUP_PATH, root / 'setup.py')
            (root / 'src').mkdir()
            (root / 'src' / '__init__.py').write_text(
                'UNRELATED = "ignored"\n'
                + declaration + '\n'
                + 'raise RuntimeError("Package initialization must not run during version extraction")\n',
                encoding='utf-8',
            )

            result = subprocess.run(
                [sys.executable, 'setup.py', '--version'],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), expected)

    def test_string_version_without_importing_package(self):
        self.assert_package_version('__version__ = "2.4.6"', '2.4.6')

    def test_numeric_tuple_version(self):
        self.assert_package_version('__version_info__ = (2, 4, 6)', '2.4.6')

    def test_mixed_tuple_version(self):
        self.assert_package_version('VERSION = (2, "4", "6rc1")', '2.4.6rc1')


if __name__ == '__main__':
    unittest.main()
