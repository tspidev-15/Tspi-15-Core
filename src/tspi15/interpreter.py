"""Parser and interpreter for the TSPI-15 v0.1 language."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


class TSPIError(Exception):
    """A user-facing TSPI-15 syntax or runtime error."""

    def __init__(self, line: int, message: str):
        self.line = line
        self.message = message
        super().__init__(f"Line {line}: {message}")


@dataclass
class SourceLine:
    number: int
    indent: int
    text: str


@dataclass
class Token:
    kind: str
    value: Any


def _strip_comment(text: str) -> str:
    in_string = False
    escaped = False
    for index, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char == "#":
            return text[:index]
    return text


def _decode_string(raw: str, line: int) -> str:
    result = []
    index = 1
    while index < len(raw) - 1:
        char = raw[index]
        if char != "\\":
            result.append(char)
            index += 1
            continue
        index += 1
        if index >= len(raw) - 1:
            raise TSPIError(line, "Incomplete escape sequence in text.")
        escaped = raw[index]
        mapping = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}
        if escaped not in mapping:
            raise TSPIError(line, f"Unknown escape sequence: \\{escaped}.")
        result.append(mapping[escaped])
        index += 1
    return "".join(result)


def _tokenize(text: str, line: int) -> list[Token]:
    result = []
    pattern = re.compile(
        r'\s*(?:(\d+(?:\.\d+)?)|("(?:\\.|[^"\\])*")|'
        r'([A-Za-z_][A-Za-z0-9_]*)|(==|!=|>=|<=|[+\-*/()<>]))'
    )
    index = 0
    while index < len(text):
        match = pattern.match(text, index)
        if not match:
            if text[index:].strip() == "":
                break
            raise TSPIError(line, f"Unexpected character near {text[index:]!r}.")
        number, string, identifier, operator = match.groups()
        index = match.end()
        if number is not None:
            value = float(number) if "." in number else int(number)
            result.append(Token("literal", value))
        elif string is not None:
            result.append(Token("literal", _decode_string(string, line)))
        elif identifier is not None:
            if identifier == "true":
                result.append(Token("literal", True))
            elif identifier == "false":
                result.append(Token("literal", False))
            elif identifier in ("and", "or"):
                result.append(Token("operator", identifier))
            else:
                result.append(Token("name", identifier))
        else:
            result.append(Token("operator", operator))
    result.append(Token("eof", None))
    return result


class ExpressionParser:
    precedence = {
        "or": 1, "and": 2,
        "==": 3, "!=": 3, ">": 3, "<": 3, ">=": 3, "<=": 3,
        "+": 4, "-": 4, "*": 5, "/": 5,
    }

    def __init__(self, text: str, line: int):
        self.tokens = _tokenize(text, line)
        self.index = 0
        self.line = line

    def current(self):
        return self.tokens[self.index]

    def take(self):
        token = self.current()
        self.index += 1
        return token

    def parse(self):
        if self.current().kind == "eof":
            raise TSPIError(self.line, "Expected an expression.")
        expression = self.expression(1)
        if self.current().kind != "eof":
            raise TSPIError(self.line, f"Unexpected token {self.current().value!r}.")
        return expression

    def expression(self, minimum):
        token = self.take()
        if token.kind == "literal":
            left = ("literal", token.value)
        elif token.kind == "name":
            left = ("name", token.value)
        elif token.kind == "operator" and token.value == "-":
            left = ("unary", self.expression(6))
        elif token.kind == "operator" and token.value == "(":
            left = self.expression(1)
            if self.current().kind != "operator" or self.current().value != ")":
                raise TSPIError(self.line, "Missing closing parenthesis.")
            self.take()
        else:
            raise TSPIError(self.line, f"Unexpected token {token.value!r} in expression.")

        while self.current().kind == "operator":
            operator = self.current().value
            priority = self.precedence.get(operator, 0)
            if priority < minimum:
                break
            self.take()
            right = self.expression(priority + 1)
            left = ("binary", operator, left, right)
        return left


class Parser:
    def __init__(self, source: str):
        self.lines = []
        for number, raw in enumerate(source.splitlines(), 1):
            prefix = raw[:len(raw) - len(raw.lstrip(" \t"))]
            if "\t" in prefix:
                raise TSPIError(number, "Use four spaces for indentation; tabs are not allowed.")
            cleaned = _strip_comment(raw).rstrip()
            if not cleaned.strip():
                continue
            indent = len(cleaned) - len(cleaned.lstrip(" "))
            if indent % 4:
                raise TSPIError(number, "Indentation must use multiples of four spaces.")
            self.lines.append(SourceLine(number, indent, cleaned[indent:]))
        self.index = 0

    def parse(self):
        result = self.block(0)
        if self.index < len(self.lines):
            raise TSPIError(self.lines[self.index].number, "Unexpected indentation.")
        return result

    def block(self, indent):
        statements = []
        while self.index < len(self.lines):
            line = self.lines[self.index]
            if line.indent < indent:
                break
            if line.indent > indent:
                raise TSPIError(line.number, "Unexpected indentation; check the preceding block.")
            statements.append(self.statement(line))
        return statements

    def body(self, parent_indent, line_number):
        if self.index >= len(self.lines) or self.lines[self.index].indent <= parent_indent:
            raise TSPIError(line_number, "Expected an indented block.")
        if self.lines[self.index].indent != parent_indent + 4:
            raise TSPIError(self.lines[self.index].number, "A block must be indented by four spaces.")
        result = self.block(parent_indent + 4)
        if not result:
            raise TSPIError(line_number, "A block cannot be empty.")
        return result

    def expr(self, text, line):
        return ExpressionParser(text, line).parse()

    def statement(self, line):
        text = line.text
        self.index += 1

        if text.startswith("var "):
            match = re.fullmatch(
                r"var\s+([A-Za-z_][A-Za-z0-9_]*)"
                r"(?:\s*:\s*(number|text|boolean))?"
                r"(?:\s*=\s*(.+))?", text
            )
            if not match:
                raise TSPIError(line.number, "Expected var name = expression, or var name: type.")
            name, declared_type, expression = match.groups()
            if expression is None and declared_type is None:
                raise TSPIError(line.number, "A variable without a value needs an explicit type.")
            value = None if expression is None else self.expr(expression, line.number)
            return ("var", name, declared_type, value, line.number)

        if text.startswith("show "):
            return ("show", self.expr(text[5:].strip(), line.number), line.number)

        if text.startswith("when ") and text.endswith(":"):
            condition = self.expr(text[5:-1].strip(), line.number)
            body = self.body(line.indent, line.number)
            otherwise = []
            if self.index < len(self.lines):
                nxt = self.lines[self.index]
                if nxt.indent == line.indent and nxt.text == "otherwise:":
                    self.index += 1
                    otherwise = self.body(line.indent, nxt.number)
            return ("when", condition, body, otherwise, line.number)

        if text.startswith("otherwise"):
            raise TSPIError(line.number, "otherwise must immediately follow a when block.")

        if text.startswith("function "):
            match = re.fullmatch(r"function\s+([A-Za-z_][A-Za-z0-9_]*):", text)
            if not match:
                raise TSPIError(line.number, "Use function name:; parameters are not supported in v0.1.")
            return ("function", match.group(1), self.body(line.indent, line.number), line.number)

        if text == "return":
            return ("return", None, line.number)
        if text.startswith("return "):
            return ("return", self.expr(text[7:].strip(), line.number), line.number)

        assignment = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)\s*(.+)", text)
        if assignment:
            name, expression = assignment.groups()
            return ("assign", name, self.expr(expression, line.number), line.number)

        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", text):
            return ("expression", text, line.number)

        raise TSPIError(line.number, "Unrecognized statement.")


@dataclass
class Variable:
    type_name: str
    value: Any = None
    initialized: bool = False


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class Interpreter:
    def __init__(self, output=None):
        self.variables = {}
        self.functions = {}
        self.output = output if output is not None else print
        self.call_depth = 0

    def run(self, source):
        self.execute_block(Parser(source).parse(), False)

    def execute_block(self, statements, in_function):
        for statement in statements:
            kind = statement[0]
            if kind == "var":
                _, name, declared_type, expression, line = statement
                if expression is None:
                    self.variables[name] = Variable(declared_type, None, False)
                else:
                    value = self.evaluate(expression, line)
                    target = declared_type or self.type_of(value)
                    self.variables[name] = Variable(target, self.coerce(value, target, line), True)
            elif kind == "assign":
                _, name, expression, line = statement
                if name not in self.variables:
                    raise TSPIError(line, f"Variable {name!r} is not defined.")
                variable = self.variables[name]
                variable.value = self.coerce(self.evaluate(expression, line), variable.type_name, line)
                variable.initialized = True
            elif kind == "show":
                _, expression, line = statement
                self.output(self.format_value(self.evaluate(expression, line)))
            elif kind == "when":
                _, condition, body, otherwise, line = statement
                branch = body if self.truthy(self.evaluate(condition, line)) else otherwise
                self.execute_block(branch, in_function)
            elif kind == "function":
                _, name, body, line = statement
                self.functions[name] = (body, line)
            elif kind == "return":
                _, expression, line = statement
                if not in_function:
                    raise TSPIError(line, "return can only be used inside a function.")
                if expression is None:
                    raise TSPIError(line, "return must include a value in TSPI-15 v0.1.")
                raise ReturnSignal(self.evaluate(expression, line))
            elif kind == "expression":
                name, line = statement[1], statement[2]
                if name in self.functions:
                    self.call_function(name, line)
                elif name in self.variables:
                    self.read_variable(name, line)
                else:
                    raise TSPIError(line, f"Function or variable {name!r} is not defined.")

    def evaluate(self, expression, line):
        kind = expression[0]
        if kind == "literal":
            return expression[1]
        if kind == "name":
            name = expression[1]
            if name in self.variables:
                return self.read_variable(name, line)
            if name in self.functions:
                return self.call_function(name, line)
            raise TSPIError(line, f"Variable or function {name!r} is not defined.")
        if kind == "unary":
            return -self.to_number(self.evaluate(expression[1], line), line)
        if kind == "binary":
            operator, left_expr, right_expr = expression[1:]
            left = self.evaluate(left_expr, line)
            if operator == "and":
                return self.truthy(left) and self.truthy(self.evaluate(right_expr, line))
            if operator == "or":
                return self.truthy(left) or self.truthy(self.evaluate(right_expr, line))
            right = self.evaluate(right_expr, line)
            if operator in ("+", "-", "*", "/"):
                return self.arithmetic(operator, left, right, line)
            return self.compare(operator, left, right, line)
        raise TSPIError(line, "Internal expression error.")

    @staticmethod
    def type_of(value):
        if type(value) is bool:
            return "boolean"
        if isinstance(value, (int, float)):
            return "number"
        if isinstance(value, str):
            return "text"
        raise TypeError("Unsupported TSPI-15 value.")

    def coerce(self, value, target, line):
        if target == "number":
            return self.to_number(value, line)
        if target == "text":
            if isinstance(value, str):
                return value
            if type(value) is bool:
                return "true" if value else "false"
            if isinstance(value, (int, float)):
                return self.format_value(value)
        if target == "boolean":
            return self.truthy(value)
        raise TSPIError(line, f"Cannot convert value to type {target!r}.")

    def to_number(self, value, line):
        if type(value) is bool:
            return 1 if value else 0
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str) and value.strip():
            try:
                number = float(value.strip())
                return int(number) if number.is_integer() and "." not in value.strip() else number
            except ValueError:
                pass
        raise TSPIError(line, f"Cannot convert {value!r} to a number.")

    def arithmetic(self, operator, left, right, line):
        if operator == "+" and isinstance(left, str) and isinstance(right, str):
            return left + right
        left, right = self.to_number(left, line), self.to_number(right, line)
        if operator == "+":
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        if right == 0:
            raise TSPIError(line, "Division by zero.")
        return left / right

    def compare(self, operator, left, right, line):
        same_type = self.type_of(left) == self.type_of(right)
        if operator in ("==", "!="):
            if same_type:
                equal = left == right
            else:
                try:
                    equal = self.to_number(left, line) == self.to_number(right, line)
                except TSPIError:
                    equal = False
            return equal if operator == "==" else not equal

        if isinstance(left, str) and isinstance(right, str):
            try:
                left, right = self.to_number(left, line), self.to_number(right, line)
            except TSPIError:
                pass
        elif not same_type or self.type_of(left) != "number":
            left, right = self.to_number(left, line), self.to_number(right, line)
        try:
            return {
                ">": lambda: left > right,
                "<": lambda: left < right,
                ">=": lambda: left >= right,
                "<=": lambda: left <= right,
            }[operator]()
        except TypeError:
            raise TSPIError(line, "These values cannot be compared.")

    @staticmethod
    def truthy(value):
        if type(value) is bool:
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return value != ""
        return bool(value)

    @staticmethod
    def format_value(value):
        if type(value) is bool:
            return "true" if value else "false"
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

    def read_variable(self, name, line):
        variable = self.variables[name]
        if not variable.initialized:
            raise TSPIError(line, f"Variable {name!r} has not been initialized.")
        return variable.value

    def call_function(self, name, line):
        if self.call_depth >= 100:
            raise TSPIError(line, "Maximum function call depth exceeded.")
        body, _ = self.functions[name]
        self.call_depth += 1
        try:
            try:
                self.execute_block(body, True)
            except ReturnSignal as returned:
                return returned.value
            raise TSPIError(line, f"Function {name!r} finished without returning a value.")
        finally:
            self.call_depth -= 1


def run_source(source: str, output=None) -> None:
    """Parse and execute a TSPI-15 source string."""
    Interpreter(output=output).run(source)
