from dataclasses import dataclass
from typing_extensions import Optional, List


@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""


@dataclass
class Literal(Expression):
    """AST node which represents a literal integer or boolean value"""
    value: int | bool


@dataclass
class Identifier(Expression):
    """AST node which represents an identifier"""
    name: str


@dataclass
class BinaryOp(Expression):
    """AST node for a binary operation like `A + B`"""
    left: Expression
    op: str
    right: Expression

@dataclass
class UnaryOp(Expression):
    """AST node which represent a unary operation `- or not`"""
    op: str
    operand: Expression

@dataclass
class IfExpr(Expression):
    """AST node which represents a 'if-then-else' statement"""
    condition: Expression
    then: Expression
    else_: Optional[Expression] = None


@dataclass
class FuncExpr(Expression):
    """AST node which represent a function call"""
    identifier: Identifier
    arguments: List[Expression]
