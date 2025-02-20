import sys
from typing import Optional, Dict, Union, Callable, Any
from compiler.types import Bool, Int, Unit, FunType, Type


class SymTab[T]:
    def __init__(self, parent: Optional["SymTab[T]"] = None) -> None:
        self.parent = parent
        self.symbols: Dict[str, T] = {}

    def add_local(self, symbol: str, value: T) -> None:
        """Adds a new symbol in the current scope."""
        self.symbols[symbol] = value

    def get_local(self, name: str) -> T | None:
        """Returns a symbol if it already exists in the scope."""
        return self.symbols.get(name)

    def lookup(self, value: str) -> T:
        """Looks up a symbol or a function, searching the current and outer scopes."""
        if value in self.symbols:
            return self.symbols[value]
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
