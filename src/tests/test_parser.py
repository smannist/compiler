import compiler.ast as ast
from compiler.parser import parse, ParsingException, EmptyListException
from compiler.tokenizer import tokenize, Location


def test_parse_plus_expression() -> None:
    tokens = tokenize("a + b")
    assert parse(tokens) == ast.BinaryOp(
            left=ast.Identifier(
                name="a",
                location=Location(line=0, column=0)),
            op="+",
            right=ast.Identifier(
                name="b",
                location=Location(line=0, column=0)
            ),
            location=Location(line=0, column=0)
        )


def test_parse_greater_than_expression() -> None:
    tokens = tokenize("a > b")
    assert parse(tokens) == ast.BinaryOp(
            left=ast.Identifier(
                name="a",
                location=Location(line=0, column=0)),
            op=">",
            right=ast.Identifier(
                name="b",
                location=Location(line=0, column=0)),
            location=Location(line=0, column=0)
        )
    


def test_parse_longer_expression() -> None:
    tokens = tokenize("a + b - c")
    assert parse(tokens) == ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Identifier(
                    name="a",
                    location=Location(line=0, column=0)
                ),
                op="+",
                right=ast.Identifier(
                    name="b",
                    location=Location(line=0, column=0)
                ),
                location=Location(line=0, column=0)
            ),
            op="-",
            right=ast.Identifier(
                name="c",
                location=Location(line=0, column=0)
            ),
            location=Location(line=0, column=0)
        )
    


def test_precedence_product_expression() -> None:
    tokens = tokenize("a + b * c")
    assert parse(tokens) == ast.BinaryOp(
            left=ast.Identifier(
                name="a",
                location=Location(line=0, column=0)
            ),
            op="+",
            right=ast.BinaryOp(
                left=ast.Identifier(
                    name="b",
                    location=Location(line=0, column=0)
                ),
                op="*",
                right=ast.Identifier(
                    name="c",
                    location=Location(line=0, column=0)
                ),
                location=Location(line=0, column=0)
            ),
            location=Location(line=0, column=0)
        )



def test_parse_if_expression() -> None:
    tokens = tokenize("if a then b + c else x * y")
    assert parse(tokens) == ast.IfExpr(
            condition=ast.Identifier(name="a", location=Location(line=0, column=0)),
            then=ast.BinaryOp(
                left=ast.Identifier(name="b", location=Location(line=0, column=0)),
                op="+",
                right=ast.Identifier(name="c", location=Location(line=0, column=0)),
                location=Location(line=0, column=0)
            ),
            else_=ast.BinaryOp(
                left=ast.Identifier(name="x", location=Location(line=0, column=0)),
                op="*",
                right=ast.Identifier(name="y", location=Location(line=0, column=0)),
                location=Location(line=0, column=0)
            ),
            location=Location(line=0, column=0)
        )
    


def test_parse_if_expression_without_else() -> None:
    tokens = tokenize("if a then b + c")
    assert parse(tokens) == ast.IfExpr(
            condition=ast.Identifier(
                name="a",
                location=Location(
                    line=1,
                    column=4)),
            then=ast.BinaryOp(
                left=ast.Identifier(
                    name="b",
                    location=Location(
                        line=1,
                        column=11)),
                op="+",
                right=ast.Identifier(
                    name="c",
                    location=Location(
                        line=1,
                        column=15)),
                location=Location(
                    line=1,
                    column=13)),
            else_=ast.Literal(
                value=None,
                location=None),
            location=Location(
                line=1,
                column=6))


def test_parse_if_expression_as_part_of_other_expressions() -> None:
    tokens = tokenize("1 + if true then 2 else 3")
    assert parse(tokens) == ast.BinaryOp(
            left=ast.Literal(
                value=1,
                location=Location(line=0, column=0)
            ),
            op="+",
            right=ast.IfExpr(
                condition=ast.Literal(
                    value=True,
                    location=Location(line=0, column=0)
                ),
                then=ast.Literal(
                    value=2,
                    location=Location(line=0, column=0)
                ),
                else_=ast.Literal(
                    value=3,
                    location=Location(line=0, column=0)
                ),
                location=Location(line=0, column=0)
            ),
            location=Location(line=0, column=0)
        )


