"""Keep both self-contained packages on the same creation instructions and assets."""
import argparse
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / 'plugins/castloop-studio-sit'
target = root / 'plugins/castloop-studio'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
files = {
    'assets/icon.png': (source / 'assets/icon.png').read_bytes(),
    'skills/studio-creation/agents/openai.yaml': (source / 'skills/studio-creation/agents/openai.yaml').read_bytes(),
    'skills/studio-creation/SKILL.md': (source / 'skills/studio-creation/SKILL.md').read_text(encoding='utf-8')
        .replace('CastLoop Studio SIT', 'CastLoop Studio')
        .replace('test environment only', 'production environment')
        .encode('utf-8'),
}
for name, content in files.items():
    destination = target / name
    if args.check:
        if not destination.is_file() or destination.read_bytes() != content:
            raise SystemExit(f'Plugin shared file differs: {name}')
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
print('Shared plugin files match' if args.check else 'Shared plugin files synchronized')
