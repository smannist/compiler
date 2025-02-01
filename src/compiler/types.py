from dataclasses import dataclass


@dataclass(frozen=True)
class Type:
    pass


@dataclass(frozen=True)
class Int(Type):
    pass


@dataclass(frozen=True)
class Bool(Type):
    pass


@dataclass(frozen=True)
class Unit(Type):
    pass


@dataclass(frozen=True)
class FunType(Type):
    param_t: list[Type]
    return_t: Type
