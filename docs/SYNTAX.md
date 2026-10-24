# TSPI-15 Syntax — v0.1

This document describes the implemented draft syntax and runtime behavior for TSPI-15 v0.1.

## 1. Source files and indentation

Programs are UTF-8 text files, conventionally ending in `.tspi`. Indentation uses multiples of four spaces. Tabs used for indentation are rejected. Blank lines are ignored.

Comments start with `#` and continue to the end of the line, except when `#` appears inside a quoted string.

## 2. Variables

~~~tspi
var name = "Alex"
var points = 100
var active = true
var unassigned: number
unassigned = 25
~~~

Types are `number` (integers and decimals), `text` (double-quoted strings), and `boolean` (`true` or `false`). A variable without an initial value must have an explicit type. Reading it before assignment is an error. Ordinary assignment converts to the variable's existing type when supported. A new `var` declaration replaces an existing global variable and may change its type.

Variables are global, including variables declared in conditional blocks. A declaration only happens if execution reaches it.

## 3. Output and expressions

~~~tspi
show "Hello"
show points
show (2 + 3) * 4
~~~

Arithmetic operators are `+`, `-`, `*`, and `/`. Parentheses have highest precedence, followed by unary minus, `*` and `/`, then `+` and `-`. Comparisons are `==`, `!=`, `>`, `<`, `>=`, and `<=`. Logical operators are `and` and `or`; `and` has higher precedence, and both operators short-circuit.

`+` concatenates two text values. Otherwise, arithmetic attempts to convert operands to numbers. Numeric text such as `"12.5"` and booleans (`true` becomes `1`, `false` becomes `0`) can convert to numbers. Non-numeric text in numeric arithmetic raises an error. Division by zero is an error; `5 / 2` produces `2.5`.

## 4. Automatic conversion

- To `number`: numbers remain numbers; booleans become `1` or `0`; numeric text is parsed after trimming surrounding whitespace.
- To `text`: text remains unchanged; booleans become `true` or `false`; numbers are formatted as text.
- To `boolean`: `false`, `0`, and empty text become false; `true`, nonzero numbers, and non-empty text become true.

An invalid conversion to `number` raises a runtime error. For equality, same-type values are compared directly. Mixed types are compared after numeric conversion if possible; if conversion fails, mixed-type equality is false and inequality is true. For ordering, two numeric text values are compared numerically; otherwise two text values are compared lexicographically. Mixed-type ordering attempts numeric conversion and errors if it fails.

## 5. Conditions

~~~tspi
when points >= 50:
    show "Passed"
otherwise:
    show "Failed"
~~~

A `when` block must contain a statement. `otherwise` is optional, must immediately follow its `when` block, and must also contain a statement. Nested conditions are supported.

Conditions use truthiness: `true` is true, `false` is false, `0` is false, nonzero numbers are true, empty text is false, and non-empty text is true.

## 6. Functions

~~~tspi
function get_score:
    return 100

var score = get_score
show score
~~~

Functions have no parameters in v0.1 and are called by writing their name without parentheses. A function must return a value during every actual call. A definition does not need to return along every possible branch, but if a call reaches the end without `return`, a runtime error is raised. `return` outside a function and `return` without a value are errors. Nested function calls are limited to 100 levels.

Functions must be defined before they are called. Variables and functions share expression names; when a name exists as both, the variable takes precedence in expressions. A bare statement containing a function name calls it.

## 7. Errors and limitations

The interpreter stops at the first syntax or runtime error and reports the source line. User input, loops, function parameters, local scopes, and multi-error recovery are not implemented in v0.1.