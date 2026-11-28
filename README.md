# AngelScript Agent Kit

**[English](README.md)** | **[Español](docs/README.es.md)**

A skill and MCP configuration that let an AI agent read, write and validate AngelScript with the [AngelScript language server](https://github.com/angelscript-tools/angelscript-lsp).

The skill teaches the grammar and the workflow. The MCP server gives the agent the project: the module entry point, the engine rules, the host API and live diagnostics.

## Install

1. Install the language server (`angel-lsp`) and put it on PATH. [Releases](https://github.com/angelscript-tools/angelscript-lsp/releases)
2. Add the plugin in Claude Code:

~~~text
> /plugin marketplace add angelscript-tools/angelscript-agent-kit
> /plugin install angelscript-agent-kit
~~~

For another agent, copy `skills/angelscript/` into its skills folder and add this MCP server:

~~~json
{ "mcpServers": { "angelscript": { "command": "angel-lsp", "args": ["--mcp", "--mcp-root", "/path/to/project"] } } }
~~~

## What the agent gets

| Tool | Use |
| --- | --- |
| `workspace_info` | Module entry point, predefined stubs, rules file, settings |
| `engine_rules` | Engine properties and safety rules of the host |
| `module_graph` | Files reachable from the module entry point |
| `predefined_lookup` | Declaration of a host type, function or namespace |
| `workspace_symbols`, `document_symbols` | Find symbols |
| `definition`, `references`, `hover`, `signature_help`, `completion` | Navigate and read |
| `open_document`, `apply_edit`, `replace_document` | Edit in memory |
| `diagnostics` | Check what changed |

`workspace_info`, `engine_rules`, `module_graph`, `references`, `workspace_symbols` and `predefined_lookup` need an `angel-lsp` release that includes them.

## Skill contents

- `SKILL.md`: when to use it and the workflow.
- `references/grammar.md`: syntax and the differences from C++.
- `references/rules-json.md`: every section of `*.angelscript.rules.json`.
- `references/predefined.md`: how to read `.as.predefined` stubs.
- `references/workflow.md`: checklists for common tasks.
- `references/cli.md`: run and check scripts with the [AngelScript CLI](https://github.com/angelscript-tools/angelscript-cli).

## Validate

~~~sh
python -I scripts/validate.py --compile /path/to/asc
~~~

It checks the manifests, the skill frontmatter and the links, and compiles every `angelscript` sample with `asc --check`.

## Support

Open an [issue](https://github.com/angelscript-tools/angelscript-agent-kit/issues). To help, read [CONTRIBUTING.md](CONTRIBUTING.md).

## Related

| Project | Use |
| --- | --- |
| [angelscript-lsp](https://github.com/angelscript-tools/angelscript-lsp) | Language server and MCP tools behind this kit |
| [angelscript-cli](https://github.com/angelscript-tools/angelscript-cli) | Run and check scripts from the terminal |
| [angelscript-dap](https://github.com/angelscript-tools/angelscript-dap) | Debugger core |

## Credits

| Project | License | Use |
| --- | --- | --- |
| [AngelScript](https://github.com/anjo76/angelscript) by Andreas Jönsson | zlib | The language this kit teaches |
| [Relrin/tree-sitter-angelscript](https://github.com/Relrin/tree-sitter-angelscript) | MIT | Grammar behind the language server |

## License

This repository is licensed under the [MIT License](LICENSE).