def test_nested_if_statements() -> None:
    tokens = tokenize(
        "if true then if false then 1 else 2 else if true then 3 else 4"
    )
    assert parse(tokens) == ast.IfExpr(
            condition=ast.Literal(
                value=True,
                location=Location(line=0, column=0)
            ),
            then=ast.IfExpr(
                condition=ast.Literal(
                    value=False,
                    location=Location(line=0, column=0)
                ),
                then=ast.Literal(
                    value=1,
                    location=Location(line=0, column=0)
                ),
                else_=ast.Literal(
                    value=2,
                    location=Location(line=0, column=0)
                ),
                location=Location(line=0, column=0)
            ),
            else_=ast.IfExpr(
                condition=ast.Literal(
                    value=True,
                    location=Location(line=0, column=0)
                ),
                then=ast.Literal(
                    value=3,
                    location=Location(line=0, column=0)
                ),
                else_=ast.Literal(
                    value=4,
                    location=Location(line=0, column=0)
                ),
                location=Location(line=0, column=0)
            ),
            location=Location(line=0, column=0)
        )



def test_parse_if_expression_with_assignment_semicolon() -> None:
    tokens = tokenize("if x > y then { z = 1; };")
    assert parse(tokens) == ast.Statements(
            expressions=[
                ast.IfExpr(
                    condition=ast.BinaryOp(
                        left=ast.Identifier(
                            name="x",
                            location=Location(line=1, column=4)
                        ),
                        op=">",
                        right=ast.Identifier(
                            name="y",
                            location=Location(line=1, column=8)
                        ),
                        location=Location(line=1, column=6)
                    ),
                    then=ast.Statements(
                        expressions=[
                            ast.BinaryOp(
                                left=ast.Identifier(
                                    name="z",
                                    location=Location(line=1, column=17)
                                ),
                                op="=",
                                right=ast.Literal(
                                    value=1,
                                    location=Location(line=1, column=21)
                                ),
                                location=Location(line=1, column=19)
                            )
                        ],
                        result=ast.Literal(
                            value=None,
                            location=None
                        ),
                        location=Location(line=1, column=24)
                    ),
                    else_=ast.Literal(
                        value=None,
                        location=None
                    ),
                    location=Location(line=1, column=10)
                )
            ],
            result=ast.Literal(
                value=None,
                location=None
            ),
            location=Location(line=1, column=25)
        )


def test_parse_if_expression_with_assignment_no_semicolon() -> None:
    tokens = tokenize("if x > y then { z = 1; }")
    assert parse(tokens) == ast.IfExpr(
            condition=ast.BinaryOp(
                left=ast.Identifier(
                    name="x",
                    location=Location(line=1, column=4)
                ),
                op=">",
                right=ast.Identifier(
                    name="y",
                    location=Location(line=1, column=8)
                ),
                location=Location(line=1, column=6)
            ),
            then=ast.Statements(
                expressions=[
                    ast.BinaryOp(
                        left=ast.Identifier(
                            name="z",
                            location=Location(line=1, column=17)
                        ),
                        op="=",
                        right=ast.Literal(
                            value=1,
                            location=Location(line=1, column=21)
                        ),
                        location=Location(line=1, column=19)
                    )
                ],
                result=ast.Literal(
                    value=None,
                    location=None
                ),
                location=Location(line=1, column=24)
            ),
            else_=ast.Literal(
                value=None,
                location=None
            ),
            location=Location(line=1, column=10)
        )


def test_parse_function_expr() -> None:
    tokens = tokenize("f(x, y + z)")
    assert parse(tokens) == ast.FuncExpr(
            identifier=ast.Identifier(
                name="f",
                location=Location(line=0, column=0)
            ),
            arguments=[
                ast.Identifier(
                    name="x",
                    location=Location(line=0, column=0)
                ),
                ast.BinaryOp(
                    left=ast.Identifier(
                        name="y",
                        location=Location(line=0, column=0)
                    ),
                    op="+",
                    right=ast.Identifier(
                        name="z",
                        location=Location(line=0, column=0)
                    ),
                    location=Location(line=0, column=0)
                )
            ],
            location=Location(line=0, column=0)
        )


def test_parse_simple_unary_operation() -> None:
    tokens = tokenize("not z")
    assert parse(tokens) == ast.UnaryOp(
            op="not", operand=ast.Identifier(
                name="z", location=Location(
                    line=0, column=0)), location=Location(
                line=0, column=0))


def test_parse_unary_not_expression() -> None:
    tokens = tokenize("if not x then y+z")
    assert parse(tokens) == ast.IfExpr(
            condition=ast.UnaryOp(
                op="not",
                operand=ast.Identifier(name="x", location=Location(line=1, column=5)),
                location=Location(line=1, column=4)
            ),
            then=ast.BinaryOp(
                left=ast.Identifier(name="y", location=Location(line=1, column=12)),
                op="+",
                right=ast.Identifier(name="z", location=Location(line=1, column=14)),
                location=Location(line=1, column=13)
            ),
            else_=ast.Literal(value=None, location=None),
            location=Location(line=1, column=7)
        )


