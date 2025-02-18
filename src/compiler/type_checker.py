import compiler.ast as ast
from typing import Any
from compiler.types import Type, FunType, Int, Bool, Unit
from compiler.symtab import SymTab


def typecheck(
    node: ast.Expression,
    symbol_table: SymTab[Any]
) -> Type:
    match node:
        case ast.Literal():
            if isinstance(node.value, bool):
                return Bool
            if isinstance(node.value, int):
                return Int
            if node.value is None:
                return Unit
            raise TypeError(f"Unsupported literal type: {node.value}")

        case ast.Identifier():
            return symbol_table.lookup(node.name)

        case ast.LiteralVarDecl():
            inferred_type = annotate_types(node.initializer, symbol_table)
            if node.type is not Unit and node.type is not inferred_type:
                raise TypeError(
                    f"Type mismatch in declaration of '{node.identifier.name}': "
                    f"declared type {node.type} but initializer has type {inferred_type}"
                )
            symbol_table.set(node.identifier.name, inferred_type, local=True)
            return inferred_type if node.as_expression else Unit

        case ast.BinaryOp():
            if node.op == "=":
                if not isinstance(node.left, ast.Identifier):
                    raise TypeError(
                        "Left-hand side of assignment must be an identifier"
                    )
                declared_type = symbol_table.lookup(node.left.name)
                assigned_type = annotate_types(node.right, symbol_table)
                if declared_type is not assigned_type:
                    raise TypeError(
                        f"Assignment type mismatch: variable '{
                            node.left.name}' is {declared_type} " f"but got {assigned_type}"
                        )
                return assigned_type
            else:
                t1 = annotate_types(node.left, symbol_table)
                t2 = annotate_types(node.right, symbol_table)
                op = symbol_table.lookup(node.op)
                result = op(t1, t2)
                if result is Unit:
                    raise TypeError(
                        f"Invalid types for binary operation '{node.op}'"
                    )
                return result

        case ast.UnaryOp():
            operand_type = annotate_types(node.operand, symbol_table)
            op = symbol_table.lookup("unary_" + node.op)
            result_type = op(operand_type)
            if result_type is Unit:
                raise TypeError(
                    f"Unary operator '{node.op}' is not defined for type {operand_type}"
                )
            return result_type

        case ast.IfExpr():
            cond_type = annotate_types(node.condition, symbol_table)
            if cond_type is not Bool:
                raise TypeError("Condition of if must be a boolean")
            then_type = annotate_types(node.then, symbol_table)
            else_type = annotate_types(node.else_, symbol_table)
            if then_type is not else_type:
                raise TypeError(
                    "Both branches of if-then-else must have the same type"
                )
            return then_type

        case ast.WhileExpr():
            cond_type = annotate_types(node.condition, symbol_table)
            if cond_type is not Bool:
                raise TypeError("Condition of while must be a boolean")
            annotate_types(node.body, symbol_table)
            return Unit

        case ast.FuncExpr():
            fun = symbol_table.lookup(node.identifier.name)
            if not isinstance(fun, FunType):
                raise TypeError(f"{node.identifier.name} is not a function")
            for arg, expected in zip(node.arguments, fun.param_t):
                actual = annotate_types(arg, symbol_table)
                if actual is not expected:
                    raise TypeError(
                        f"In function {node.identifier.name}: expected argument type "
                        f"{expected} but got {actual}"
                    )
            return fun.return_t

        case ast.Statements():
            local_scope = SymTab[Any](parent=symbol_table)
            for expr in node.expressions:
                annotate_types(expr, local_scope)
            return annotate_types(node.result, local_scope) if node.result is not None else Unit

        case _:
            raise Exception(
                f"Typecheck not implemented for node type: {
                    type(node).__name__}"
            )


def annotate_types(node: ast.Expression | None, symbol_table: SymTab[Any]) -> Type:
    if node is None:
        return Unit
    t = typecheck(node, symbol_table)
    node.type = t
    return t
