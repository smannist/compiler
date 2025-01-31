import sys
import compiler.ast as ast
from typing import Any, Optional, Dict, Callable, Union


type Value = Union[int, bool, None, Callable]


class SymTab:
    def __init__(self) -> None:
        self.symbols: Dict[str, Any] = {
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
            "and": lambda a, b: a and b,
            "or": lambda a, b: a or b,
            "False": False,
            "True": True,
            "None": None,
        }
        self.functions: Dict[str, Callable] = {
            "print_int": lambda a: print(a),
            "print_bool": lambda a: print("true" if a else "false"),
            "read_int": lambda: int(sys.stdin.readline().strip())
        }

    def declare(self, symbol: str, value: Any) -> None:
        self.symbols[symbol] = value

    def lookup(self, value: str) -> Any:
        if value in self.symbols:
            return self.symbols[value]
        if value in self.functions:
            return self.functions[value]
        raise Exception(f"Symbol '{value}' not found.")


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
                    symbol_table.declare(node.left.name, value)
                    return value
                else:
                    raise TypeError(f"Left-hand side of assignment must be an identifier, got {type(node.left)}")
            operator = symbol_table.lookup(node.op)
            a = interpret(node.left, symbol_table)
            b = interpret(node.right, symbol_table)
            operator = symbol_table.lookup(node.op)
            return operator(a, b)
        case ast.UnaryOp():
            operand = interpret(node.operand, symbol_table)
            operator = symbol_table.lookup(f"unary_{node.op}")
            return operator(operand)
        case ast.IfExpr():
            if interpret(node.condition, symbol_table):
                return interpret(node.then, symbol_table)
            return interpret(node.else_, symbol_table)
        case ast.FuncExpr():
            func = symbol_table.lookup(node.identifier.name)
            args = [interpret(arg, symbol_table) for arg in node.arguments]
            return func(*args)
        case ast.LiteralVarDecl():
            symbol_table.declare(
                node.identifier.name,
                interpret(node.initializer, symbol_table)
            )
            return None
        case ast.Statements():
            for expr in node.expressions:
                interpret(expr, symbol_table)
                if node.result is not None:
                    if isinstance(node.result, ast.Literal) and node.result.value is None:
                        return symbol_table.lookup(str(node.result.value))
                    else:
                        return interpret(node.result, symbol_table)
            return None
        case _:
            raise ValueError(f"Unsupported node type: {type(node).__name__}")
