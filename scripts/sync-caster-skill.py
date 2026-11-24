"""Copy the public mini-game guide into a Caster server checkout before building it."""
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("server", type=Path, help="XNarratorServer checkout")
parser.add_argument("--check", action="store_true")
args = parser.parse_args()
source = Path(__file__).resolve().parents[1] / "skills/castloop-mini-game-ui"
target = args.server / "skills/castloop-mini-game-ui"
if not (args.server / "skills/catalog.go").is_file():
    parser.error("Expected the server checkout containing skills/catalog.go")
for entry in [source / "SKILL.md", *sorted((source / "references/common").glob("*.md"))]:
    dest = target / entry.relative_to(source)
    if args.check:
        if not dest.is_file() or entry.read_text(encoding="utf-8") != dest.read_text(encoding="utf-8"):
            parser.exit(1, f"Caster guide differs: {dest}\n")
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(entry.read_bytes())
