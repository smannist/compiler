import compiler.ast as ast
from compiler.types import Type, FunType, Int, Bool, Unit
from typing import Optional, Any, Callable


class SymTab:
    def __init__(self, parent: Optional["SymTab"] = None) -> None:
        self.parent = parent
        self.symbols: dict[str, Type | Callable] = {}
        self.functions: dict[str, FunType] = {}

        if parent is None:
            arith_op = lambda t1, t2: Int if t1 is Int and t2 is Int else Unit
            cmp_op = lambda t1, t2: Bool if t1 is Int and t2 is Int else Unit
            eq_op = lambda t1, t2: Bool if t1 is t2 else Unit
            bool_op = lambda t1, t2: Bool if t1 is Bool and t2 is Bool else Unit

            self.symbols.update({
                **{op: arith_op for op in ["+", "-", "*", "/", "%"]},
                **{op: cmp_op for op in ["<", "<=", ">", ">="]},
                **{op: bool_op for op in ["and", "or"]},
                "==": eq_op,
                "!=": eq_op,
                "unary_-": lambda t: Int if t is Int else Unit,
                "unary_not": lambda t: Bool if t is Bool else Unit
            })

            self.functions.update({
                "print_int": FunType(return_t=Unit, param_t=[Int]),
                "print_bool": FunType(return_t=Unit, param_t=[Bool]),
                "read_int": FunType(return_t=Unit, param_t=[Int])
            })

    def lookup(self, name: str) -> Any:
        if name in self.symbols:
            return self.symbols[name]
        if name in self.functions:
            return self.functions[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        raise Exception(f"Symbol '{name}' not found.")

    def set(self, name: str, type_val: Type, local: bool = False) -> None:
        if local or name in self.symbols:
            self.symbols[name] = type_val
        elif self.parent is not None:
            self.parent.set(name, type_val)
        else:
            self.symbols[name] = type_val


def typecheck(node: ast.Expression, symbol_table: SymTab) -> Type:
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
            inferred_type = typeresult(node.initializer, symbol_table)
            if node.type is not Unit and node.type is not inferred_type:
                raise TypeError(
                    f"Type mismatch in declaration of '{node.identifier.name}': "
                    f"declared type {node.type} but initializer has type {inferred_type}"
                )
            symbol_table.set(
                name=node.identifier.name,
                type_val=inferred_type,
                local=True
            )
            return inferred_type if node.as_expression else Unit

        case ast.BinaryOp():
            if node.op == "=":
                if not isinstance(node.left, ast.Identifier):
                    raise TypeError("Left-hand side of assignment must be an identifier")
                declared_type = symbol_table.lookup(node.left.name)
                assigned_type = typeresult(node.right, symbol_table)
                if declared_type is not assigned_type:
                    raise TypeError(
                        f"Assignment type mismatch: variable '{node.left.name}' is {declared_type} "
                        f"but got {assigned_type}"
                    )
                return assigned_type
            else:
                t1 = typeresult(node.left, symbol_table)
                t2 = typeresult(node.right, symbol_table)
                op = symbol_table.lookup(node.op)
                result = op(t1, t2)
                if result is Unit:
                    raise TypeError(f"Invalid types for binary operation '{node.op}'")
                return result

        case ast.UnaryOp():
            operand_type = typeresult(node.operand, symbol_table)
            op = symbol_table.lookup("unary_" + node.op)
            result_type = op(operand_type)
            if result_type is Unit:
                raise TypeError(
                    f"Unary operator '{node.op}' is not defined for type {operand_type}"
                )
            return result_type

        case ast.IfExpr():
            cond_type = typeresult(node.condition, symbol_table)
            if cond_type is not Bool:
                raise TypeError("Condition of if must be a boolean")
            then_type = typeresult(node.then, symbol_table)
            else_type = typeresult(node.else_, symbol_table)
            if then_type is not else_type:
                raise TypeError(
                    "Both branches of if-then-else must have the same type"
                    )
            return then_type

        case ast.WhileExpr():
            cond_type = typeresult(node.condition, symbol_table)
            if cond_type is not Bool:
                raise TypeError("Condition of while must be a boolean")
            typeresult(node.body, symbol_table)
            return Unit

        case ast.FuncExpr():
            fun = symbol_table.lookup(node.identifier.name)
            if not isinstance(fun, FunType):
                raise TypeError(f"{node.identifier.name} is not a function")
            for arg, expected in zip(node.arguments, fun.param_t):
                actual = typeresult(arg, symbol_table)
                if actual is not expected:
                    raise TypeError(
                        f"In function {node.identifier.name}: expected argument type "
                        f"{expected} but got {actual}"
                    )
            return fun.return_t

        case ast.Statements():
            local_scope = SymTab(parent=symbol_table)
            for expr in node.expressions:
                typeresult(expr, local_scope)
            return typeresult(node.result,
                              local_scope) if node.result is not None else Unit

        case _:
            raise Exception(
                f"Typecheck not implemented for node type: {type(node)}"
            )


def typeresult(node: ast.Expression | None, symbol_table: SymTab) -> Type:
    if node is None:
        return Unit
    t = typecheck(node, symbol_table)
    node.type = t
    return t
