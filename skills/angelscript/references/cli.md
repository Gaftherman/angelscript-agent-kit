# Running scripts with the AngelScript CLI

The CLI is a standalone runtime for loose scripts: <https://github.com/Gaftherman/angelscript-cli>. Use it for scripts that do not need a host game or application. Scripts that call host-only APIs cannot run in it.

```sh
asc --check script.as            # compile only, exit 0 when clean
asc script.as                    # run main()
asc script.as one "two words"    # arguments reach the script through getArgs()
```

`asc`, `angelscript` and `angelscript-cli` are the same program.

- The entry point is `int main()` or `void main()`. The integer is the exit code.
- Compile errors print `path:line:col: error: message` to stderr and exit with 1. Usage errors exit with 2.
- The standard library has `string`, `array`, `dictionary`, math, file, filesystem, date and time, `print`, `println`, `getArgs` and TCP sockets (`tcpConnect`, `tcpListen`).
- To debug, set `angelscript.runner.path` in VS Code or leave it empty to use the CLI from PATH, then press F5.

Prefer the `diagnostics` tool for fast feedback while editing. Use `asc --check` as the final confirmation that the file compiles outside the editor.
