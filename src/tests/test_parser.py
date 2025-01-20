import compiler.ast as ast
from compiler.parser import parse
from compiler.tokenizer import Token, Location

L = Location(0, 0)


def test_parse_simple_expression() -> None:
    tokens = [
        Token(loc=L, type="identifier", text="a"),
        Token(loc=L, type="binary_op", text="+"),
        Token(loc=L, type="identifier", text="b")
    ]

    assert parse(tokens) == [
        ast.BinaryOp(
            left=ast.Identifier(
                name="a"),
            op="+",
            right=ast.Identifier(
                name="b")
        )
    ]

def test_parse_longer_expression() -> None:
    tokens = [
        Token(loc=L, type="identifier", text="a"),
        Token(loc=L, type="binary_op", text="+"),
        Token(loc=L, type="identifier", text="b"),
        Token(loc=L, type="identifier", text="-"),
        Token(loc=L, type="identifier", text="c")
    ]

    assert parse(tokens) == [
        ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Identifier(name='a'),
                op='+',
                right=ast.Identifier(name='b')
            ),
            op='-',
            right=ast.Identifier(name='c')
        )
]

def test_binary_op_should_be_followed_by_int_literal_or_identifier() -> None:
    tokens = [
        Token(loc=L, type="identifier", text="a"),
        Token(loc=L, type="binary_op", text="+"),
        Token(loc=L, type="identifier", text="b"),
        Token(loc=L, type="binary_op", text="+")
    ]
    try:
        parse(tokens)
    except Exception as e:
        assert str(e) == f"{L.__str__()}: expected an integer literal or an identifier"
    else:
        assert False, "Expected Exception was not raised"

def test_empty_token_list_raises_an_error() -> None:
    tokens = []
    try:
        parse(tokens)
    except Exception as e:
        assert str(e) == "token list must not be empty."
    else:
        assert False, "Expected Exception was not raised"

def test_incorrect_source_code_raises_and_error() -> None:
    tokens = [
        Token(loc=L, type="identifier", text="a"),
        Token(loc=L, type="binary_op", text="+"),
        Token(loc=L, type="identifier", text="b"),
        Token(loc=L, type="identifier", text="c"),
        Token(loc=L, type="identifier", text="r")
    ]
    try:
        parse(tokens)
    except Exception as e:
        assert str(e) == "incorrect expression."
    else:
        assert False, "Expected Exception was not raised"
