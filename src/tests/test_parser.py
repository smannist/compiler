import compiler.ast as ast
from compiler.parser import parse, ParsingException, EmptyListException
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
            condition=ast.Identifier(name="a"),
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
            condition=ast.Identifier(name="a"),
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
                condition=ast.Literal(value=True),
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
            condition=ast.Literal(value=True),
            then=ast.IfExpr(
                condition=ast.Literal(value=False),
                then=ast.Literal(value=1),
                else_=ast.Literal(value=2),
            ),
            else_=ast.IfExpr(
                condition=ast.Literal(value=True),
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


def test_parse_simple_unary_operation() -> None:
    tokens = tokenize("not z")
    assert parse(tokens) == [
        ast.UnaryOp(
            op="not",
            operand=ast.Identifier("z")
        )
    ]


def test_parse_unary_not_expression() -> None:
    tokens = tokenize("if not x then y+z")
    assert parse(tokens) == [
        ast.IfExpr(
            condition=ast.UnaryOp(
                op="not",
                operand=ast.Identifier("x")
            ),
            then=ast.BinaryOp(
                left=ast.Identifier("y"),
                op="+",
                right=ast.Identifier("z")
            ),
            else_=None,
        )
    ]


def test_parse_unary_minus_expression() -> None:
    tokens = tokenize("if -x then y+z")
    assert parse(tokens) == [
        ast.IfExpr(
            condition=ast.UnaryOp(
                op="-",
                operand=ast.Identifier("x")
            ),
            then=ast.BinaryOp(
                left=ast.Identifier("y"),
                op="+",
                right=ast.Identifier("z")
            ),
            else_=None,
        )
    ]


def test_parse_unary_minus_with_parentheses() -> None:
    tokens = tokenize("if -(x+1) then y")
    assert parse(tokens) == [
        ast.IfExpr(
            condition=ast.UnaryOp(
                op="-",
                operand=ast.BinaryOp(
                    left=ast.Identifier(name="x"),
                    op="+",
                    right=ast.Literal(value=1)
                )
            ),
            then=ast.Identifier(name="y"),
            else_=None
        )
    ]


def test_parse_unary_chaining_not_operators() -> None:
    tokens = tokenize("not not x")
    assert parse(tokens) == [
        ast.UnaryOp(
            op="not",
            operand=ast.UnaryOp(
            op="not",
            operand=ast.Identifier("x")
        )
        )
    ]


def test_parse_unary_chaining_minus_operators() -> None:
    tokens = tokenize("--x")
    assert parse(tokens) == [
        ast.UnaryOp(
            op="-",
            operand=ast.UnaryOp(
            op="-",
            operand=ast.Identifier("x")
        )
        )
    ]


def test_parse_assignment_op_right_asso() -> None:
    tokens = tokenize("if x = y+z then z")
    assert parse(tokens) == [
        ast.IfExpr(
            condition=ast.BinaryOp(
                left=ast.Identifier(name="x"),
                op="=",
                right=ast.BinaryOp(
                    left=ast.Identifier(name="y"),
                    op="+",
                    right=ast.Identifier(name="z")
                )
            ),
            then=ast.Identifier(name="z"),
            else_=None
        )
    ]


def test_parse_or_expression() -> None:
    tokens = tokenize("a or b")
    assert parse(tokens) == [
        ast.BinaryOp(
            left=ast.Identifier(name="a"),
            op="or",
            right=ast.Identifier(name="b")
        )
    ]


def test_parse_and_expression() -> None:
    tokens = tokenize("a and b")
    assert parse(tokens) == [
        ast.BinaryOp(
            left=ast.Identifier(name="a"),
            op="and",
            right=ast.Identifier(name="b")
        )
    ]


def test_parse_complex_and_or_expression() -> None:
    tokens = tokenize("a and b or c and d")
    assert parse(tokens) == [
        ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Identifier(name="a"),
                op="and",
                right=ast.Identifier(name="b")
            ),
            op="or",
            right=ast.BinaryOp(
                left=ast.Identifier(name="c"),
                op="and",
                right=ast.Identifier(name="d")
            )
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
    except EmptyListException as e:
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
