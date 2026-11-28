# AngelScript Agent Kit

**[English](README.md)** | **[Español](docs/README.es.md)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![release](https://img.shields.io/github/v/release/angelscript-tools/angelscript-agent-kit)](https://github.com/angelscript-tools/angelscript-agent-kit/releases)

A skill and an MCP server that let an AI agent write, check and refactor [AngelScript](https://www.angelcode.com/angelscript/) scripts that run inside a host application, such as a game. It works with Claude Code, Codex, Gemini CLI, Antigravity (`agy`), Cursor, OpenCode and any client that supports MCP.

The skill teaches the workflow and the traps of the language. The MCP server, [angelscript-mcp](https://github.com/angelscript-tools/angelscript-mcp), gives the agent the project: compile checks, symbol search and the exact API the host registers.

## Install

You need Node.js 20 or newer. The MCP server runs with `npx`, and downloads the [language server](https://github.com/angelscript-tools/angelscript-lsp/releases) it wraps on first use.

| Agent | Command |
| --- | --- |
| Claude Code | `/plugin marketplace add angelscript-tools/angelscript-agent-kit`, then `/plugin install angelscript@angelscript-agent-kit` and `/plugin install angelscript-mcp@angelscript-agent-kit` |
| Codex | `codex plugin marketplace add angelscript-tools/angelscript-agent-kit` then `codex plugin add angelscript-agent-kit@angelscript-agent-kit` |
| Gemini CLI | `gemini extensions install https://github.com/angelscript-tools/angelscript-agent-kit` |
| Antigravity (`agy`) | `git clone https://github.com/angelscript-tools/angelscript-agent-kit` then `agy plugin install ./angelscript-agent-kit/plugins/angelscript` and `agy plugin install ./angelscript-agent-kit/plugins/angelscript-mcp` |
| Any other | Add the MCP server below and copy `plugins/angelscript/skills/angelscript/` into the agent's skills folder |

Claude Code gets two plugins: `angelscript` (the skill, the part submitted to the Claude plugin directory) and `angelscript-mcp` (the MCP server, which starts a local command and so is installed from this marketplace only).

The MCP server on its own:

~~~json
{
  "mcpServers": {
    "angelscript": {
      "command": "npx",
      "args": ["-y", "@angelscript-tools/mcp"]
    }
  }
}
~~~

- **Codex without the plugin:** `codex mcp add angelscript -- npx -y @angelscript-tools/mcp`
- **Cursor:** put the JSON above in `.cursor/mcp.json`.
- **OpenCode:** in `opencode.json` add `"mcp": { "angelscript": { "type": "local", "command": ["npx", "-y", "@angelscript-tools/mcp"] } }`.
- **Windows:** if a client cannot start `npx`, use `"command": "cmd"` with `"args": ["/c", "npx", "-y", "@angelscript-tools/mcp"]`.

The server reads the `angelscript.*` keys of `.vscode/settings.json` in the project folder: the host API stub (`.as.predefined`), the module entry point and the search directories. Without a stub it can only check the language itself, and it tells the agent so.

## What the agent gets

| Tool | Use |
| --- | --- |
| `angelscript_project_info` | Engine version, host stubs, modules, rules file and setup warnings |
| `angelscript_check` | Compile-check files and list errors with line and column |
| `angelscript_host_api` | Look up a host function, type or enum, with documentation and members |
| `angelscript_find_symbol` | Find where a class, function or field is declared |
| `angelscript_find_references` | List every use of a symbol, grouped by file |
| `angelscript_file_outline` | The structure of a file without reading it all |
| `angelscript_describe_symbol` | Signature and documentation of a symbol |
| `angelscript_rename_symbol` | Rename across files; previews first, writes on `apply=true` |

The tools read files from disk, so the agent edits with its own file tools and then calls `angelscript_check`. Only `angelscript_rename_symbol` with `apply=true` writes.

## Skill contents

- `SKILL.md`: when to use it and the workflow.
- `references/grammar.md`: syntax and the differences from C++.
- `references/rules-json.md`: every section of `*.angelscript.rules.json`.
- `references/predefined.md`: how to read `.as.predefined` stubs.
- `references/workflow.md`: checklists for common tasks.
- `references/cli.md`: run and check loose scripts with the [AngelScript CLI](https://github.com/angelscript-tools/angelscript-cli).

## Evaluate

`scripts/eval.py` gives an agent three tasks on a fresh random workspace: fix compile errors, add a function that uses the host API, and rename a method. It then checks the result with a separate MCP call: the scripts compile, the host stub is untouched and the expected text is present.

~~~sh
python -I scripts/eval.py codex --mcp-entry /path/to/angelscript-mcp/dist/index.js --lsp-path /path/to/angel_lsp
python -I scripts/eval.py agy   --mcp-entry /path/to/angelscript-mcp/dist/index.js --lsp-path /path/to/angel_lsp
~~~

Add `--no-skill` to measure what the skill adds. The scenarios live in `evals/scenarios.json`.

## Validate

~~~sh
python -I scripts/validate.py --compile /path/to/asc
~~~

It checks the manifests of every agent, the skill frontmatter, the tool names used in the docs and the links, and compiles every `angelscript` sample with `asc --check`.

## Support

Open an [issue](https://github.com/angelscript-tools/angelscript-agent-kit/issues). To help, read [CONTRIBUTING.md](CONTRIBUTING.md).

## Related

| Project | Use |
| --- | --- |
| [angelscript-mcp](https://github.com/angelscript-tools/angelscript-mcp) | The MCP server behind this kit |
| [angelscript-lsp](https://github.com/angelscript-tools/angelscript-lsp) | The language server the MCP server wraps |
| [angelscript-cli](https://github.com/angelscript-tools/angelscript-cli) | Run and check scripts from the terminal |
| [angelscript-dap](https://github.com/angelscript-tools/angelscript-dap) | Debugger core |

## Credits

| Project | License | Use |
| --- | --- | --- |
| [AngelScript](https://github.com/anjo76/angelscript) by Andreas Jönsson | zlib | The language this kit teaches |
| [Relrin/tree-sitter-angelscript](https://github.com/Relrin/tree-sitter-angelscript) | MIT | Grammar behind the language server |

## License

This repository is licensed under the [MIT License](LICENSE).