def test_parse_unary_minus_expression() -> None:
    tokens = tokenize("if -x then y+z")
    assert parse(tokens) == ast.IfExpr(
            condition=ast.UnaryOp(
                op="-",
                operand=ast.Identifier(
                    name="x",
                    location=Location(line=1, column=5)
                ),
                location=Location(line=1, column=4)
            ),
            then=ast.BinaryOp(
                left=ast.Identifier(
                    name="y",
                    location=Location(line=1, column=12)
                ),
                op="+",
                right=ast.Identifier(
                    name="z",
                    location=Location(line=1, column=14)
                ),
                location=Location(line=1, column=13)
            ),
            else_=ast.Literal(
                value=None,
                location=None
            ),
            location=Location(line=1, column=7)
        )


def test_parse_sum_with_unary() -> None:
    tokens = tokenize("-2 + 3")
    assert parse(tokens) == ast.BinaryOp(
        location=Location(line=1, column=4),
        left=ast.UnaryOp(
            location=Location(line=1, column=1),
            op="-",
            operand=ast.Literal(
                location=Location(line=1, column=2),
                value=2
            )
        ),
        op="+",
        right=ast.Literal(
            location=Location(line=1, column=6),
            value=3
        )
    )


def test_parse_subtraction_with_unaries() -> None:
    tokens = tokenize("-2--4")
    assert parse(tokens) == ast.BinaryOp(
        location=Location(line=1, column=4),
        left=ast.UnaryOp(
            location=Location(line=1, column=1),
            op="-",
            operand=ast.Literal(
                location=Location(line=1, column=2),
                value=2
            )
        ),
        op="-",
        right=ast.UnaryOp(
            location=Location(line=1, column=5),
            op="-",
            operand=ast.Literal(
                location=Location(line=1, column=6),
                value=4
            )
        )
    )


def test_parse_unary_minus_with_parentheses() -> None:
    tokens = tokenize("if -(x+1) then y")
    assert parse(tokens) == ast.IfExpr(
            condition=ast.UnaryOp(
                op="-",
                operand=ast.BinaryOp(
                    left=ast.Identifier(
                        name="x",
                        location=Location(line=1, column=4)
                    ),
                    op="+",
                    right=ast.Literal(
                        value=1,
                        location=Location(line=0, column=0)
                    ),
                    location=Location(line=1, column=6)
                ),
                location=Location(line=0, column=0)
            ),
            then=ast.Identifier(
                name="y",
                location=Location(line=0, column=0)
            ),
            else_=ast.Literal(
                value=None,
                location=None
            ),
            location=Location(line=1, column=12)
        )


def test_parse_unary_chaining_not_operators() -> None:
    tokens = tokenize("not not x")
    assert parse(tokens) == ast.UnaryOp(
            op="not", operand=ast.UnaryOp(
                op="not", operand=ast.Identifier(
                    name="x", location=Location(
                        line=0, column=0)), location=Location(
                    line=0, column=0)), location=Location(
                line=0, column=0))


def test_parse_unary_chaining_minus_operators() -> None:
    tokens = tokenize("--x")
    assert parse(tokens) == ast.UnaryOp(
            op="-",
            operand=ast.UnaryOp(
                op="-",
                operand=ast.Identifier(
                    name="x",
                    location=Location(
                        line=0,
                        column=0)),
                location=Location(
                    line=0,
                    column=0)),
            location=Location(
                line=0,
                column=0))


def test_parse_assignment_op_right_asso() -> None:
    tokens = tokenize("if x = y+z then z")
    assert parse(tokens) == ast.IfExpr(
            condition=ast.BinaryOp(
                left=ast.Identifier(name="x", location=Location(line=1, column=4)),
                op="=",
                right=ast.BinaryOp(
                    left=ast.Identifier(name="y", location=Location(line=1, column=8)),
                    op="+",
                    right=ast.Identifier(name="z", location=Location(line=1, column=10)),
                    location=Location(line=1, column=9)
                ),
                location=Location(line=1, column=6)
            ),
            then=ast.Identifier(name="z", location=Location(line=1, column=17)),
            else_=ast.Literal(value=None, location=None),
            location=Location(line=1, column=12)
        )


