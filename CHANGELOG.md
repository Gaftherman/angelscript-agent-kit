# Changelog

## [Unreleased]

## [0.2.2] - 2026-11-28

### Fixed

- Stop tracking the compiled `evals/__pycache__` file that made the release validation fail, and check compiled files against what git tracks instead of the working tree.

### Added

- Add `PRIVACY.md` and the `documentationUrl`, `supportUrl`, `privacyPolicyUrl` and `termsOfServiceUrl` fields to both plugin manifests, and an install line to the skill plugin README, as the plugin directory listing asks.

### Changed

- Use the new icon for both plugins; `plugins/angelscript-mcp` now has one too, and the validator checks both.

## [0.2.1] - 2026-11-28

### Changed

- Split the Claude plugin in two so the skill can go through the plugin directory: `plugins/angelscript` holds the skill and an icon, `plugins/angelscript-mcp` holds the MCP server. The repository root is no longer a plugin.
- Pin the MCP server to `@angelscript-tools/mcp@0.1.0` in every manifest.

### Added

- Add a 512 px icon for the skill plugin, a `.gitignore`, and a validator check that the skill plugin holds only the file types the plugin directory accepts.

---
**Full Changelog**: https://github.com/angelscript-tools/angelscript-agent-kit/compare/v0.2.0...v0.2.1

## [0.2.0] - 2026-11-28

### Fixed

- The Claude Code plugin started `angel-lsp`, a name that does not exist: the executable is `angel_lsp`. The plugin now starts the MCP server with `npx`.

### Changed

- Move the MCP server to its own project, [angelscript-mcp](https://github.com/angelscript-tools/angelscript-mcp), run with `npx -y @angelscript-tools/mcp`. The kit no longer needs `angel_lsp` on `PATH`.
- Replace the fifteen LSP-shaped tools with eight: `angelscript_project_info`, `angelscript_check`, `angelscript_host_api`, `angelscript_find_symbol`, `angelscript_find_references`, `angelscript_file_outline`, `angelscript_describe_symbol` and `angelscript_rename_symbol`. Rewrite the skill, the checklists and every reference for them.
- Tell the agent to ask about a missing rules file, stub or entry point only when the task depends on it, and to say what was missing in its report. Stopping to ask blocked simple fixes.
- Explain that `asc --check` does not load host stubs, so scripts that call host APIs need `angelscript_check`.
- Rewrite both READMEs with an install command for each agent.

### Added

- Add the Codex manifest (`.codex-plugin/plugin.json`), the Gemini CLI extension (`gemini-extension.json`) and `AGENTS.md`.
- Add `scripts/eval.py` and `evals/`: three scenarios on a random workspace, checked by a separate MCP call.
- Make `scripts/validate.py` check every manifest, that the versions and the MCP command agree, the skill frontmatter limits, and that the docs name only existing tools.

---
**Full Changelog**: https://github.com/angelscript-tools/angelscript-agent-kit/compare/v0.1.1...v0.2.0

## [0.1.1] - 2026-11-25

### Added

- Add the "When something is missing" section: ask the user when `workspace_info` reports a missing rules file, stub or entry point, and respect the engine version from `engine_rules`.
- Add `CONTRIBUTING.md` and `docs/CONTRIBUTING.es.md`, move the Spanish README to `docs/`, and add `.editorconfig` and `ruff.toml`.

---
**Full Changelog**: https://github.com/angelscript-tools/angelscript-agent-kit/compare/v0.1.0...v0.1.1

## [0.1.0] - 2026-11-24

### Added

- Add the `angelscript` skill with grammar, engine rules, predefined stubs, workflow and CLI references.
- Add the Claude Code plugin manifest and the MCP configuration for `angel-lsp --mcp`.
- Add `scripts/validate.py` to check the manifests, links and AngelScript samples.
