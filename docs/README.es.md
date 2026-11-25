# AngelScript Agent Kit

**[English](../README.md)** | **[Español](README.es.md)**

Una skill y una configuración MCP para que un agente de IA lea, escriba y valide AngelScript con el [servidor de lenguaje de AngelScript](https://github.com/Gaftherman/angelscript-lsp).

La skill enseña la gramática y el flujo de trabajo. El servidor MCP da al agente el proyecto: el punto de entrada del módulo, las reglas del motor, la API del host y los diagnósticos en vivo.

## Instalación

1. Instala el servidor de lenguaje (`angel-lsp`) y ponlo en el PATH. [Releases](https://github.com/Gaftherman/angelscript-lsp/releases)
2. Añade el plugin en Claude Code:

~~~text
> /plugin marketplace add Gaftherman/angelscript-agent-kit
> /plugin install angelscript-agent-kit
~~~

Para otro agente, copia `skills/angelscript/` a su carpeta de skills y añade este servidor MCP:

~~~json
{ "mcpServers": { "angelscript": { "command": "angel-lsp", "args": ["--mcp", "--mcp-root", "/ruta/al/proyecto"] } } }
~~~

## Qué recibe el agente

| Herramienta | Uso |
| --- | --- |
| `workspace_info` | Punto de entrada del módulo, stubs predefinidos, archivo de reglas, ajustes |
| `engine_rules` | Propiedades del motor y reglas de seguridad del host |
| `module_graph` | Archivos alcanzables desde el punto de entrada del módulo |
| `predefined_lookup` | Declaración de un tipo, función o namespace del host |
| `workspace_symbols`, `document_symbols` | Buscar símbolos |
| `definition`, `references`, `hover`, `signature_help`, `completion` | Navegar y leer |
| `open_document`, `apply_edit`, `replace_document` | Editar en memoria |
| `diagnostics` | Comprobar lo que cambió |

`workspace_info`, `engine_rules`, `module_graph`, `references`, `workspace_symbols` y `predefined_lookup` requieren una versión de `angel-lsp` que las incluya.

## Contenido de la skill

- `SKILL.md`: cuándo usarla y el flujo de trabajo.
- `references/grammar.md`: sintaxis y diferencias con C++.
- `references/rules-json.md`: cada sección de `*.angelscript.rules.json`.
- `references/predefined.md`: cómo leer los stubs `.as.predefined`.
- `references/workflow.md`: listas de pasos para tareas comunes.
- `references/cli.md`: ejecutar y comprobar scripts con la [CLI de AngelScript](https://github.com/Gaftherman/angelscript-cli).

## Validar

~~~sh
python -I scripts/validate.py --compile /ruta/a/asc
~~~

Comprueba los manifiestos, el frontmatter de la skill y los enlaces, y compila cada ejemplo `angelscript` con `asc --check`.

## Créditos

- [AngelScript](https://github.com/anjo76/angelscript) de Andreas Jönsson (licencia zlib): el lenguaje que enseña este kit.
- [Servidor de lenguaje de AngelScript](https://github.com/Gaftherman/angelscript-lsp): el servidor MCP detrás de las herramientas. Se apoya en [Relrin/tree-sitter-angelscript](https://github.com/Relrin/tree-sitter-angelscript) y en los proyectos de su sección de créditos.
- [CLI de AngelScript](https://github.com/Gaftherman/angelscript-cli): ejecuta y comprueba los ejemplos.

## Licencia

[MIT](../LICENSE). Para ayudar, lee [CONTRIBUTING.es.md](CONTRIBUTING.es.md).