def test_parse_or_expression() -> None:
    tokens = tokenize("a or b")
    assert parse(tokens) == ast.BinaryOp(
            left=ast.Identifier(
                name="a",
                location=Location(line=0, column=0)
            ),
            op="or",
            right=ast.Identifier(
                name="b",
                location=Location(line=0, column=0)
            ),
            location=Location(line=0, column=0)
        )


def test_parse_and_expression() -> None:
    tokens = tokenize("a and b")
    assert parse(tokens) == ast.BinaryOp(
            left=ast.Identifier(
                name="a",
                location=Location(line=0, column=0)
            ),
            op="and",
            right=ast.Identifier(
                name="b",
                location=Location(line=0, column=0)
            ),
            location=Location(line=0, column=0)
        )


def test_parse_complex_and_or_expression() -> None:
    tokens = tokenize("a and b or c and d")
    assert parse(tokens) == ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Identifier(name="a", location=Location(line=0, column=0)),
                op="and",
                right=ast.Identifier(name="b", location=Location(line=0, column=0)),
                location=Location(line=0, column=0)
            ),
            op="or",
            right=ast.BinaryOp(
                left=ast.Identifier(name="c", location=Location(line=0, column=0)),
                op="and",
                right=ast.Identifier(name="d", location=Location(line=0, column=0)),
                location=Location(line=0, column=0)
            ),
            location=Location(line=0, column=0)
        )


def test_parse_simple_statement_without_final_semicolon() -> None:
    source_code = """{
        f(a);
        x = y;
        f(x)
    }
    """
    tokens = tokenize(source_code)
    assert parse(tokens) == ast.Statements(
            expressions=[
                ast.FuncExpr(
                    identifier=ast.Identifier(name="f", location=Location(line=0, column=0)),
                    arguments=[
                        ast.Identifier(name="a", location=Location(line=0, column=0))
                    ],
                    location=Location(line=0, column=0)
                ),
                ast.BinaryOp(
                    left=ast.Identifier(name="x", location=Location(line=0, column=0)),
                    op="=",
                    right=ast.Identifier(name="y", location=Location(line=0, column=0)),
                    location=Location(line=0, column=0)
                )
            ],
            result=ast.FuncExpr(
                identifier=ast.Identifier(name="f", location=Location(line=0, column=0)),
                arguments=[
                    ast.Identifier(name="x", location=Location(line=0, column=0))
                ],
                location=Location(line=0, column=0)
            ),
            location=Location(line=0, column=0)
        )


def test_parse_simple_statement_with_final_semicolon() -> None:
    source_code = """{
        f(a);
        x = y;
        f(x);
    }
    """
    tokens = tokenize(source_code)
    assert parse(tokens) == ast.Statements(
            expressions=[
                ast.FuncExpr(
                    identifier=ast.Identifier(name="f", location=Location(line=0, column=0)),
                    arguments=[
                        ast.Identifier(name="a", location=Location(line=0, column=0))
                    ],
                    location=Location(line=0, column=0)
                ),
                ast.BinaryOp(
                    left=ast.Identifier(name="x", location=Location(line=0, column=0)),
                    op="=",
                    right=ast.Identifier(name="y", location=Location(line=0, column=0)),
                    location=Location(line=0, column=0)
                ),
                ast.FuncExpr(
                    identifier=ast.Identifier(name="f", location=Location(line=0, column=0)),
                    arguments=[
                        ast.Identifier(name="x", location=Location(line=0, column=0))
                    ],
                    location=Location(line=0, column=0)
                )
            ],
            result=ast.Literal(value=None, location=None),
            location=Location(line=3, column=6)
        )


def test_parse_simple_while_expr() -> None:
    source_code = """while y > x do {
        x = x + 1;
    };
    """
    tokens = tokenize(source_code)
    assert parse(tokens) == ast.Statements(
            expressions=[
                ast.WhileExpr(
                    condition=ast.BinaryOp(
                        left=ast.Identifier(name="y", location=Location(line=1, column=7)),
                        op=">",
                        right=ast.Identifier(name="x", location=Location(line=1, column=11)),
                        location=Location(line=1, column=9)
                    ),
                    body=ast.Statements(
                        expressions=[
                            ast.BinaryOp(
                                left=ast.Identifier(name="x", location=Location(line=2, column=9)),
                                op="=",
                                right=ast.BinaryOp(
                                    left=ast.Identifier(name="x", location=Location(line=2, column=13)),
                                    op="+",
                                    right=ast.Literal(value=1, location=Location(line=2, column=17)),
                                    location=Location(line=2, column=15)
                                ),
                                location=Location(line=2, column=11)
                            )
                        ],
                        result=ast.Literal(value=None, location=None),
                        location=Location(line=3, column=5)
                    ),
                    location=Location(line=1, column=13)
                ),
            ],
            result=ast.Literal(value=None, location=None),
            location=Location(line=3, column=6)
        )


