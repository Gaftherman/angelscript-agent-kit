# Task checklists

## Add a feature to a script

1. `workspace_info`, `engine_rules`, `module_graph`.
2. `document_symbols` of the file and `workspace_symbols` for similar names: follow the local style and reuse helpers.
3. `predefined_lookup` for every host type or function you plan to call.
4. `open_document`, then `apply_edit` for small changes or `replace_document` for new files.
5. `diagnostics` on each changed file. Repeat until it reports no errors.
6. If you changed a signature, call `references` and update every caller, then run `diagnostics` on those files too.

## Fix a diagnostic

1. `diagnostics` returns the code, range and message. Read the message: it often names the replacement type.
2. `hover` on the symbol and `definition` to see the declaration.
3. Fix the cause. Do not silence it with a rules change or a different stub unless the user asks.
4. Run `diagnostics` again.

## Rename or move a symbol

1. `references` with `includeDeclaration` to list every use, including other files in the module (`module_graph`).
2. Edit each place, then `diagnostics` on every touched file.
3. Strings that name a function (callbacks registered by name) do not show up in `references`. Look for them in `engine_rules` under `unusedSymbolRules.stringReflectionCallees`.

## New project

1. Ask which host runs the scripts and get its `.as.predefined` stub and `*.angelscript.rules.json`. Without them the server only checks the language itself.
2. Pick the module entry point: the file the host loads first. Setting `angelscript.moduleEntryPoint` makes the server check the module as one unit.
3. Confirm with `workspace_info`.

## Before you say it is done

- `diagnostics` is clean on every file you touched.
- Every host API you used came from `predefined_lookup`.
- Entry points the host calls still exist with the same signature.
- If a runner is installed, `asc --check <entry>` passes.
