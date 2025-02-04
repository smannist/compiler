from dataclasses import dataclass


@dataclass(frozen=True)
class Type:
    pass


@dataclass(frozen=True)
class IntType(Type):
    pass


@dataclass(frozen=True)
class BoolType(Type):
    pass


@dataclass(frozen=True)
class UnitType(Type):
    pass


@dataclass(frozen=True)
class FunType(Type):
    param_t: list[Type]
    return_t: Type


Int = IntType()
Bool = BoolType()
Unit = UnitType()
