# Engine rules (`*.angelscript.rules.json`)

A rules file tells the language server how the host engine is configured, so it reports what the real compiler and the host's safety policy would reject. Do not hand-read it: call `engine_rules`, which returns the rules in effect and the file they came from.

## Where the file comes from

1. The `angelscript.rulesFile` setting, if set.
2. Otherwise the first `*.angelscript.rules.json` found in the workspace root and in the folders of the active predefined stubs.

`workspace_info` reports the path. No file means no host rules: only the default language rules apply.

Schema: <https://raw.githubusercontent.com/Gaftherman/angelscript-lsp/main/schemas/angelscript.rules.schema.json>

## Sections

| Section | Meaning | What to do as an agent |
| --- | --- | --- |
| `name` | Display name of the ruleset. | Mention it when you describe the host. |
| `noHandleTypes` | Value types that cannot have `@` handles. | Never write `T@` or `array<T@>` for these types. |
| `engine` | The AngelScript release the host embeds: `version`, `source` (`official` or `custom`) and `name`. Default 2.39.0. | Do not use syntax or properties newer than `version`. |
| `engineProperties` | The host's `asEP_*` settings. | Obey them, see below. |
| `storageRules` | Where unsafe types may be stored (members, globals, arrays). | Use the `suggestReplacement` type instead of the forbidden storage. |
| `typeSuggestions` | Discouraged types and their replacement. | Use `toType` when the rule applies to your scope. |
| `callRules` (alias `schedulerRules`) | Checks on calls: forbidden argument types, forbidden callback parameters, forbidden methods. | Do not pass the forbidden type. Follow `suggestReplacement`. |
| `unusedSymbolRules` | Which unused symbols are reported and which names the host calls. | Treat `ignoredGlobalFunctions`, lifecycle methods and callbacks as entry points. |

## Minimal file

Offer this when `workspace_info` reports `no-rules-file`, after asking the user for the engine version:

```json
{
  "$schema": "https://raw.githubusercontent.com/Gaftherman/angelscript-lsp/main/schemas/angelscript.rules.schema.json",
  "name": "my-host",
  "engine": { "version": "2.39.0", "source": "official" }
}
```

## `engineProperties`

| Property | Effect on the code you write |
| --- | --- |
| `propertyAccessorMode` | `0` disabled, `1` explicit `get`/`set` only, `2` automatic virtual properties, `3` also on handles. Do not use `get`/`set` blocks when it is `0`. |
| `disallowGlobalVars` | No global variable declarations. |
| `requireEnumScope` | Write `Color::Red`, not `Red`. |
| `boolConversionMode` | `0` strict: write `x != 0`, `h !is null`. `1` allows numbers and handles in conditions. |
| `allowUnsafeReferences` | `&` references without a direction are allowed. |
| `allowMultilineStrings` | Plain `"` strings may span lines. |
| `disableIntegerDivision` | `/` on integers yields a float. |

## `storageRules` and `callRules` by example

```json
{
  "storageRules": [
    {
      "id": "no-raw-entity-members",
      "inheritsFrom": "CBaseEntity",
      "handleOnly": true,
      "disallowInMembers": true,
      "suggestReplacement": "EHandle",
      "severity": "error"
    }
  ],
  "callRules": [
    {
      "id": "no-raw-handles-in-timers",
      "receiverTypes": ["CScheduler"],
      "methods": ["SetTimeout"],
      "disallowParamInheritsFrom": "CBaseEntity",
      "disallowParamHandleOnly": true,
      "paramSuggestReplacement": "EHandle",
      "severity": "error"
    }
  ]
}
```

Meaning: a class member of type `CBaseEntity@` is an error, store an `EHandle`. A callback passed to `CScheduler::SetTimeout` must not take a `CBaseEntity@` parameter.

## Editing a rules file

Only change it when the user asks. After editing, call `workspace_info` and `engine_rules` again to confirm the server loaded it, then call `diagnostics` on a script the rule should affect.
