"""Guard the staged Codex OAuth migration and environment isolation."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def server(name):
    return json.loads((ROOT / 'plugins' / name / '.mcp.json').read_text(encoding='utf-8'))['mcpServers'][name]


class CodexDcrTest(unittest.TestCase):
    def test_sit_uses_discovery_registration_without_fixed_client_or_callback(self):
        self.assertEqual(server('castloop-studio-sit'), {
            'type': 'http',
            'url': 'https://castloop-sit.xverse.cn/mcp',
            'scopes': ['openid', 'studio:read', 'studio:write', 'offline_access'],
        })

    def test_production_keeps_the_existing_pre_registered_client(self):
        production = server('castloop-studio')
        self.assertEqual(production['url'], 'https://studio.castloop.ai/mcp')
        self.assertEqual(production['oauth'], {
            'clientId': 'zl6mpa97xs5zdjt3by7pr',
            'callbackUrl': 'http://127.0.0.1/callback',
        })


if __name__ == '__main__':
    unittest.main()
