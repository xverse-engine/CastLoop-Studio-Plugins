"""Copy the public mini-game guide into a Caster server checkout before building it."""
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("server", type=Path, help="XNarratorServer checkout")
parser.add_argument("--check", action="store_true")
args = parser.parse_args()
source = Path(__file__).resolve().parents[1] / "skills/castloop-mini-game-ui/SKILL.md"
target = args.server / "skills/castloop-mini-game-ui/SKILL.md"
if not (args.server / "skills/catalog.go").is_file():
    parser.error("Expected the server checkout containing skills/catalog.go")
if args.check:
    if not target.is_file() or source.read_text(encoding="utf-8") != target.read_text(encoding="utf-8"):
        parser.exit(1, "Caster mini-game guide differs from plugin source\n")
else:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())
