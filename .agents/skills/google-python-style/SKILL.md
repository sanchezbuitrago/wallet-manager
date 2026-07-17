---
name: google-python-style
description: Google Python Style Guide - comprehensive guidelines for writing clean, maintainable Python code following Google standards.
---

# Google Python Style Guide

When writing Python code, follow these rules from the Google Python Style Guide.

## Core Principles

1. **Be Consistent** - Follow existing code conventions in the project
2. **Be Readable** - Code is read more than written
3. **Keep it Simple** - Avoid clever tricks; clarity over brevity

## Import Rules

### Import complete modules, not names

```python
# CORRECT
import os
import sys
from collections.abc import Mapping, Sequence

# WRONG
from os import getcwd, path
from sys import argv, exit
```

**Exception**: `typing` and `collections.abc` imports are exempt - you may import names directly.

### Import organization (in order)

1. `from __future__ import annotations`
2. Standard library imports
3. Third-party imports (e.g., `from pydantic import BaseModel`)
4. Local imports (full package path: `from app.commons import ...`)

### Never use relative imports

```python
# CORRECT
from mypackage.mymodule import MyClass

# WRONG
from .mymodule import MyClass
```

## Line Length

- **Maximum 80 characters**
- Exceptions: URLs, import statements, long strings, pylint comments
- Use implicit line continuation (parentheses, brackets, braces)
- Never use backslash for line continuation

```python
# CORRECT
result = [
    some_function(x)
    for x in range(10)
    if x > 5
]

# WRONG
result = [some_function(x) for x in range(10) if x > 5]
```

## Indentation

- **4 spaces** for indentation
- **Never use tabs**
- Closing brackets can be at end of expression or on separate line (indented same as opening)

```python
# CORRECT
def function_name(
    arg1,
    arg2,
    arg3,
) -> None:
    ...

# WRONG - 2-space indent
def function_name(
  arg1,
  arg2,
)
```

## Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Modules | `lower_with_under` | `my_module.py` |
| Classes | `CapWords` | `MyClass` |
| Functions/Methods | `lower_with_under()` | `my_function()` |
| Variables | `lower_with_under` | `my_var` |
| Constants | `CAPS_WITH_UNDER` | `MAX_VALUE` |
| Private | `_leading_underscore` | `_internal_var` |
| Protected methods | `_leading_underscore()` | `_helper()` |

## Docstrings

### Module docstring

```python
"""Module docstring - brief description of the module.

Provides functionality for X, Y, Z.
"""
```

### Class docstring

```python
class MyClass:
    """Brief description of the class.

    More detailed description if needed.
    """
    
    def method(self) -> None:
        """Brief description of the method.
        
        Args:
            param1: Description of param1.
            param2: Description of param2.
            
        Returns:
            Description of return value.
            
        Raises:
            ValueError: When X happens.
        """
```

### Function docstring

```python
def my_function(param1: str, param2: int) -> bool:
    """Brief description of the function.
    
    Args:
        param1: Description of param1.
        param2: Description of param2.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: When X happens.
    """
```

## Type Annotations

### Always annotate public APIs

```python
def my_function(x: int, y: str) -> bool:
    ...
```

### Use modern syntax (Python 3.10+)

```python
# CORRECT
def my_function(x: str | None) -> str:
    ...

# WRONG
from typing import Optional
def my_function(x: Optional[str]) -> str:
    ...
```

### Use abstract types in annotations

```python
from collections.abc import Sequence, Mapping

# CORRECT
def process(items: Sequence[int]) -> Mapping[str, int]:
    ...

# WRONG
def process(items: list[int]) -> dict[str, int]:
    ...
```

## Whitespace

### Around operators

```python
# CORRECT
x = 1
y = x + 1
z = (x == y)
if x > 5:
    ...

# WRONG
x=1
y = x+1
z = (x==y)
if x>5:
```

### No spaces inside brackets

```python
# CORRECT
spam(ham[1], {'eggs': 2}, [])

# WRONG
spam( ham[ 1 ], { 'eggs': 2 }, [ ] )
```

### Spaces around `=` only for keyword args with type annotations

```python
# CORRECT
def func(a: int = 0) -> int:
    ...

# WRONG
def func(a: int=0) -> int:
    ...
```

## Comments

### When to comment

- Explain **why** something is done, not **what**
- Don't comment obvious code
- Use `# TODO:` for temporary solutions

```python
# CORRECT
# Performance workaround: MongoDB doesn't support transactions
# in shared clusters, so we use manual idempotency checks
result = await collection.find_one({"id": id})

# WRONG
result = await collection.find_one({"id": id})  # find one document
```

## Error Handling

### Catch specific exceptions

```python
# CORRECT
try:
    result = await db.find_one({"id": id})
except pymongo.errors.PyMongoError as e:
    logger.error(f"Database error: {e}")

# WRONG
try:
    result = await db.find_one({"id": id})
except Exception as e:
    logger.error(f"Error: {e}")
```

### Don't use assert in production code

```python
# CORRECT
if not condition:
    raise ValueError("Condition not met")

# WRONG
assert condition, "Condition not met"
```

## Files and Resources

### Always close resources with context managers

```python
# CORRECT
with open("file.txt") as f:
    content = f.read()

# WRONG
f = open("file.txt")
content = f.read()
f.close()
```

## Strings

### Use f-strings

```python
# CORRECT
name = "Alice"
greeting = f"Hello, {name}!"

# WRONG
greeting = "Hello, %s!" % name
greeting = "Hello, {}!".format(name)
```

### Prefer single quotes, but be consistent

```python
# Either is fine:
greeting = 'Hello, World!'
greeting = "Hello, World!"
```

## Collections

### Use appropriate types

```python
# List for ordered, mutable sequences
items: list[int] = [1, 2, 3]

# Tuple for immutable sequences
point: tuple[int, int] = (1, 2)

# Dict for key-value pairs
config: dict[str, str] = {"key": "value"}

# Set for unique elements
unique: set[int] = {1, 2, 3}
```

## Boolean Context

### Use implicit falsy checks

```python
# CORRECT
if not items:
    print("no items")

if not user:
    print("no user")

# WRONG
if len(items) == 0:
    print("no items")

if user is None:
    print("no user")
```

## Comprehensions

### Keep them simple

```python
# CORRECT
result = [x * 2 for x in items if x > 5]

# WRONG - too complex
result = [x * 2 for x in items if x > 5 and x % 2 == 0 for y in range(x)]
```

## Main Block

### Always use `if __name__ == '__main__':`

```python
def main() -> None:
    """Main entry point."""
    ...

if __name__ == "__main__":
    main()
```

## Summary Checklist

- [ ] Imports: complete modules, no relative imports
- [ ] Line length: max 80 chars (use implicit continuation)
- [ ] Indentation: 4 spaces, no tabs
- [ ] Naming: `lower_with_under` for functions/variables, `CapWords` for classes
- [ ] Docstrings: all public APIs
- [ ] Type annotations: all public APIs
- [ ] Whitespace: around operators, no inside brackets
- [ ] Comments: explain why, not what
- [ ] Errors: catch specific exceptions
- [ ] Resources: use context managers
- [ ] Strings: use f-strings
- [ ] Booleans: use implicit falsy checks
- [ ] Main: `if __name__ == '__main__':`