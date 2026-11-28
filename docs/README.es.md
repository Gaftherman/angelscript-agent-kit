# AngelScript Agent Kit

**[English](../README.md)** | **[Español](README.es.md)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![release](https://img.shields.io/github/v/release/angelscript-tools/angelscript-agent-kit)](https://github.com/angelscript-tools/angelscript-agent-kit/releases)

Una skill y un servidor MCP para que un agente de IA escriba, compruebe y refactorice scripts de [AngelScript](https://www.angelcode.com/angelscript/) que se ejecutan dentro de una aplicación anfitriona, como un juego. Funciona con Claude Code, Codex, Gemini CLI, Antigravity (`agy`), Cursor, OpenCode y cualquier cliente con soporte MCP.

La skill enseña el flujo de trabajo y las trampas del lenguaje. El servidor MCP, [angelscript-mcp](https://github.com/angelscript-tools/angelscript-mcp), da al agente el proyecto: comprobación de compilación, búsqueda de símbolos y la API exacta que registra la aplicación anfitriona.

## Instalación

Necesitas Node.js 20 o superior. El servidor MCP se ejecuta con `npx` y descarga la primera vez el [servidor de lenguaje](https://github.com/angelscript-tools/angelscript-lsp/releases) que envuelve.

Elige tu agente. Todos reciben la skill y el servidor MCP.

### Claude Code

~~~text
/plugin marketplace add angelscript-tools/angelscript-agent-kit
/plugin install angelscript@angelscript-agent-kit
/plugin install angelscript-mcp@angelscript-agent-kit
~~~

### Codex

~~~sh
codex plugin marketplace add angelscript-tools/angelscript-agent-kit
codex plugin add angelscript@angelscript-agent-kit
codex plugin add angelscript-mcp@angelscript-agent-kit
~~~

En ejecuciones no interactivas como `codex exec`, `npx` puede arrancar después del primer turno y faltan las herramientas. Para eso, instala el servidor una vez con `npm install -g @angelscript-tools/mcp`, añade solo el primer plugin y registra el servidor con `codex mcp add angelscript -- angelscript-mcp`.

### Gemini CLI

~~~sh
gemini extensions install https://github.com/angelscript-tools/angelscript-agent-kit
gemini skills install https://github.com/angelscript-tools/angelscript-agent-kit --path plugins/angelscript/skills/angelscript
~~~

La extensión añade el servidor MCP y el contexto del proyecto; el segundo comando añade la skill.

### Antigravity (`agy`)

~~~sh
git clone https://github.com/angelscript-tools/angelscript-agent-kit
agy plugin install ./angelscript-agent-kit/plugins/angelscript
agy plugin install ./angelscript-agent-kit/plugins/angelscript-mcp
~~~

### Cualquier otro agente

Añade el servidor MCP de abajo y copia `plugins/angelscript/skills/angelscript/` en la carpeta de skills del agente.

Claude Code recibe dos plugins: `angelscript` (la skill, la parte que se envía al directorio de plugins de Claude) y `angelscript-mcp` (el servidor MCP, que inicia un comando local y por eso se instala solo desde este marketplace).

El servidor MCP solo:

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
| [angelscript-lsp](https://github.com/angelscript-tools/angelscript-lsp) | El servidor de lenguaje que envuelve el servidor MCP |
| [angelscript-cli](https://github.com/angelscript-tools/angelscript-cli) | Ejecuta y comprueba scripts desde el terminal |
| [angelscript-mcp](https://github.com/angelscript-tools/angelscript-mcp) | El servidor MCP detrás de este kit |
| [angelscript-dap](https://github.com/angelscript-tools/angelscript-dap) | Núcleo del depurador |
| [angelscript-debugger-example](https://github.com/angelscript-tools/angelscript-debugger-example) | Una aplicación que muestra cómo integrar el depurador |
| [angelscript-jit](https://github.com/angelscript-tools/angelscript-jit) | Compilador JIT opcional |
| [angelscript-engine](https://github.com/angelscript-tools/angelscript-engine) | Builds del SDK con parches para AngelScript 2.20 a 2.39 |
| [tree-sitter-angelscript](https://github.com/angelscript-tools/tree-sitter-angelscript) | Gramática de Tree-sitter que usa el servidor de lenguaje |

## Créditos

| Proyecto | Licencia | Uso |
| --- | --- | --- |
| [AngelScript](https://github.com/anjo76/angelscript) de Andreas Jönsson | zlib | El lenguaje que enseña este kit |
| [Relrin/tree-sitter-angelscript](https://github.com/Relrin/tree-sitter-angelscript) | MIT | Gramática del servidor de lenguaje |

## Licencia

Este repositorio está bajo la [licencia MIT](../LICENSE).
