# Predefined stubs (`.as.predefined`)

A host registers types and functions in C++, so no `.as` file declares them. A predefined stub is a text file that declares that API in AngelScript syntax so the language server can complete, hover and type-check against it. It is never compiled by the host.

## Finding them

- `workspace_info` returns `activePredefined`, the stubs loaded now.
- Files ending in `.as.predefined` (setting `angelscript.predefinedExtension`) are discovered in the workspace.
- A stub can `#define WORD` the words the host defines, which `#if` blocks in scripts depend on.

## Reading the host API

Do not open stubs and scan them by eye. Call `predefined_lookup` with the name you need:

- `predefined_lookup("CBaseEntity")` returns the declaration, the file and the documentation of the class.
- `predefined_lookup("Math::clamp")` finds a namespaced function.

If nothing matches, the host does not expose that name. Say so, or find an equivalent with `workspace_symbols`.

## What a stub looks like

```text
namespace Game
{
    /** Spawns an entity at a position. */
    CBaseEntity@ Spawn(const string &in className, const Vector &in origin);
}

class CBaseEntity
{
    string GetName() const;
    void SetOrigin(const Vector &in origin);
}
```

Functions and methods have no body: `;` ends the declaration. Doc comments become hover text.

## Rules

- A stub describes the host. If a script does not match it, change the script.
- Do not add declarations for APIs you are unsure exist: the script would pass diagnostics and fail at runtime.
- Edit a stub only when the user says the host changed, and keep the doc comments.
