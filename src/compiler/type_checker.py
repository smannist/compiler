import compiler.ast as ast
from compiler.types import Type, Int, Bool, Unit
from typing import Optional, Any, Callable

# might be a good idea to switch to a generic later
# very plain and still might need restructure anyway


class SymTab:
    def __init__(self, parent: Optional["SymTab"] = None) -> None:
        self.parent = parent
        self.symbols: dict[str, Type | Callable] = {}

        if parent is None:
            self.symbols.update({
                "+": lambda t1, t2: (
                    Int() if isinstance(t1, Int) and isinstance(t2, Int)
                    else Unit()
                )
            })

    def lookup(self, name: str) -> Any:
        if name in self.symbols:
            return self.symbols[name]
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
            if isinstance(node.value, int):
                return Int()
            if isinstance(node.value, bool):
                return Bool()
            if node.value is None:
                return Unit()
            raise TypeError(f"Unsupported literal type: {node.value}")

        case ast.Identifier():
            return symbol_table.lookup(node.name)

        case ast.LiteralVarDecl():
            symbol_table.set(
                name=node.identifier.name,
                type_val=typeresult(node.initializer, symbol_table),
                local=True
            )
            return Unit()

        case ast.BinaryOp():
            t1 = typeresult(node.left, symbol_table)
            t2 = typeresult(node.right, symbol_table)
            op = symbol_table.lookup(node.op)
            t = op(t1, t2)
            if isinstance(t, Int):
                return t
            raise TypeError(f"Expected an integer got {t}")

        case ast.Statements():
            local_scope = SymTab(parent=symbol_table)
            for expr in node.expressions:
                typeresult(expr, local_scope)
            if node.result is not None:
                return typeresult(node.result, local_scope)
            return Unit()

        case _:
            raise Exception(
                f"Typecheck not implemented for node type: {
                    type(node)}"
            )


def typeresult(node: ast.Expression, symbol_table: SymTab) -> Type:
    t = typecheck(node, symbol_table)
    node.type = t
    return t
