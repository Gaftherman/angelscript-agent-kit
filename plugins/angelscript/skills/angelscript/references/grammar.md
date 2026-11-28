# AngelScript grammar for agents

The examples below compile with the standard library of the AngelScript CLI (`asc --check`). Host engines add types and functions, so always confirm those with `angelscript_host_api`.

## Types

Primitives: `bool`, `int8`, `int16`, `int`, `int64`, `uint8`, `uint16`, `uint`, `uint64`, `float`, `double`. There is no `char`, `long` or `unsigned`. `int` is 32 bits.

```angelscript
int count = 3;
uint64 big = 1;
float ratio = 0.5f;   // the f suffix is required for float literals
double exact = 0.5;
```

## References and handles

- A **handle** (`@`) is a reference-counted pointer to a reference type. `T@ h;` is a handle to `T`. It starts as `null`.
- Plain `T value;` of a class type is the object itself. Assigning copies the value unless you use `@`.
- Assign a handle with `@a = @b;`. Plain `a = b;` copies the object.
- `is` and `!is` compare handles: `if (h is null)`.
- Value types such as `string` and `array<T>` cannot have handles unless the host says so. `angelscript_project_info` with `detail: "full"` lists the `noHandleTypes` of the host.

```angelscript
class Node { int value; }

void handles()
{
    Node@ a = Node();
    Node@ b = a;          // b and a refer to the same object
    Node  c = a;          // c is a copy of the object
    @b = null;
    if (b is null) { a.value = 1; }
    c.value = 2;
}
```

## Parameters

Reference parameters need a direction: `&in`, `&out` or `&inout`. Pass `const T &in` for read-only arguments.

```angelscript
void split(const string &in text, string &out head, string &out tail)
{
    int at = text.findFirst(",");
    head = at < 0 ? text : text.substr(0, at);
    tail = at < 0 ? "" : text.substr(at + 1);
}
```

## Classes and interfaces

```angelscript
interface IShape { float area() const; }

class Circle : IShape
{
    private float radius;
    Circle(float r) { radius = r; }
    float area() const { return 3.14159f * radius * radius; }
}

class Base { void hello() {} }
final class Leaf : Base { }        // final: cannot be inherited
abstract class Shape2 { }          // abstract: cannot be instantiated
```

- Constructors have no return type. A destructor is `~Name()`.
- Members are `public` by default. `private` and `protected` exist.
- Override with `override`, forbid overriding with `final`.
- `shared` classes and functions are visible across modules.
- `mixin class` is copied into the classes that name it after `:`.

## Properties

Virtual properties use `get` and `set`:

```angelscript
class Box
{
    private int _w;
    int w { get const { return _w; } set { _w = value; } }
}
```

They need `propertyAccessorMode` of 2 or higher in the host. `angelscript_project_info` with `detail: "full"` shows it.

## Functions, funcdefs, namespaces

```angelscript
funcdef int Op(int, int);                 // function pointer type

namespace math
{
    int add(int a, int b) { return a + b; }
    int apply(Op@ f, int x, int y) { return f(x, y); }
}

int run() { return math::apply(math::add, 2, 3); }
```

Scope with `::`. A leading `::` means the global scope.

## Enums

```angelscript
enum Color { Red, Green = 5, Blue }
Color pick() { return Color::Green; }   // Color::Red is required when requireEnumScope is set
```

## Control flow

`if`, `else`, `for`, `while`, `do … while`, `switch`/`case`, `break`, `continue`, `return`, `try`/`catch`. `try` has no exception type: `catch { … }` catches any script exception.

## Strings and arrays

```angelscript
void collections()
{
    string s = "a" + 1;                    // concatenation converts numbers
    string raw = """Triple quotes keep \n unescaped""";
    array<int> list = {1, 2, 3};
    list.insertLast(4);
    array<array<int>> grid(2, array<int>(2, 0));
    dictionary map = {{"key", 1}};
}
```

Character escapes are the usual ones. Single-quoted text is a string, not a character, unless the host sets `asEP_USE_CHARACTER_LITERALS`.

## Preprocessor and includes

`#include "path/file.as"` is resolved by the host or the builder, relative to the including file. `#define WORD`, `#if WORD`, `#else` and `#endif` depend on the words the host defines. The server lists them in the `angelscript.define` setting and in the predefined stubs.

## Differences from C++ that cause most mistakes

| C++ habit | AngelScript |
| --- | --- |
| `Type* p` | `Type@ h` |
| `p->field` | `h.field` |
| `&x` | `@x` |
| `nullptr` | `null` |
| `const T& x` | `const T &in x` |
| `new T()` | `T()` or `T@ h = T();` |
| `delete p` | none, handles are reference counted |
| `std::string`, `std::vector` | `string`, `array<T>` |
| `using namespace x;` | supported by AngelScript 2.38 and later, otherwise qualify with `x::` |
| integer literal `10L`, `10U` | no suffixes except `f` on floats |
| `x == y` on handles compares objects | use `is` to compare the handles |
| header files | none, use `#include` or a single module |
