# Contribuir a AngelScript Agent Kit

**[English](../CONTRIBUTING.md)** | **[Español](CONTRIBUTING.es.md)**

Gracias por ayudar. Se agradecen los informes de errores, las correcciones, la documentación y los ejemplos.

## Informar de un problema

Abre una [incidencia](https://github.com/angelscript-tools/angelscript-agent-kit/issues) con la versión que usas, tu sistema operativo, los pasos para reproducirlo y la salida que viste. Lo que más ayuda es un script de pocas líneas que reproduzca el problema.

## Proponer un cambio

1. Haz un fork del repositorio y crea una rama desde `main`.
2. Mantén cada cambio pequeño y enfocado, con pruebas cuando cambie el comportamiento.
3. Escribe los mensajes de commit como `tipo(ámbito): descripción breve en imperativo` sin punto final. Tipos: `feat`, `fix`, `test`, `perf`, `refactor`, `style`, `docs`, `chore`.
4. Abre una pull request que explique qué cambió y cómo lo comprobaste.

## Compilar y probar

El kit es Markdown y JSON. Valídalo antes de enviar un cambio:

~~~sh
python scripts/validate.py
~~~

## Estilo

Mantén las instrucciones cortas y concretas. Sigue `.editorconfig` (LF, UTF-8). Da formato a Python con `ruff format`.

## Licencia

Al contribuir aceptas que tu trabajo se publique bajo la [licencia MIT](../LICENSE).

## Proyectos relacionados

| Proyecto | Uso |
| --- | --- |
| [angelscript-dap](https://github.com/angelscript-tools/angelscript-dap) | El núcleo del depurador |
| [angelscript-debugger-example](https://github.com/angelscript-tools/angelscript-debugger-example) | Una aplicación que muestra cómo usar el depurador |
| [angelscript-cli](https://github.com/angelscript-tools/angelscript-cli) | Ejecuta, comprueba y depura scripts desde la terminal |
| [angelscript-lsp](https://github.com/angelscript-tools/angelscript-lsp) | Soporte del editor para VS Code |
