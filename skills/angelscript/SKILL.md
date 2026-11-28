---
name: angelscript
description: Writes, reviews and fixes AngelScript (.as) scripts that run inside a host application such as a game, using the angelscript MCP server for compile checks, symbol search and host API lookup. Use when a task touches .as files, .as.predefined host stubs, angelscript.rules.json, a module entry point, or an application that embeds AngelScript.
license: MIT
compatibility: Needs the angelscript MCP server (npx -y @angelscript-tools/mcp) and Node.js 20 or newer.
---

# AngelScript

AngelScript looks like C++ but differs in places, and every host application registers its own API. Do not guess either: ask the angelscript tools. Your client may show their names with a prefix, such as `mcp__angelscript__angelscript_check`.

## Tools

| Tool | Use it to |
| --- | --- |
| `angelscript_project_info` | Learn the engine version, host stubs, modules and rules. Call it first. |
| `angelscript_check` | Compile-check files and list errors. Call it after every edit. |
| `angelscript_host_api` | Look up a host function, type or enum before using it. |
| `angelscript_find_symbol` | Find where a class, function or field is declared. |
| `angelscript_find_references` | List every use of a symbol before changing it. |
| `angelscript_file_outline` | See a file's structure without reading all of it. |
| `angelscript_describe_symbol` | Read a symbol's signature and documentation. |
| `angelscript_rename_symbol` | Rename across files. Previews by default; `apply=true` writes. |

Name symbols as `Namespace::Class::member`. When a name is ambiguous or overloaded, pass `path/to/file.as:LINE`.

## Workflow

1. **Learn the project.** Call `angelscript_project_info`. If it returns a warning, read "When setup is missing" below: ask only when your task depends on what is missing.
2. **Find the host API before using it.** Call `angelscript_host_api` for every host type or function you plan to call. If it reports no match, the host does not provide that name: do not invent it. Use a suggested name or ask the user.
3. **Read before editing.** Use `angelscript_file_outline` and `angelscript_find_symbol` to follow the local style and reuse helpers. Use `angelscript_describe_symbol` for exact signatures.
4. **Edit with your own file tools.** The angelscript tools read files from disk and never see unsaved text. Only `angelscript_rename_symbol` with `apply=true` writes.
5. **Check after every edit.** Call `angelscript_check`. Fix every error before you report done. A warning from a `storageRules` or `callRules` entry is a host constraint, not noise.
6. **Changing a signature?** Call `angelscript_find_references` first, update each caller, then check those files too.

## When setup is missing

`angelscript_project_info` lists warnings, each with a `code` and a question. Do not stop the task for a gap it does not need. Finish with the defaults and say in your report what was missing. Ask the user only in these cases:

- `no-rules-file`: the engine version and properties are unknown, and 2.39.0 is assumed. Ask only when the task needs a feature that depends on the version or on engine properties. Offer the minimal file in [references/rules-json.md](references/rules-json.md).
- `no-predefined`: the host API is unknown. Ask for the `.as.predefined` stub or the API reference before writing code that calls the host. Never invent host functions or types.
- `no-module-entry-point`: ask which script the host loads first and which callbacks it calls only when the task adds or changes a callback.

A feature newer than the engine version is not available: `foreach` needs 2.38, for example. Use the older form.

## Rules that matter most

- Engine properties change what is legal: with `disallowGlobalVars` you cannot declare globals, with `requireEnumScope` you must write `Color::Red`. Use `angelscript_project_info` with `detail: "full"` to see them.
- A function the host calls (`main`, `MapInit`, callbacks) is an entry point. Do not delete it as unused or rename it.
- Check scripts in the context of their module: an included file can compile alone and still fail in the module.
- Do not edit `.as.predefined` stubs to make an error go away. They describe the host, so the script must change.
- `asc --check` from the standalone CLI does not load host stubs. Use `angelscript_check` for scripts that call host APIs. See [references/cli.md](references/cli.md).

## References

- [references/grammar.md](references/grammar.md): syntax and where AngelScript differs from C++.
- [references/rules-json.md](references/rules-json.md): the fields of `*.angelscript.rules.json`.
- [references/predefined.md](references/predefined.md): what `.as.predefined` files are and how to read them.
- [references/workflow.md](references/workflow.md): checklists for common tasks.
- [references/cli.md](references/cli.md): running and checking loose scripts from a terminal.