def test_parse_nested_while_with_if_and_statements() -> None:
    source_code = """{ while f() do {
        x = 10;
        y = if g(x) then {
            x = x + 1;
            x
        } else {
            g(x)
        };
            g(y);
        };
        123
    }"""
    tokens = tokenize(source_code)
    assert parse(tokens) == ast.Statements(
            expressions=[
                ast.WhileExpr(
                    condition=ast.FuncExpr(
                        identifier=ast.Identifier(name="f", location=Location(line=1, column=9)),
                        arguments=[],
                        location=Location(line=1, column=9)
                    ),
                    body=ast.Statements(
                        expressions=[
                            ast.BinaryOp(
                                left=ast.Identifier(name="x", location=Location(line=2, column=9)),
                                op="=",
                                right=ast.Literal(value=10, location=Location(line=2, column=13)),
                                location=Location(line=2, column=11)
                            ),
                            ast.BinaryOp(
                                left=ast.Identifier(name="y", location=Location(line=3, column=9)),
                                op="=",
                                right=ast.IfExpr(
                                    condition=ast.FuncExpr(
                                        identifier=ast.Identifier(name="g", location=Location(line=3, column=16)),
                                        arguments=[ast.Identifier(name="x", location=Location(line=3, column=18))],
                                        location=Location(line=3, column=16)
                                    ),
                                    then=ast.Statements(
                                        expressions=[
                                            ast.BinaryOp(
                                                left=ast.Identifier(name="x", location=Location(line=4, column=13)),
                                                op="=",
                                                right=ast.BinaryOp(
                                                    left=ast.Identifier(name="x", location=Location(line=4, column=17)),
                                                    op="+",
                                                    right=ast.Literal(value=1, location=Location(line=4, column=21)),
                                                    location=Location(line=4, column=19)
                                                ),
                                                location=Location(line=4, column=15)
                                            )
                                        ],
                                        result=ast.Identifier(name="x", location=Location(line=5, column=13)),
                                        location=Location(line=6, column=11)
                                    ),
                                    else_=ast.Statements(
                                        expressions=[],
                                        result=ast.FuncExpr(
                                            identifier=ast.Identifier(name="g", location=Location(line=7, column=13)),
                                            arguments=[ast.Identifier(name="x", location=Location(line=7, column=15))],
                                            location=Location(line=7, column=13)
                                        ),
                                        location=Location(line=8, column=9)
                                    ),
                                    location=Location(line=6, column=9)
                                ),
                                location=Location(line=10, column=9)
                            ),
                            ast.FuncExpr(
                                identifier=ast.Identifier(name="g", location=Location(line=9, column=13)),
                                arguments=[ast.Identifier(name="y", location=Location(line=9, column=15))],
                                location=Location(line=9, column=13)
                            )
                        ],
                        result=ast.Literal(value=None, location=None),
                        location=Location(line=3, column=11)
                    ),
                    location=Location(line=1, column=12)
                ),
            ],
            result=ast.Literal(value=123, location=Location(line=11, column=9)),
            location=Location(line=1, column=5)
        )


def test_parse_variable_decl() -> None:
    tokens = tokenize("var x = 123; var y = 200;")
    assert (parse(tokens)) == ast.Statements(
            expressions=[
                ast.LiteralVarDecl(
                    identifier=ast.Identifier(name="x", location=Location(line=1, column=5)),
                    initializer=ast.Literal(value=123, location=Location(line=1, column=9)),
                    location=Location(line=1, column=12)
                ),
                ast.LiteralVarDecl(
                    identifier=ast.Identifier(name="y", location=Location(line=0, column=0)),
                    initializer=ast.Literal(value=200, location=Location(line=0, column=0)),
                    location=Location(line=1, column=25)
                )
            ],
            result=ast.Literal(value=None, location=None),
            location=Location(line=1, column=25)
        )


