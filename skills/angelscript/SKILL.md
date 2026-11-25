---
name: angelscript
description: Write, review and fix AngelScript (.as) code with the AngelScript language server over MCP. Use when a task touches .as files, .as.predefined stubs, *.angelscript.rules.json, a module entry point, or a host game or application that embeds AngelScript.
---

# AngelScript with the language server

AngelScript looks like C++ but has its own rules, and each host registers its own API. Never guess either. Ask the language server.

## Workflow

1. **Learn the project first.** Call `workspace_info` for the module entry point, the active predefined stubs and the rules file. Call `engine_rules` for the host's engine properties and safety rules. Call `module_graph` to see which files form the module.
2. **Find the host API before using it.** Call `predefined_lookup` with the type, function or namespace name. If it returns nothing, the host does not provide it: do not invent it.
3. **Read before editing.** Use `document_symbols`, `workspace_symbols`, `definition`, `references` and `hover`.
4. **Edit in memory, then validate.** Use `open_document`, `apply_edit` or `replace_document`, then call `diagnostics` on every file you changed. Fix every error before reporting done. Warnings that a `storageRules` or `callRules` entry produced are host constraints, not noise.
5. **Run it when a runner exists.** `asc --check file.as` compiles without running, `asc file.as` runs it. See [references/cli.md](references/cli.md).

## When something is missing

`workspace_info` returns `warnings`. Each has a `code`, a `message` and an `ask`. When a warning is present, stop and ask the user that question before writing code that depends on it:

- `no-rules-file`: the engine version and engine properties are unknown. Ask which AngelScript version the host embeds (if unsure, the latest, 2.39.0, is assumed) and offer the minimal file in [references/rules-json.md](references/rules-json.md).
- `no-predefined`: the host API is unknown. Ask for the `.as.predefined` stub or the API reference. Never invent host functions or types.
- `no-module-entry-point`: ask which script is the entry point and which callbacks the host calls.

`engine_rules` returns an `engine` section with the declared `version` and `source`. A feature newer than that version (for example `foreach` before 2.38) is not available: use the older form. A `custom` engine keeps its `engineProperties` as the source of truth, so ask when something looks unusual instead of assuming vanilla behaviour.

## Rules that matter most

- Engine properties in `engine_rules` change what is legal: with `disallowGlobalVars` you cannot declare globals, with `requireEnumScope` you must write `Color::Red`.
- A function the host calls (`main`, `MapInit`, callbacks) is an entry point. Do not delete it as unused and do not rename it.
- Check scripts in the context of their module: an included file can compile alone and still fail in the module, and the reverse.
- Do not edit `.as.predefined` stubs to make an error go away. They describe the host, so the script must change.

## References

- [references/grammar.md](references/grammar.md): syntax and the places where AngelScript differs from C++.
- [references/rules-json.md](references/rules-json.md): the fields of `*.angelscript.rules.json` and what they change.
- [references/predefined.md](references/predefined.md): what `.as.predefined` files are and how to read them.
- [references/workflow.md](references/workflow.md): a checklist for common tasks.
- [references/cli.md](references/cli.md): running and checking scripts from a terminal.
