import sys
import compiler.ast as ast
from typing import Any, Optional, Callable, Union

Value = Union[int, bool, None, Callable]


class SymTab:
    def __init__(self, parent: Optional["SymTab"] = None) -> None:
        self.parent = parent
        self.symbols = {}
        self.functions = {}

        if parent is None:
            self.symbols.update({
                "unary_-": lambda a: -a,
                "unary_not": lambda a: not a,
                "+": lambda a, b: a + b,
                "-": lambda a, b: a - b,
                "%": lambda a, b: a % b,
                "*": lambda a, b: a * b,
                "/": lambda a, b: a / b,
                "==": lambda a, b: a == b,
                "!=": lambda a, b: a != b,
                "<": lambda a, b: a < b,
                "<=": lambda a, b: a <= b,
                ">": lambda a, b: a > b,
                ">=": lambda a, b: a >= b,
                "False": False,
                "True": True,
                "None": None,
            })
            self.functions.update({
                "print_int": lambda a: print(a),
                "print_bool": lambda a: print("true" if a else "false"),
                "read_int": lambda: int(sys.stdin.readline().strip())
            })

    def lookup(self, name: str) -> Any:
        if name in self.symbols:
            return self.symbols[name]
        if name in self.functions:
            return self.functions[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        raise Exception(f"Symbol or function '{name}' not found.")

    def set(self, name: str, value: Any, local: bool = False) -> None:
        if local or name in self.symbols:
            self.symbols[name] = value
        elif self.parent is not None:
            self.parent.set(name, value)
        else:
            self.symbols[name] = value


def interpret(node: Optional[ast.Expression], symbol_table: SymTab) -> Value:
    if node is None:
        raise ValueError("Expected an AST node.")

    match node:
        case ast.Literal():
            return node.value

        case ast.Identifier():
            return symbol_table.lookup(node.name)

        case ast.BinaryOp():
            if node.op == "=":
                if isinstance(node.left, ast.Identifier):
                    value = interpret(node.right, symbol_table)
                    symbol_table.set(node.left.name, value)
                    return value
                else:
                    raise TypeError("Left-hand side of assignment must be an identifier")
            elif node.op == "or":
                left = interpret(node.left, symbol_table)
                if left:
                    return left
                else:
                    return interpret(node.right, symbol_table)
            elif node.op == "and":
                left = interpret(node.left, symbol_table)
                if not left:
                    return left
                else:
                    return interpret(node.right, symbol_table)
            else:
                a = interpret(node.left, symbol_table)
                b = interpret(node.right, symbol_table)
                op = symbol_table.lookup(node.op)
                return op(a, b)

        case ast.UnaryOp():
            operand = interpret(node.operand, symbol_table)
            op = symbol_table.lookup(f"unary_{node.op}")
            return op(operand)

        case ast.IfExpr():
            if interpret(node.condition, symbol_table):
                return interpret(node.then, symbol_table)
            else:
                return interpret(node.else_, symbol_table)

        case ast.FuncExpr():
            func = symbol_table.lookup(node.identifier.name)
            args = [interpret(arg, symbol_table) for arg in node.arguments]
            return func(*args)

        case ast.LiteralVarDecl():
            value = interpret(node.initializer, symbol_table)
            symbol_table.set(node.identifier.name, value, local=True)
            return None

        case ast.Statements():
            local_scope = SymTab(parent=symbol_table)
            for expr in node.expressions:
                interpret(expr, local_scope)
            if node.result is not None:
                return interpret(node.result, local_scope)
            return None

        case ast.WhileExpr():
            while interpret(node.condition, symbol_table):
                interpret(node.body, symbol_table)
            return None

        case _:
            raise ValueError(f"Unsupported node type: {type(node).__name__}")
