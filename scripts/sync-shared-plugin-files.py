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
game = Path('skills/castloop-mini-game-ui')
for path in sorted((source / game).rglob('*')):
    if not path.is_file() or path.suffix not in {'.md', '.ts', '.json', '.mjs', '.py'}:
        continue
    content = path.read_bytes()
    if path == source / game / 'SKILL.md':
        guide = path.read_text(encoding='utf-8').replace('CastLoop Studio SIT', 'CastLoop Studio')
        guide = guide.replace('SIT storyId', '正式环境 storyId').replace('当前 SIT 连接', '当前正式环境连接')
        content = guide.encode('utf-8')
    files[path.relative_to(source)] = content

for name, content in files.items():
    destination = target / name
    if args.check:
        if not destination.is_file() or destination.read_bytes() != content:
            raise SystemExit(f'Plugin shared file differs: {name}')
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
print('Shared plugin files match' if args.check else 'Shared plugin files synchronized')
