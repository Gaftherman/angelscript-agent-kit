"""Generate a throwaway AngelScript workspace with random identifiers.

The workspace has a host stub, a util script and a main script with injected
compile errors. Random names keep an agent from passing by memory.
"""

import json
import random
import string
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Fixture:
    root: Path
    seed: int
    host_class: str
    host_namespace: str
    host_spawn: str
    host_log: str
    host_damage: str
    script_class: str
    script_method: str

    def stub_text(self) -> str:
        return (self.root / "api" / "game.as.predefined").read_text(encoding="utf-8")


def _ident(rnd: random.Random, prefix: str) -> str:
    return prefix + "".join(rnd.choice(string.ascii_lowercase) for _ in range(5)).capitalize()


def create(root: Path, seed: int) -> Fixture:
    rnd = random.Random(seed)
    fx = Fixture(
        root=root,
        seed=seed,
        host_class=_ident(rnd, "Ent"),
        host_namespace=_ident(rnd, "Host"),
        host_spawn=_ident(rnd, "Spawn"),
        host_log=_ident(rnd, "Log"),
        host_damage=_ident(rnd, "Hurt"),
        script_class=_ident(rnd, "Actor"),
        script_method=_ident(rnd, "Tick"),
    )
    for folder in (".vscode", "api", "scripts"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    settings = {
        "angelscript.include.implicitExtension": True,
        "angelscript.searchDirectories": ["${workspaceFolder}/scripts"],
        "angelscript.modules": [{"name": "Game", "entry": "${workspaceFolder}/scripts/main.as"}],
        "angelscript.predefined.active": "${workspaceFolder}/api/game.as.predefined",
    }
    (root / ".vscode" / "settings.json").write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    (root / "api" / "game.as.predefined").write_text(
        f"""
class {fx.host_class} {{
    // Current health points.
    int Health() const;
    // Removes health points from the entity.
    void {fx.host_damage}(int amount);
}}

namespace {fx.host_namespace} {{
    // Writes a line to the host console.
    void {fx.host_log}(const string &in message);
    // Creates an entity by name, or null when the name is unknown.
    {fx.host_class}@ {fx.host_spawn}(const string &in name);
}}
""",
        encoding="utf-8",
    )
    (root / "scripts" / "util.as").write_text("int Twice(int value)\n{\n    return value * 2;\n}\n", encoding="utf-8")
    (root / "scripts" / "main.as").write_text(
        f"""#include "util"

class {fx.script_class}
{{
    int hits = 0;

    void {fx.script_method}({fx.host_class}@ target)
    {{
        target.{fx.host_damage}(Twice(3));
        hits++;
    }}
}}

void main()
{{
    {fx.host_class}@ e = {fx.host_namespace}::{fx.host_spawn[:-1]}("rat");
    {fx.host_namespace}::{fx.host_log}(missingText);
    {fx.script_class} actor;
    actor.{fx.script_method}(e);
}}
""",
        encoding="utf-8",
    )
    return fx
