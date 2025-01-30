import compiler.ast as ast
from compiler.parser import parse
from compiler.tokenizer import tokenize
from typing import Any, Optional

type Value = int | bool | None

def interpret(node: Optional[ast.Expression]) -> Value:
    if node is None:
        raise ValueError("Expected an AST node.")

    match node:
        case ast.Literal():
            return node.value
        case ast.BinaryOp():
            a: Any = interpret(node.left)
            b: Any = interpret(node.right)
            if node.op == '+':
                return a + b
            elif node.op == '<':
                return a < b
            else:
                raise ValueError(f"Unsupported binary operator: {node.op}")
        case ast.IfExpr():
            if interpret(node.condition):
                return interpret(node.then)
            else:
                return interpret(node.else_)
        case _:
            raise ValueError(f"Unsupported node type: {type(node).__name__}")
