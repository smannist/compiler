import compiler.ast as ast
from typing import Any, Union, Optional, Callable
from compiler.types import Type, FunType, Int, Bool, Unit
from compiler.symtab import SymTab

Value = Union[Type, Optional[Callable[..., Any]]]


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

            if (isinstance(node.else_, ast.Literal) and node.else_.value is None):
                return Unit

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
            local_symtab = SymTab[Any](parent=symbol_table)
            for expr in node.expressions:
                annotate_types(expr, local_symtab)
            return annotate_types(node.result, local_symtab) if node.result is not None else Unit

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


def build_typechecker_root_symtab() -> SymTab[Value]:
    symtab: SymTab[Value] = SymTab()

    arith_op: Callable = lambda t1, t2: Int if t1 is Int and t2 is Int else Unit
    cmp_op: Callable = lambda t1, t2: Bool if t1 is Int and t2 is Int else Unit
    eq_op: Callable = lambda t1, t2: Bool if t1 is t2 else Unit
    bool_op: Callable = lambda t1, t2: Bool if t1 is Bool and t2 is Bool else Unit

    for op in ["+", "-", "*", "/", "%"]:
        symtab.add_local(op, arith_op)
    for op in ["<", "<=", ">", ">="]:
        symtab.add_local(op, cmp_op)
    for op in ["and", "or"]:
        symtab.add_local(op, bool_op)
    for op in ["==", "!="]:
        symtab.add_local(op, eq_op)

    symtab.add_local("unary_-", lambda t: Int if t is Int else Unit)
    symtab.add_local("unary_not", lambda t: Bool if t is Bool else Unit)
    symtab.add_local("print_int", FunType(return_t=Unit, param_t=[Int]))
    symtab.add_local("print_bool", FunType(return_t=Unit, param_t=[Bool]))
    symtab.add_local("read_int", FunType(return_t=Int, param_t=[Int]))

    return symtab
