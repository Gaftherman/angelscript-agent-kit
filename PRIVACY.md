# Privacy

The AngelScript skill and the `angelscript-mcp` plugin collect no personal data and have no telemetry or accounts.

- **Skill (`angelscript`):** plain Markdown instructions. It runs nothing and sends nothing.
- **MCP server (`angelscript-mcp`):** runs on your machine and reads only the AngelScript files of the workspace you point it at. It sends no source code or results anywhere.
- **Network use:** the first start downloads the pinned `angel_lsp` release and its `SHA256SUMS` from the GitHub releases of `angelscript-tools/angelscript-lsp`, and verifies the checksum. npm and GitHub receive the usual request metadata, such as your IP address.

Your AI client, not this project, handles whatever you send to the model. See its own privacy policy.

Questions: open an issue at <https://github.com/angelscript-tools/angelscript-agent-kit/issues>.
