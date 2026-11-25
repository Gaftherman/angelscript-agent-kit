"""Validate the kit: manifests, skill frontmatter, relative links and AngelScript samples.

Usage: python -I scripts/validate.py [--compile <path-to-angelscript-cli>]
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "angelscript"
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def check_json() -> None:
    for name in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", ".mcp.json"):
        try:
            json.loads((ROOT / name).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            fail(f"{name}: {exc}")


def check_frontmatter() -> None:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        fail("SKILL.md: missing frontmatter")
        return
    fields = dict(line.split(": ", 1) for line in match.group(1).splitlines() if ": " in line)
    if fields.get("name") != "angelscript":
        fail("SKILL.md: name must be angelscript")
    if not 20 <= len(fields.get("description", "")) <= 1024:
        fail("SKILL.md: description must be 20-1024 characters")


def markdown_files() -> list[Path]:
    return sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts)


def check_links() -> None:
    for path in markdown_files():
        for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", path.read_text(encoding="utf-8")):
            if re.match(r"[a-z]+:", target):
                continue
            if not (path.parent / target).exists():
                fail(f"{path.relative_to(ROOT)}: broken link {target}")


def check_samples(cli: str) -> None:
    for path in markdown_files():
        blocks = re.findall(r"```angelscript\n(.*?)```", path.read_text(encoding="utf-8"), re.S)
        for index, block in enumerate(blocks, 1):
            with tempfile.TemporaryDirectory() as folder:
                script = Path(folder) / "sample.as"
                script.write_text(block + "\nvoid main() {}\n", encoding="utf-8")
                result = subprocess.run([cli, "--check", str(script)], capture_output=True, text=True)
                if result.returncode != 0:
                    fail(f"{path.relative_to(ROOT)} sample {index}: {result.stderr.strip()}")


def main() -> int:
    check_json()
    check_frontmatter()
    check_links()
    if "--compile" in sys.argv:
        check_samples(sys.argv[sys.argv.index("--compile") + 1])
    for message in errors:
        print(f"error: {message}", file=sys.stderr)
    print("ok" if not errors else f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
