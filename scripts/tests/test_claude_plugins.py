"""Claude packages must be portable across chat, Cowork and Code."""
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ClaudePluginsTest(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('claude_packages', ROOT / 'scripts/build-claude-plugins.py')
        self.builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.builder)

    def test_separates_claude_packages_from_existing_codex_configuration(self):
        files = self.builder.generated_files(ROOT)
        marketplace = json.loads(files[Path('.claude-plugin/marketplace.json')])
        self.assertEqual(marketplace['name'], 'castloop-studio-development')
        for entry in marketplace['plugins']:
            name = entry['name']
            prefix = Path('claude') / name
            self.assertEqual(entry['source'], './' + prefix.as_posix())
            config = json.loads(files[prefix / '.mcp.json'])
            expected_url = ('https://castloop-sit.xverse.cn/mcp' if name.endswith('-sit')
                            else 'https://studio.castloop.ai/mcp')
            self.assertEqual(config, {'mcpServers': {name: {'type': 'http', 'url': expected_url}}})
            manifest = json.loads(files[prefix / '.claude-plugin/plugin.json'])
            self.assertEqual(manifest['name'], name)
            codex = json.loads((ROOT / 'plugins' / name / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
            self.assertEqual(manifest['version'], codex['version'])
            self.assertNotIn('mcpServers', manifest)  # Uses the default .mcp.json on every surface.
            skill = files[prefix / 'skills/studio-creation/SKILL.md'].decode()
            self.assertIn('Do not proactively list stories', skill)
            self.assertIn('Do not modify stories or submit paid tasks during onboarding', skill)
            self.assertIn('readStorySections', skill)
            self.assertIn('Connectors', skill)
            self.assertIn('never invent an OAuth URL', skill)
            self.assertIn('+ > Add plugins', skill)
            readme = files[prefix / 'README.md'].decode()
            self.assertIn('**' + codex['version'] + '**', readme)
            self.assertIn('+ → Add plugins', readme)
            self.assertIn('Browse plugins', readme)
            self.assertIn('CLI', readme)
        self.assertTrue(all(path.parts[0] in {'claude', '.claude-plugin'} for path in files))

    def test_archives_are_self_contained_and_exclude_private_and_other_host_files(self):
        files = self.builder.generated_files(ROOT)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            for archive_path in self.builder.write_archives(files, output):
                with zipfile.ZipFile(archive_path) as archive:
                    manifest = json.loads(archive.read('.claude-plugin/plugin.json'))
                    self.assertEqual(archive_path.name, manifest['name'] + '-claude-' + manifest['version'] + '.zip')
                    names = archive.namelist()
                    self.assertIn('.claude-plugin/plugin.json', names)
                    self.assertIn('.mcp.json', names)
                    self.assertIn('skills/studio-creation/SKILL.md', names)
                    self.assertIn('LICENSE', names)
                    self.assertNotIn('.codex-plugin/plugin.json', names)
                    self.assertNotIn('mcp.claude.json', names)
                    self.assertFalse(any(name.startswith(('docs/', 'scripts/', 'plugins/')) for name in names))
            with self.assertRaises(FileExistsError):
                self.builder.write_archives(files, output)


if __name__ == '__main__':
    unittest.main()
