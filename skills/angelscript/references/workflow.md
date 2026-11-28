# Task checklists

## Add a feature to a script

1. `angelscript_project_info`: engine version, stubs, modules and warnings.
2. `angelscript_file_outline` of the file, and `angelscript_find_symbol` for similar names: follow the local style and reuse helpers.
3. `angelscript_host_api` for every host type or function you plan to call.
4. Edit the file with your own file tools.
5. `angelscript_check` on each changed file. Repeat until it reports no errors.
6. If you changed a signature, call `angelscript_find_references` and update every caller, then check those files too.

## Fix a compile error

1. `angelscript_check` returns `path:line:col`, a code and a message. The message often names the replacement type.
2. `angelscript_describe_symbol` on the symbol involved to see its declaration.
3. Fix the cause. Do not silence it with a rules change or a different stub unless the user asks.
4. `angelscript_check` again.

## Rename a symbol

1. `angelscript_rename_symbol` with `apply=false` previews every edit across the module.
2. Read the preview, then call it again with `apply=true`.
3. `angelscript_check` with no `paths` to confirm the whole workspace still compiles.
4. Strings that name a function (callbacks registered by name) are not renamed. Search for them with `angelscript_project_info` `detail: "full"` and the `stringReflectionCallees` rule.

## New project

1. Ask which host runs the scripts and get its `.as.predefined` stub and `*.angelscript.rules.json`. Without them the server only checks the language itself.
2. Pick the module entry point: the file the host loads first. Setting `angelscript.moduleEntryPoint` makes the server check the module as one unit.
3. Confirm with `angelscript_project_info`.

## Before you say it is done

- `angelscript_check` reports 0 errors on every file you touched.
- Every host API you used came from `angelscript_host_api`.
- Entry points the host calls still exist with the same signature.
