"""Validate the kit: manifests, skill frontmatter, tool names, relative links and AngelScript samples.

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

# The tools angelscript-mcp registers. Docs may only name these.
TOOLS = {
    "angelscript_project_info",
    "angelscript_check",
    "angelscript_host_api",
    "angelscript_find_symbol",
    "angelscript_find_references",
    "angelscript_file_outline",
    "angelscript_describe_symbol",
    "angelscript_rename_symbol",
}
# Names of the retired tools of `angel_lsp --mcp`. They must not come back.
RETIRED = ("workspace_info", "engine_rules", "module_graph", "predefined_lookup", "document_symbols", "open_document", "apply_edit", "replace_document", "angel-lsp")
MCP_ARGS = ["-y", "@angelscript-tools/mcp"]
MANIFESTS = (
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".codex-plugin/plugin.json",
    "gemini-extension.json",
    ".mcp.json",
)
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def load(name: str) -> dict:
    try:
        return json.loads((ROOT / name).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        fail(f"{name}: {exc}")
        return {}


def check_manifests() -> None:
    data = {name: load(name) for name in MANIFESTS}
    versions = {
        name: data[name].get("version")
        for name in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json", "gemini-extension.json")
    }
    if len(set(versions.values())) != 1:
        fail(f"plugin versions differ: {versions}")
    servers = {
        ".mcp.json": data[".mcp.json"].get("mcpServers", {}).get("angelscript", {}),
        "gemini-extension.json": data["gemini-extension.json"].get("mcpServers", {}).get("angelscript", {}),
    }
    for name, server in servers.items():
        if server.get("command") != "npx" or server.get("args") != MCP_ARGS:
            fail(f"{name}: the angelscript MCP server must run `npx {' '.join(MCP_ARGS)}`")
    for name in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
        if data[name].get("mcpServers") != "./.mcp.json":
            fail(f"{name}: mcpServers must point to ./.mcp.json")
    if data[".codex-plugin/plugin.json"].get("skills") != "./skills/":
        fail(".codex-plugin/plugin.json: skills must be ./skills/")
    if not (ROOT / data["gemini-extension.json"].get("contextFileName", "missing")).exists():
        fail("gemini-extension.json: contextFileName does not exist")


def check_frontmatter() -> None:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        fail("SKILL.md: missing frontmatter")
        return
    fields = dict(line.split(": ", 1) for line in match.group(1).splitlines() if ": " in line)
    name = fields.get("name", "")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64 or "claude" in name or "anthropic" in name:
        fail("SKILL.md: name must be 1-64 lowercase letters, digits and hyphens")
    if name != SKILL.name:
        fail("SKILL.md: name must match the folder name")
    description = fields.get("description", "")
    if not 20 <= len(description) <= 1024:
        fail("SKILL.md: description must be 20-1024 characters")
    if re.search(r"\b(I|you)\b", description):
        fail("SKILL.md: write the description in the third person")
    if len(fields.get("compatibility", "")) > 500:
        fail("SKILL.md: compatibility is limited to 500 characters")
    if text.count("\n") > 500:
        fail("SKILL.md: keep the body under 500 lines")


def markdown_files() -> list[Path]:
    return sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts)


def check_tool_names() -> None:
    for path in markdown_files():
        if path.name == "CHANGELOG.md":
            continue
        text = path.read_text(encoding="utf-8")
        for name in set(re.findall(r"\bangelscript_[a-z_]+\b", text)) - TOOLS:
            fail(f"{path.relative_to(ROOT)}: unknown tool {name}")
        for name in RETIRED:
            if re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", text):
                fail(f"{path.relative_to(ROOT)}: retired name {name}")


def check_links() -> None:
    for path in markdown_files():
        for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", path.read_text(encoding="utf-8")):
            if re.match(r"[a-z]+:", target):
                continue
            if not (path.parent / target).exists():
                fail(f"{path.relative_to(ROOT)}: broken link {target}")


def check_scenarios() -> None:
    try:
        scenarios = json.loads((ROOT / "evals" / "scenarios.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        fail(f"evals/scenarios.json: {exc}")
        return
    ids = [s.get("id") for s in scenarios]
    if len(ids) < 3 or len(set(ids)) != len(ids):
        fail("evals/scenarios.json: need at least three scenarios with unique ids")
    for scenario in scenarios:
        for tool in scenario.get("expect", {}).get("tools_used", []):
            if tool not in TOOLS:
                fail(f"evals/scenarios.json: unknown tool {tool}")


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
    check_manifests()
    check_frontmatter()
    check_tool_names()
    check_links()
    check_scenarios()
    if "--compile" in sys.argv:
        check_samples(sys.argv[sys.argv.index("--compile") + 1])
    for message in errors:
        print(f"error: {message}", file=sys.stderr)
    print("ok" if not errors else f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
