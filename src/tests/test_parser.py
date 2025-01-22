import compiler.ast as ast
from compiler.parser import parse, ParsingException, EmptyListExpection
from compiler.tokenizer import tokenize


def test_parse_plus_expression() -> None:
    tokens = tokenize("a + b")
    assert parse(tokens) == [
        ast.BinaryOp(
            left=ast.Identifier(
                name="a"),
            op="+",
            right=ast.Identifier(
                name="b")
        )
    ]


def test_parse_greater_than_expression() -> None:
    tokens = tokenize("a > b")
    assert parse(tokens) == [
        ast.BinaryOp(
            left=ast.Identifier(
                name="a"),
            op=">",
            right=ast.Identifier(
                name="b")
        )
    ]


def test_parse_longer_expression() -> None:
    tokens = tokenize("a + b - c")
    assert parse(tokens) == [
        ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Identifier(name="a"),
                op="+",
                right=ast.Identifier(name="b")
            ),
            op="-",
            right=ast.Identifier(name="c")
        )
    ]


def test_precedence_product_expression() -> None:
    tokens = tokenize("a + b * c")
    assert parse(tokens) == [
        ast.BinaryOp(
            left=ast.Identifier(name="a"),
            op="+",
            right=ast.BinaryOp(
                left=ast.Identifier(name="b"),
                op="*",
                right=ast.Identifier(name="c")
            )
        )
    ]


def test_parse_if_expression() -> None:
    tokens = tokenize("if a then b + c else x * y")
    assert parse(tokens) == [
        ast.IfExpr(
            if_=ast.Identifier(name="a"),
            then=ast.BinaryOp(
                left=ast.Identifier(name="b"),
                op="+",
                right=ast.Identifier(name="c"),
            ),
            else_=ast.BinaryOp(
                left=ast.Identifier(name="x"),
                op="*",
                right=ast.Identifier(name="y"),
            ),
        )
    ]


def test_parse_if_expression_without_else() -> None:
    tokens = tokenize("if a then b + c")
    assert parse(tokens) == [
        ast.IfExpr(
            if_=ast.Identifier(name="a"),
            then=ast.BinaryOp(
                left=ast.Identifier(name="b"),
                op="+",
                right=ast.Identifier(name="c"),
            ),
            else_=None
        )
    ]


def test_parse_if_expression_as_part_of_other_expressions() -> None:
    tokens = tokenize("1 + if true then 2 else 3")
    assert parse(tokens) == [
        ast.BinaryOp(
            left=ast.Literal(value=1),
            op="+",
            right=ast.IfExpr(
                if_=ast.Literal(value=True),
                then=ast.Literal(value=2),
                else_=ast.Literal(value=3)
            )
        )
    ]


def test_nested_if_statements() -> None:
    tokens = tokenize(
        "if true then if false then 1 else 2 else if true then 3 else 4")
    assert parse(tokens) == [
        ast.IfExpr(
            if_=ast.Literal(value=True),
            then=ast.IfExpr(
                if_=ast.Literal(value=False),
                then=ast.Literal(value=1),
                else_=ast.Literal(value=2),
            ),
            else_=ast.IfExpr(
                if_=ast.Literal(value=True),
                then=ast.Literal(value=3),
                else_=ast.Literal(value=4),
            ),
        )
    ]


def test_parse_function_expr() -> None:
    tokens = tokenize("f(x, y + z)")
    assert parse(tokens) == [
        ast.FuncExpr(
            identifier=ast.Identifier(name="f"),
            arguments=[
                ast.Identifier(name="x"),
                ast.BinaryOp(
                    left=ast.Identifier(name="y"),
                    op="+",
                    right=ast.Identifier(name="z")
                )
            ]
        )
    ]


def test_binary_op_should_be_followed_by_int_literal_or_identifier() -> None:
    tokens = tokenize("a + b +")
    try:
        parse(tokens)
    except ParsingException as e:
        assert str(
            e) == f"L(line=1, column=7): expected an integer literal or an identifier"
    else:
        assert False, "Expected Exception was not raised"


def test_empty_token_list_raises_an_error() -> None:
    tokens: list = []
    try:
        parse(tokens)
    except EmptyListExpection as e:
        assert str(e) == "token list must not be empty."
    else:
        assert False, "Expected Exception was not raised"


def test_incorrect_source_code_multiliteral_raises_and_error() -> None:
    tokens = tokenize("a+b c r")
    try:
        parse(tokens)
    except ParsingException as e:
        assert str(
            e) == "L(line=1, column=5): incorrect expression: identifier should be followed by a binary operator or a statement."
    else:
        assert False, "Expected Exception was not raised"

def test_incorrect_source_code_multiop_raises_and_error() -> None:
    tokens = tokenize("a+b + + +")
    try:
        parse(tokens)
    except ParsingException as e:
        assert str(
            e) == "L(line=1, column=7): expected an integer literal or an identifier"
    else:
        assert False, "Expected Exception was not raised"
