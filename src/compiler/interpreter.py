import compiler.ast as ast
from typing import Optional, Callable, Union, Any
from compiler.symtab import SymTab

Value = Union[int, bool, None, Optional[Callable[..., Any]]]


def interpret(
    node: Optional[ast.Expression],
    symbol_table: SymTab[Value]
) -> Value:
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
                    raise TypeError(
                        "Left-hand side of assignment must be an identifier"
                    )
            elif node.op == "or":
                left = interpret(node.left, symbol_table)
                return left or interpret(node.right, symbol_table)
            elif node.op == "and":
                left = interpret(node.left, symbol_table)
                return left if not left else interpret(
                    node.right, symbol_table)
            else:
                a = interpret(node.left, symbol_table)
                b = interpret(node.right, symbol_table)
                op = symbol_table.lookup(node.op)
                if not callable(op):
                    raise TypeError(f"'{node.op}' is not callable")
                return op(a, b)

        case ast.UnaryOp():
            operand = interpret(node.operand, symbol_table)
            op = symbol_table.lookup(f"unary_{node.op}")
            if not callable(op):
                raise TypeError(f"'{node.op}' is not callable")
            return op(operand)

        case ast.IfExpr():
            if interpret(node.condition, symbol_table):
                return interpret(node.then, symbol_table)
            else:
                return interpret(node.else_, symbol_table)

        case ast.FuncExpr():
            func = symbol_table.lookup(node.identifier.name)
            if not callable(func):
                raise TypeError(f"'{func}' is not callable")
            args = [interpret(arg, symbol_table) for arg in node.arguments]
            return func(*args)

        case ast.LiteralVarDecl():
            value = interpret(node.initializer, symbol_table)
            symbol_table.set(node.identifier.name, value, local=True)
            return None

        case ast.Statements():
            local_symtab = SymTab(parent=symbol_table)
            for expr in node.expressions:
                interpret(expr, local_symtab)
            if node.result:
                return interpret(node.result, local_symtab)
            return None

        case ast.WhileExpr():
            while interpret(node.condition, symbol_table):
                interpret(node.body, symbol_table)
            return None

        case _:
            raise ValueError(f"Unsupported node type: {type(node).__name__}")
