# AngelScript Agent Kit

**[English](../README.md)** | **[Español](README.es.md)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![release](https://img.shields.io/github/v/release/angelscript-tools/angelscript-agent-kit)](https://github.com/angelscript-tools/angelscript-agent-kit/releases)

Una skill y un servidor MCP para que un agente de IA escriba, compruebe y refactorice scripts de [AngelScript](https://www.angelcode.com/angelscript/) que se ejecutan dentro de una aplicación anfitriona, como un juego. Funciona con Claude Code, Codex, Gemini CLI, Antigravity (`agy`), Cursor, OpenCode y cualquier cliente con soporte MCP.

La skill enseña el flujo de trabajo y las trampas del lenguaje. El servidor MCP, [angelscript-mcp](https://github.com/angelscript-tools/angelscript-mcp), da al agente el proyecto: comprobación de compilación, búsqueda de símbolos y la API exacta que registra la aplicación anfitriona.

## Instalación

Necesitas Node.js 20 o superior. El servidor MCP se ejecuta con `npx` y descarga la primera vez el [servidor de lenguaje](https://github.com/angelscript-tools/angelscript-lsp/releases) que envuelve.

| Agente | Comando |
| --- | --- |
| Claude Code | `/plugin marketplace add angelscript-tools/angelscript-agent-kit` y luego `/plugin install angelscript-agent-kit --marketplace angelscript-tools/angelscript-agent-kit` |
| Codex | `codex plugin marketplace add angelscript-tools/angelscript-agent-kit` y luego `codex plugin add angelscript-agent-kit@angelscript-agent-kit` |
| Gemini CLI | `gemini extensions install https://github.com/angelscript-tools/angelscript-agent-kit` |
| Antigravity (`agy`) | `git clone https://github.com/angelscript-tools/angelscript-agent-kit` y luego `agy plugin install ./angelscript-agent-kit` |
| Cualquier otro | Añade el servidor MCP de abajo y copia `skills/angelscript/` en la carpeta de skills del agente |

El servidor MCP solo:

~~~json
{ "mcpServers": { "angelscript": { "command": "npx", "args": ["-y", "@angelscript-tools/mcp"] } } }
~~~

- **Codex sin el plugin:** `codex mcp add angelscript -- npx -y @angelscript-tools/mcp`
- **Cursor:** pon el JSON anterior en `.cursor/mcp.json`.
- **OpenCode:** en `opencode.json` añade `"mcp": { "angelscript": { "type": "local", "command": ["npx", "-y", "@angelscript-tools/mcp"] } }`.
- **Windows:** si un cliente no puede iniciar `npx`, usa `"command": "cmd"` con `"args": ["/c", "npx", "-y", "@angelscript-tools/mcp"]`.

El servidor lee las claves `angelscript.*` de `.vscode/settings.json` en la carpeta del proyecto: el stub de la API del anfitrión (`.as.predefined`), el punto de entrada del módulo y los directorios de búsqueda. Sin un stub solo puede comprobar el lenguaje en sí, y se lo dice al agente.

## Qué obtiene el agente

| Herramienta | Uso |
| --- | --- |
| `angelscript_project_info` | Versión del motor, stubs del anfitrión, módulos, archivo de reglas y avisos de configuración |
| `angelscript_check` | Comprueba la compilación de archivos y lista errores con línea y columna |
| `angelscript_host_api` | Busca una función, tipo o enum del anfitrión, con documentación y miembros |
| `angelscript_find_symbol` | Encuentra dónde se declara una clase, función o campo |
| `angelscript_find_references` | Lista cada uso de un símbolo, agrupado por archivo |
| `angelscript_file_outline` | La estructura de un archivo sin leerlo entero |
| `angelscript_describe_symbol` | Firma y documentación de un símbolo |
| `angelscript_rename_symbol` | Renombra entre archivos; primero muestra una vista previa y escribe con `apply=true` |

Las herramientas leen los archivos del disco, así que el agente edita con sus propias herramientas de archivos y después llama a `angelscript_check`. Solo `angelscript_rename_symbol` con `apply=true` escribe.

## Contenido de la skill

- `SKILL.md`: cuándo usarla y el flujo de trabajo.
- `references/grammar.md`: sintaxis y diferencias con C++.
- `references/rules-json.md`: cada sección de `*.angelscript.rules.json`.
- `references/predefined.md`: cómo leer los stubs `.as.predefined`.
- `references/workflow.md`: listas de comprobación para tareas habituales.
- `references/cli.md`: ejecutar y comprobar scripts sueltos con la [CLI de AngelScript](https://github.com/angelscript-tools/angelscript-cli).

## Evaluar

`scripts/eval.py` da a un agente tres tareas en un espacio de trabajo aleatorio nuevo: corregir errores de compilación, añadir una función que use la API del anfitrión y renombrar un método. Después comprueba el resultado con una llamada MCP aparte: los scripts compilan, el stub del anfitrión no se ha tocado y está el texto esperado.

~~~sh
python -I scripts/eval.py codex --mcp-entry /ruta/a/angelscript-mcp/dist/index.js --lsp-path /ruta/a/angel_lsp
python -I scripts/eval.py agy   --mcp-entry /ruta/a/angelscript-mcp/dist/index.js --lsp-path /ruta/a/angel_lsp
~~~

Añade `--no-skill` para medir qué aporta la skill. Los escenarios están en `evals/scenarios.json`.

## Validar

~~~sh
python -I scripts/validate.py --compile /ruta/a/asc
~~~

Comprueba los manifiestos de cada agente, el frontmatter de la skill, los nombres de herramientas usados en la documentación y los enlaces, y compila cada ejemplo `angelscript` con `asc --check`.

## Soporte

Abre un [issue](https://github.com/angelscript-tools/angelscript-agent-kit/issues). Para ayudar, lee [CONTRIBUTING.es.md](CONTRIBUTING.es.md).

## Relacionados

| Proyecto | Uso |
| --- | --- |
| [angelscript-mcp](https://github.com/angelscript-tools/angelscript-mcp) | El servidor MCP detrás de este kit |
| [angelscript-lsp](https://github.com/angelscript-tools/angelscript-lsp) | El servidor de lenguaje que envuelve el servidor MCP |
| [angelscript-cli](https://github.com/angelscript-tools/angelscript-cli) | Ejecuta y comprueba scripts desde el terminal |
| [angelscript-dap](https://github.com/angelscript-tools/angelscript-dap) | Núcleo del depurador |

## Créditos

| Proyecto | Licencia | Uso |
| --- | --- | --- |
| [AngelScript](https://github.com/anjo76/angelscript) de Andreas Jönsson | zlib | El lenguaje que enseña este kit |
| [Relrin/tree-sitter-angelscript](https://github.com/Relrin/tree-sitter-angelscript) | MIT | Gramática del servidor de lenguaje |

## Licencia

Este repositorio está bajo la [licencia MIT](../LICENSE).