def test_parse_variable_decl_at_top_level_semi() -> None:
    source_code = """
    var x = 123;
    var y = 200;
    while x > y do {
        x = x + 1;
    };
    """
    tokens = tokenize(source_code)
    assert parse(tokens) == ast.Statements(
            expressions=[
                ast.LiteralVarDecl(
                    identifier=ast.Identifier(name="x", location=Location(line=2, column=9)),
                    initializer=ast.Literal(value=123, location=Location(line=2, column=13)),
                    location=Location(line=2, column=16)
                ),
                ast.LiteralVarDecl(
                    identifier=ast.Identifier(name="y", location=Location(line=3, column=9)),
                    initializer=ast.Literal(value=200, location=Location(line=3, column=13)),
                    location=Location(line=3, column=16)
                ),
                ast.WhileExpr(
                    condition=ast.BinaryOp(
                        left=ast.Identifier(name="x", location=Location(line=4, column=11)),
                        op=">",
                        right=ast.Identifier(name="y", location=Location(line=4, column=15)),
                        location=Location(line=4, column=13)
                    ),
                    body=ast.Statements(
                        expressions=[
                            ast.BinaryOp(
                                left=ast.Identifier(name="x", location=Location(line=5, column=9)),
                                op="=",
                                right=ast.BinaryOp(
                                    left=ast.Identifier(name="x", location=Location(line=5, column=13)),
                                    op="+",
                                    right=ast.Literal(value=1, location=Location(line=5, column=17)),
                                    location=Location(line=5, column=15)
                                ),
                                location=Location(line=5, column=11)
                            )
                        ],
                        result=ast.Literal(value=None, location=None),
                        location=Location(line=0, column=0)
                    ),
                    location=Location(line=4, column=17)
                )
            ],
            result=ast.Literal(value=None, location=None),
            location=Location(line=6, column=6)
        )


def test_parse_nested_statements_with_variable_decls() -> None:
    source_code = """
    var x = 2;
    {
        var x = 1;
        print_int(x);
    }
    print_int(x);
    """
    tokens = tokenize(source_code)
    assert parse(tokens) == ast.Statements(
        expressions=[
            ast.LiteralVarDecl(
                identifier=ast.Identifier(name="x", location=Location(line=2, column=9)),
                initializer=ast.Literal(value=2, location=Location(line=2, column=13)),
                location=Location(line=2, column=16)
            ),
            ast.Statements(
                expressions=[
                    ast.LiteralVarDecl(
                        identifier=ast.Identifier(name="x", location=Location(line=3, column=13)),
                        initializer=ast.Literal(value=1, location=Location(line=3, column=17)),
                        location=Location(line=3, column=20)
                    ),
                    ast.FuncExpr(
                        identifier=ast.Identifier(name="print_int", location=Location(line=4, column=13)),
                        arguments=[ast.Identifier(name="x", location=Location(line=4, column=23))],
                        location=Location(line=4, column=13)
                    )
                ],
                result=ast.Literal(value=None, location=None),
                location=Location(line=5, column=6)
            ),
            ast.FuncExpr(
                identifier=ast.Identifier(name="print_int", location=Location(line=6, column=9)),
                arguments=[ast.Identifier(name="x", location=Location(line=6, column=19))],
                location=Location(line=6, column=9)
            )
        ],
        result=ast.Literal(value=None, location=None),
        location=Location(line=7, column=6)
    )


def test_parse_while_block_with_vars_inside_no_semi_result_expr() -> None:
    tokens = tokenize("""
        while x > y do {
            var x = 123;
            var y = 200;
            x = x + 1
        }
    """)
    assert parse(tokens) == ast.WhileExpr(
            condition=ast.BinaryOp(
                left=ast.Identifier(name="x", location=Location(line=0, column=0)),
                op=">",
                right=ast.Identifier(name="y", location=Location(line=0, column=0)),
                location=Location(line=0, column=0)
            ),
            body=ast.Statements(
                expressions=[
                    ast.LiteralVarDecl(
                        identifier=ast.Identifier(name="x", location=Location(line=0, column=0)),
                        initializer=ast.Literal(value=123, location=Location(line=0, column=0)),
                        location=Location(line=0, column=0)
                    ),
                    ast.LiteralVarDecl(
                        identifier=ast.Identifier(name="y", location=Location(line=0, column=0)),
                        initializer=ast.Literal(value=200, location=Location(line=0, column=0)),
                        location=Location(line=0, column=0)
                    )
                ],
                result=ast.BinaryOp(
                    left=ast.Identifier(name="x", location=Location(line=0, column=0)),
                    op="=",
                    right=ast.BinaryOp(
                        left=ast.Identifier(name="x", location=Location(line=0, column=0)),
                        op="+",
                        right=ast.Literal(value=1, location=Location(line=0, column=0)),
                        location=Location(line=0, column=0)
                    ),
                    location=Location(line=0, column=0)
                ),
                location=Location(line=0, column=0)
            ),
            location=Location(line=0, column=0)
        )


