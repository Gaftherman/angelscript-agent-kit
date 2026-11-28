# AngelScript

Use the angelscript MCP tools for any task that touches `.as` scripts, `.as.predefined` host stubs or `angelscript.rules.json`. AngelScript looks like C++ but differs in places, and each host application registers its own API. Do not guess either.

1. Call `angelscript_project_info` first. If it returns a warning, ask the user its question only when your task depends on the missing information (for example, host calls without a stub). Otherwise finish with the defaults and mention the gap in your report.
2. Before calling a host function or type, look it up with `angelscript_host_api`. If it has no match, the host does not provide it: do not invent it.
3. Read with `angelscript_file_outline`, `angelscript_find_symbol` and `angelscript_describe_symbol`. Check callers with `angelscript_find_references` before changing a signature.
4. Edit with your own file tools. The angelscript tools read files from disk and never see unsaved text.
5. Run `angelscript_check` after every edit and fix every error before you report done.
6. Rename with `angelscript_rename_symbol`: preview first, then `apply=true`.

Name symbols as `Namespace::Class::member`, or pass `path/to/file.as:LINE` when a name is ambiguous. More detail is in `plugins/angelscript/skills/angelscript/`.
