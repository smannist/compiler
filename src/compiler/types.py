from dataclasses import dataclass, field


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
    return_t: Type
    param_t: list[Type] = field(default_factory=list)


Int = IntType()
Bool = BoolType()
Unit = UnitType()
