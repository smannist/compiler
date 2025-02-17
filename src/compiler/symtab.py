import sys
from typing import Optional, Dict, Union, Callable, Any
from compiler.types import Bool, Int, Unit, FunType, Type

InterValue = Union[int, bool, None, Optional[Callable[..., Any]]] # interpreter impl.
TypeValue = Union[Type, Optional[Callable[..., Any]]] # type_checker impl.


class SymTab[T]:
    def __init__(self, parent: Optional["SymTab[T]"] = None) -> None:
        self.parent = parent
        self.symbols: Dict[str, T] = {}
        self.functions: Dict[str, T] = {}

    def add_symbol(self, symbol: str, value: T) -> None:
        """Adds a new symbol in the current scope."""
        self.symbols[symbol] = value

    def add_function(self, name: str, value: T) -> None:
        """Adds a (built-in) function in the current scope."""
        self.functions[name] = value

    def lookup(self, value: str) -> T:
        """Looks up a symbol or a function, searching the current and outer scopes."""
        if value in self.symbols:
            return self.symbols[value]
        if value in self.functions:
            return self.functions[value]
        if self.parent is not None:
            return self.parent.lookup(value)
        raise Exception(f"Symbol or function '{value}' not found.")

    def set(self, symbol: str, value: T, local: bool = False) -> None:
        """Set a symbol's value, optionally only in the current scope."""
        if local or symbol in self.symbols:
            self.symbols[symbol] = value
        elif self.parent is not None:
            self.parent.set(symbol, value)
        else:
            self.symbols[symbol] = value


def build_type_symtab() -> SymTab[TypeValue]:
    symtab: SymTab[TypeValue] = SymTab()

    arith_op: Callable = lambda t1, t2: Int if t1 is Int and t2 is Int else Unit
    cmp_op: Callable = lambda t1, t2: Bool if t1 is Int and t2 is Int else Unit
    eq_op: Callable = lambda t1, t2: Bool if t1 is t2 else Unit
    bool_op: Callable = lambda t1, t2: Bool if t1 is Bool and t2 is Bool else Unit

    for op in ["+", "-", "*", "/", "%"]:
        symtab.add_symbol(op, arith_op)
    for op in ["<", "<=", ">", ">="]:
        symtab.add_symbol(op, cmp_op)
    for op in ["and", "or"]:
        symtab.add_symbol(op, bool_op)

    symtab.add_symbol("==", eq_op)
    symtab.add_symbol("!=", eq_op)
    symtab.add_symbol("unary_-", lambda t: Int if t is Int else Unit)
    symtab.add_symbol("unary_not", lambda t: Bool if t is Bool else Unit)

    symtab.add_function("print_int", FunType(return_t=Unit, param_t=[Int]))
    symtab.add_function("print_bool", FunType(return_t=Unit, param_t=[Bool]))
    symtab.add_function("read_int", FunType(return_t=Unit, param_t=[Int]))

    return symtab


def build_interpreter_symtab() -> SymTab[InterValue]:
    symtab: SymTab[InterValue] = SymTab()

    symtab.add_symbol("unary_-", lambda a: -a)
    symtab.add_symbol("unary_not", lambda a: not a)
    symtab.add_symbol("+", lambda a, b: a + b)
    symtab.add_symbol("-", lambda a, b: a - b)
    symtab.add_symbol("%", lambda a, b: a % b)
    symtab.add_symbol("*", lambda a, b: a * b)
    symtab.add_symbol("/", lambda a, b: a / b)
    symtab.add_symbol("==", lambda a, b: a == b)
    symtab.add_symbol("!=", lambda a, b: a != b)
    symtab.add_symbol("<", lambda a, b: a < b)
    symtab.add_symbol("<=", lambda a, b: a <= b)
    symtab.add_symbol(">", lambda a, b: a > b)
    symtab.add_symbol(">=", lambda a, b: a >= b)
    symtab.add_symbol("False", False)
    symtab.add_symbol("True", True)
    symtab.add_symbol("None", None)

    symtab.add_function("print_int", lambda a: print(a))
    symtab.add_function("print_bool", lambda a: print("true" if a else "false"))
    symtab.add_function("read_int", lambda: int(sys.stdin.readline().strip()))

    return symtab
