"""Run the kit's scenarios against a real agent and verify the outcome independently.

Usage:
  python -I scripts/eval.py codex --mcp-entry /path/to/angelscript-mcp/dist/index.js --lsp-path /path/to/angel_lsp
  python -I scripts/eval.py agy   --mcp-entry ... --lsp-path ... [--scenario fix-errors] [--seed 7]

Each scenario gets a fresh random workspace. The agent edits it with the MCP
server attached (and the skill, unless --no-skill). A separate MCP call then
checks that the scripts compile, the host stub is untouched and the expected
text is present. Exit code 1 if any scenario fails.
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "evals"))
import fixture  # noqa: E402


def tool(name: str) -> str:
    found = shutil.which(name)
    if not found:
        sys.exit(f"error: '{name}' is not on PATH")
    return found


def toml_string(value: str) -> str:
    return json.dumps(value.replace("\\", "/"))


def check_errors(args: argparse.Namespace, root: Path) -> int:
    command = [
        tool("npx"), "--yes", "@modelcontextprotocol/inspector", "--cli",
        "node", args.mcp_entry, "--root", str(root), "--lsp-path", args.lsp_path,
        "--method", "tools/call", "--tool-name", "angelscript_check",
        "--tool-arg", "min_severity=error", "--tool-arg", "response_format=json",
    ]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    payload = json.loads(result.stdout)
    return int(json.loads(payload["content"][0]["text"])["errors"])


def run_codex(args: argparse.Namespace, root: Path, prompt: str) -> str:
    if not args.no_skill:
        shutil.copytree(ROOT / "plugins" / "angelscript" / "skills" / "angelscript", root / ".agents" / "skills" / "angelscript")
    server = [
        "-c", f"mcp_servers.angelscript.command={toml_string('node')}",
        "-c", "mcp_servers.angelscript.args=" + json.dumps([args.mcp_entry, "--root", str(root), "--lsp-path", args.lsp_path]).replace("\\\\", "/"),
        "-c", 'mcp_servers.angelscript.default_tools_approval_mode="approve"',
    ]
    command = [tool("codex"), "exec", "--skip-git-repo-check", "-s", "workspace-write", "-C", str(root), *server, prompt]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=args.timeout, stdin=subprocess.DEVNULL)
    return result.stdout + result.stderr


def run_agy(args: argparse.Namespace, root: Path, prompt: str) -> str:
    if not args.no_skill:
        shutil.copy(ROOT / "AGENTS.md", root / "AGENTS.md")
        shutil.copytree(ROOT / "plugins" / "angelscript" / "skills" / "angelscript", root / ".agents" / "skills" / "angelscript")
    name = "zz-angelscript-eval"
    agy = tool("agy")
    subprocess.run([agy, "mcp", "add", name, "node", args.mcp_entry, "--root", str(root), "--lsp-path", args.lsp_path], check=True, capture_output=True)
    try:
        command = [agy, "-p", prompt, "--model", args.agy_model, "--sandbox", "--dangerously-skip-permissions", "--print-timeout", f"{args.timeout}s"]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=args.timeout + 30, cwd=root, stdin=subprocess.DEVNULL)
        return result.stdout + result.stderr
    finally:
        subprocess.run([agy, "mcp", "remove", name], capture_output=True)


def evaluate(args: argparse.Namespace, scenario: dict, seed: int) -> dict:
    work = Path(tempfile.mkdtemp(prefix="asevals-"))
    fx = fixture.create(work, seed)
    names = {"host_spawn": fx.host_spawn, "host_damage": fx.host_damage, "host_log": fx.host_log, "script_method": fx.script_method}
    stub_hash = hashlib.sha256(fx.stub_text().encode()).hexdigest()
    prompt = scenario["prompt"].format(**names)
    transcript = (run_codex if args.agent == "codex" else run_agy)(args, work, prompt)
    expect = scenario["expect"]
    failures = []

    errors = check_errors(args, work)
    if errors != expect["check_errors"]:
        failures.append(f"{errors} compile errors remain")
    if expect.get("stub_unchanged") and hashlib.sha256(fx.stub_text().encode()).hexdigest() != stub_hash:
        failures.append("the host stub was modified")
    main = (work / "scripts" / "main.as").read_text(encoding="utf-8")
    for needle in expect.get("main_contains", []):
        if needle.format(**names) not in main:
            failures.append(f"main.as lacks '{needle.format(**names)}'")
    for needle in expect.get("main_lacks", []):
        if needle.format(**names) in main:
            failures.append(f"main.as still has '{needle.format(**names)}'")
    used = sorted(set(re.findall(r"angelscript/(angelscript_\w+)", transcript)))
    if args.agent == "codex":
        for required in expect.get("tools_used", []):
            if required not in used:
                failures.append(f"the agent never called {required}")
    result = {"scenario": scenario["id"], "agent": args.agent, "seed": seed, "passed": not failures, "failures": failures, "tools_used": used}
    if not args.keep:
        shutil.rmtree(work, ignore_errors=True)
    else:
        (work / "transcript.txt").write_text(transcript, encoding="utf-8")
        result["workspace"] = str(work)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("agent", choices=["codex", "agy"])
    parser.add_argument("--mcp-entry", required=True, help="path to angelscript-mcp dist/index.js")
    parser.add_argument("--lsp-path", required=True, help="path to the angel_lsp executable")
    parser.add_argument("--scenario", action="append", help="scenario id (repeatable); default: all")
    parser.add_argument("--seed", type=int, default=20261128)
    parser.add_argument("--timeout", type=int, default=300, help="seconds per scenario")
    parser.add_argument("--agy-model", default="Gemini 3.8 Flash (High)")
    parser.add_argument("--no-skill", action="store_true", help="run without the skill, to measure what it adds")
    parser.add_argument("--keep", action="store_true", help="keep the workspaces")
    args = parser.parse_args()

    scenarios = json.loads((ROOT / "evals" / "scenarios.json").read_text(encoding="utf-8"))
    if args.scenario:
        scenarios = [s for s in scenarios if s["id"] in args.scenario]
    results = [evaluate(args, scenario, args.seed + index) for index, scenario in enumerate(scenarios)]
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{status}  {result['scenario']}  tools={','.join(result['tools_used']) or 'n/a'}")
        for failure in result["failures"]:
            print(f"      - {failure}")
    print(json.dumps(results))
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
