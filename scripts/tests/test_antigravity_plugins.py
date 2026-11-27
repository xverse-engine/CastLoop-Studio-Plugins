"""Antigravity native plugin packages must stay environment-isolated and valid."""
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class AntigravityPluginsTest(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location(
            'antigravity_packages', ROOT / 'scripts/build-antigravity-plugins.py'
        )
        self.builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.builder)

    def test_generates_native_antigravity_packages_per_environment(self):
        files = self.builder.generated_files(ROOT)
        for name in ('castloop-studio', 'castloop-studio-sit'):
            prefix = Path('antigravity') / name
            manifest = json.loads(files[prefix / 'plugin.json'])
            codex = json.loads(
                (ROOT / 'plugins' / name / '.codex-plugin/plugin.json').read_text(encoding='utf-8')
            )
            self.assertEqual(manifest['name'], name)
            self.assertEqual(manifest['version'], codex['version'])
            self.assertEqual(manifest['logo'], 'assets/icon.png')
            self.assertIn('assets/icon.png', [p.relative_to(prefix).as_posix() for p in files if p.parts[:2] == prefix.parts])

            config = json.loads(files[prefix / 'mcp_config.json'])
            expected_url = (
                'https://castloop-sit.xverse.cn/mcp'
                if name.endswith('-sit')
                else 'https://studio.castloop.ai/mcp'
            )
            self.assertEqual(config, {'mcpServers': {name: {'url': expected_url}}})

            skill = files[prefix / 'skills/studio-creation/SKILL.md'].decode('utf-8')
            self.assertIn('Antigravity', skill)
            self.assertIn('readStorySections', skill)
            self.assertIn('Never invent an OAuth URL', skill)
            self.assertIn('Do not proactively list stories', skill)

            readme = files[prefix / 'README.md'].decode('utf-8')
            self.assertIn('**' + codex['version'] + '**', readme)
            self.assertIn(expected_url, readme)
            self.assertIn('mcp_config.json', readme)

        self.assertTrue(all(path.parts[0] == 'antigravity' for path in files))

    def test_archives_are_self_contained(self):
        files = self.builder.generated_files(ROOT)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            for archive_path in self.builder.write_archives(files, output):
                with zipfile.ZipFile(archive_path) as archive:
                    manifest = json.loads(archive.read('plugin.json'))
                    self.assertEqual(
                        archive_path.name,
                        f"{manifest['name']}-antigravity-{manifest['version']}.zip",
                    )
                    names = archive.namelist()
                    self.assertIn('plugin.json', names)
                    self.assertIn('mcp_config.json', names)
                    self.assertIn('assets/icon.png', names)
                    self.assertIn('skills/studio-creation/SKILL.md', names)
                    self.assertIn('LICENSE', names)
                    self.assertNotIn('.codex-plugin/plugin.json', names)
            with self.assertRaises(FileExistsError):
                self.builder.write_archives(files, output)


if __name__ == '__main__':
    unittest.main()