def test_parse_nested_blocks_result_block_iden() -> None:
    source_code = """{
        { a }
        { b }
    }"""

    tokens = tokenize(source_code)
    assert parse(tokens) == ast.Statements(
        expressions=[
            ast.Statements(
                expressions=[],
                result=ast.Identifier(
                    name="a",
                    location=Location(line=0, column=0)
                ),
                location=Location(line=0, column=0)
            )
        ],
        result=ast.Statements(
            expressions=[],
            result=ast.Identifier(
                name="b",
                location=Location(line=0, column=0)
            ),
            location=Location(line=0, column=0)
        ),
        location=Location(line=0, column=0)
    )


def test_parse_if_expr_with_block_then_no_semi_inside_curl_then() -> None:
    tokens = tokenize("{ if true then { a } b }")
    assert parse(tokens) == ast.Statements(
            expressions=[
                ast.IfExpr(
                    condition=ast.Literal(value=True, location=Location(line=1, column=6)),
                    then=ast.Statements(
                        expressions=[],
                        result=ast.Identifier(name="a", location=Location(line=1, column=18)),
                        location=Location(line=1, column=20)
                    ),
                    else_=ast.Literal(value=None, location=None),
                    location=Location(line=1, column=11)
                )
            ],
            result=ast.Identifier(name="b", location=Location(line=1, column=22)),
            location=Location(line=1, column=24)
        )


def test_parse_if_expr_with_block_then_semi_inside_curl_then_1() -> None:
    tokens = tokenize("{ if true then { a }; b }")
    assert parse(tokens) == ast.Statements(
            expressions=[
                ast.IfExpr(
                    condition=ast.Literal(value=True, location=Location(line=0, column=0)),
                    then=ast.Statements(
                        expressions=[],
                        result=ast.Identifier(name="a", location=Location(line=0, column=0)),
                        location=Location(line=0, column=0)
                    ),
                    else_=ast.Literal(value=None, location=None),
                    location=Location(line=0, column=0)
                )
            ],
            result=ast.Identifier(name="b", location=Location(line=0, column=0)),
            location=Location(line=0, column=0)
        )

def test_parse_if_expr_with_block_then_semi_inside_curl_then_2() -> None:
    tokens = tokenize("{ if true then { a } b; c }")
    assert parse(tokens) == ast.Statements(
            expressions=[
                ast.IfExpr(
                    condition=ast.Literal(
                        value=True, location=Location(
                            line=1, column=6)),
                    then=ast.Statements(
                        expressions=[],
                        result=ast.Identifier(
                            name="a", location=Location(
                                line=1, column=18)),
                        location=Location(line=1, column=20)
                    ),
                    else_=ast.Literal(
                        value=None, location=None),
                    location=Location(line=1, column=11)
                ),
                ast.Identifier(name="b", location=Location(line=1, column=22)),
            ],
            result=ast.Identifier(
                name="c", location=Location(
                    line=1, column=25)),
            location=Location(line=1, column=27)
        )


def test_parse_if_expr_with_block_then_semi_inside_curl_then_else() -> None:
    tokens = tokenize("{ if true then { a } else { b } c }")
    assert parse(tokens) == ast.Statements(
            expressions=[
                ast.IfExpr(
                    condition=ast.Literal(value=True, location=Location(line=0, column=0)),
                    then=ast.Statements(
                        expressions=[],
                        result=ast.Identifier(name="a", location=Location(line=0, column=0)),
                        location=Location(line=0, column=0)
                    ),
                    else_=ast.Statements(
                        expressions=[],
                        result=ast.Identifier(name="b", location=Location(line=0, column=0)),
                        location=Location(line=0, column=0)
                    ),
                    location=Location(line=0, column=0)
                )
            ],
            result=ast.Identifier(name="c", location=Location(line=0, column=0)),
            location=Location(line=0, column=0)
        )


def test_parse_curly_declaration() -> None:
    tokens = tokenize("x = { { f(a) } { b } }")
    assert parse(tokens) == ast.BinaryOp(
            left=ast.Identifier(name="x", location=Location(line=1, column=1)),
            op="=",
            right=ast.Statements(
                expressions=[
                    ast.Statements(
                        expressions=[],
                        result=ast.FuncExpr(
                            identifier=ast.Identifier(name="f", location=Location(line=1, column=12)),
                            arguments=[ast.Identifier(name="a", location=Location(line=1, column=11))],
                            location=Location(line=1, column=12)
                        ),
                        location=Location(line=1, column=14)
                    )
                ],
                result=ast.Statements(
                    expressions=[],
                    result=ast.Identifier(name="b", location=Location(line=1, column=18)),
                    location=Location(line=1, column=20)
                ),
                location=Location(line=1, column=22)
            ),
            location=Location(line=1, column=3)
        )


