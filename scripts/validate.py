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
SKILL_PLUGIN = ROOT / "plugins" / "angelscript"
MCP_PLUGIN = ROOT / "plugins" / "angelscript-mcp"
SKILL = SKILL_PLUGIN / "skills" / "angelscript"

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
MCP_ARGS = ["-y", "@angelscript-tools/mcp@0.1.1"]
SKILL_PLUGIN_JSON = "plugins/angelscript/.claude-plugin/plugin.json"
MCP_PLUGIN_JSON = "plugins/angelscript-mcp/.claude-plugin/plugin.json"
MCP_JSON = "plugins/angelscript-mcp/.mcp.json"
MANIFESTS = (
    SKILL_PLUGIN_JSON,
    MCP_PLUGIN_JSON,
    ".claude-plugin/marketplace.json",
    ".codex-plugin/plugin.json",
    "gemini-extension.json",
    MCP_JSON,
)
# The directory takes only these file types in the plugin it receives.
DIRECTORY_SUFFIXES = {".md", ".json", ".png", ""}
DIRECTORY_BLOCKED_NAMES = {"agents.md", "claude.md", "claude.local.md", ".mcp.json", "hooks.json", ".lsp.json", "monitors.json"}
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
        for name in (SKILL_PLUGIN_JSON, MCP_PLUGIN_JSON, ".codex-plugin/plugin.json", "gemini-extension.json")
    }
    if len(set(versions.values())) != 1:
        fail(f"plugin versions differ: {versions}")
    listed = {entry.get("name"): entry.get("source") for entry in data[".claude-plugin/marketplace.json"].get("plugins", [])}
    if listed != {"angelscript": "./plugins/angelscript", "angelscript-mcp": "./plugins/angelscript-mcp"}:
        fail(f".claude-plugin/marketplace.json: must list the two plugins under ./plugins, found {listed}")
    if (ROOT / ".claude-plugin" / "plugin.json").exists():
        fail(".claude-plugin/plugin.json: the repository root is not a plugin; keep the manifests under plugins/")
    servers = {
        MCP_JSON: data[MCP_JSON].get("mcpServers", {}).get("angelscript", {}),
        "gemini-extension.json": data["gemini-extension.json"].get("mcpServers", {}).get("angelscript", {}),
    }
    for name, server in servers.items():
        if server.get("command") != "npx" or server.get("args") != MCP_ARGS:
            fail(f"{name}: the angelscript MCP server must run `npx {' '.join(MCP_ARGS)}`")
    if data[MCP_PLUGIN_JSON].get("mcpServers") != "./.mcp.json":
        fail(f"{MCP_PLUGIN_JSON}: mcpServers must point to ./.mcp.json")
    if data[".codex-plugin/plugin.json"].get("mcpServers") != "./plugins/angelscript-mcp/.mcp.json":
        fail(".codex-plugin/plugin.json: mcpServers must point to ./plugins/angelscript-mcp/.mcp.json")
    if data[".codex-plugin/plugin.json"].get("skills") != "./plugins/angelscript/skills/":
        fail(".codex-plugin/plugin.json: skills must be ./plugins/angelscript/skills/")
    if not (ROOT / data["gemini-extension.json"].get("contextFileName", "missing")).exists():
        fail("gemini-extension.json: contextFileName does not exist")


def png_size(path: Path) -> tuple[int, int] | None:
    header = path.read_bytes()[:24]
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")


def check_icon(plugin: Path, manifest_name: str) -> None:
    """Each plugin needs a square PNG icon of 512-2048 px under 2 MB, declared in its manifest."""
    rel = (plugin / ".claude-plugin" / "icon.png").relative_to(ROOT).as_posix()
    icon = ROOT / rel
    size = png_size(icon) if icon.exists() else None
    if size is None:
        fail(f"{rel}: missing or not a PNG")
    elif size[0] != size[1] or not 512 <= size[0] <= 2048 or icon.stat().st_size >= 2_000_000:
        fail(f"{rel}: must be square, 512-2048 px and under 2 MB, found {size}")
    manifest = load(manifest_name)
    if manifest.get("icon") != "./.claude-plugin/icon.png":
        fail(f"{manifest_name}: icon must be ./.claude-plugin/icon.png")
    for field in ("documentationUrl", "supportUrl", "privacyPolicyUrl", "termsOfServiceUrl"):
        if not str(manifest.get(field, "")).startswith("https://"):
            fail(f"{manifest_name}: {field} must be an https URL")


def tracked_files(pattern: str) -> list[str]:
    """Files git tracks that match the pattern; the working tree is the fallback outside a checkout."""
    try:
        result = subprocess.run(["git", "ls-files", pattern, f"**/{pattern}"], cwd=ROOT, capture_output=True, text=True, check=True)
        return sorted(set(result.stdout.split()))
    except (OSError, subprocess.CalledProcessError):
        return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob(pattern) if ".git" not in p.parts)


def check_directory_plugin() -> None:
    """The skill plugin is the folder submitted to the plugin directory, which accepts only inert files."""
    if not SKILL_PLUGIN.is_dir():
        fail("plugins/angelscript is missing")
        return
    manifest = load(SKILL_PLUGIN_JSON)
    if "mcpServers" in manifest:
        fail(f"{SKILL_PLUGIN_JSON}: the directory refuses plugins that start a local MCP server; declare it in plugins/angelscript-mcp")
    for path in sorted(SKILL_PLUGIN.rglob("*")):
        if not path.is_file():
            continue
        name = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() not in DIRECTORY_SUFFIXES or (path.suffix == "" and path.name != "LICENSE"):
            fail(f"{name}: file type not accepted by the directory")
        if path.name.lower() in DIRECTORY_BLOCKED_NAMES:
            fail(f"{name}: file name not accepted by the directory")
        if "__pycache__" in path.parts or "node_modules" in path.parts:
            fail(f"{name}: folder not accepted by the directory")
        if path.suffix.lower() != ".png":
            data = path.read_bytes()
            if data.startswith(b"#!") or b"\0" in data:
                fail(f"{name}: must be UTF-8 text without #! or NUL bytes")
    check_icon(SKILL_PLUGIN, SKILL_PLUGIN_JSON)
    check_icon(MCP_PLUGIN, MCP_PLUGIN_JSON)
    if not (ROOT / ".gitignore").exists() or "__pycache__" not in (ROOT / ".gitignore").read_text(encoding="utf-8"):
        fail(".gitignore must ignore __pycache__")
    compiled = tracked_files("*.pyc")
    if compiled:
        fail(f"remove compiled files from git: {compiled}")


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
    check_directory_plugin()
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
