import compiler.ast as ast
from compiler.parser import parse
from compiler.tokenizer import Token, Location

L = Location(0, 0)


def test_expression_parsed_correctly():
    tokens = [
        Token(loc=L, type="identifier", text="a"),
        Token(loc=L, type="binary_op", text="+"),
        Token(loc=L, type="identifier", text="b")
    ]

    assert parse(tokens) == ast.BinaryOp(
        left=ast.Literal(
            value='a'),
        op='+',
        right=ast.Literal(
            value='b'))