def test_parse_curly_declaration_2() -> None:
    tokens = tokenize("{ { x }; { y }; }")
    assert parse(tokens) == ast.Statements(
            expressions=[
                ast.Statements(
                    expressions=[],
                    result=ast.Identifier(
                        name="x", location=Location(
                            line=0, column=0)),
                    location=Location(line=1, column=5)
                ),
                ast.Statements(
                    expressions=[],
                    result=ast.Identifier(
                        name="y", location=Location(
                            line=0, column=0)),
                    location=Location(line=1, column=7)
                )
            ],
            result=ast.Literal(value=None, location=None),
            location=Location(line=1, column=17)
        )


def test_parse_curly_declaration_3() -> None:
    tokens = tokenize("{ { x } { y } }")
    assert parse(tokens) == ast.Statements(
            expressions=[
                ast.Statements(
                    expressions=[], result=ast.Identifier(
                        name="x", location=Location(
                            line=1, column=5)), location=Location(
                        line=1, column=7)), ], result=ast.Statements(
                expressions=[], result=ast.Identifier(
                    name="y", location=Location(
                        line=1, column=11)), location=Location(
                    line=1, column=11)), location=Location(
                line=1, column=15))


def test_binary_op_should_be_followed_by_int_literal_or_identifier() -> None:
    tokens = tokenize("a + b +")
    try:
        parse(tokens)
    except ParsingException as e:
        assert str(
            e) == f"L(line=1, column=7): expected an integer literal or an identifier"
    else:
        assert False, "Expected ParsingException was not raised"


def test_empty_token_list_raises_an_error() -> None:
    tokens: list = []
    try:
        parse(tokens)
    except EmptyListException as e:
        assert str(e) == "token list must not be empty."
    else:
        assert False, "Expected EmptyListException was not raised"


def test_incorrect_source_code_multiliteral_raises_and_error() -> None:
    tokens = tokenize("a+b c r")
    try:
        parse(tokens)
    except ParsingException as e:
        assert str(
            e) == "L(line=1, column=5): incorrect expression: identifier should be followed by a binary operator or a statement."
    else:
        assert False, "Expected ParsingException was not raised"


def test_incorrect_source_code_multiop_raises_and_error() -> None:
    tokens = tokenize("a+b + + +")
    try:
        parse(tokens)
    except ParsingException as e:
        assert str(
            e) == "L(line=1, column=7): expected an integer literal or an identifier"
    else:
        assert False, "Expected ParsingException was not raised"


def test_parse_simple_while_expr_missing_semicolon() -> None:
    source_code = """while y > x do {
        h(x);
        d(x)
        t(x)
    };
    """
    tokens = tokenize(source_code)
    try:
        parse(tokens)
    except ParsingException as e:
        assert str(
            e) == "L(line=4, column=9): consecutive result expressions are not allowed."
    else:
        assert False, "Expected ParsingException was not raised"


def test_parse_invalid_scope_in_if_expression() -> None:
    tokens = tokenize("""if x > y then var z = 10;""")
    try:
        parse(tokens)
    except ParsingException as e:
        assert str(
            e) == "L(line=1, column=25): variable declarations are not allowed as a part of 'then' condition."
    else:
        assert False, "Expected ParsingException was not raised"


def test_parse_invalid_scope_in_while_expression() -> None:
    tokens = tokenize("""while var x = 10 do {x=x+1}""")
    try:
        parse(tokens)
    except ParsingException as e:
        assert str(
            e) == "L(line=1, column=18): variable declarations are not allowed as a part of 'while' condition."
    else:
        assert False, "Expected ParsingException was not raised"


def test_parse_invalid_block_statements_1() -> None:
    tokens = tokenize("""{ a b }""")
    try:
        parse(tokens)
    except ParsingException as e:
        assert str(
            e) == "L(line=1, column=5): incorrect expression: identifier should be followed by a binary operator or a statement."
    else:
        assert False, "Expected ParsingException was not raised"


def test_parse_invalid_block_statements_2() -> None:
    tokens = tokenize("""{ if true then { a } b c }""")
    try:
        parse(tokens)
    except ParsingException as e:
        assert str(
            e) == "L(line=1, column=24): incorrect expression: identifier should be followed by a binary operator or a statement."
    else:
        assert False, "Expected ParsingException was not raised"
