import compiler.ast as ast
from compiler.tokenizer import Token
from typing_extensions import Optional

# bottom level has highest precedence
LEFT_ASSOCIATIVE_BINARY_OPERATORS = [
    ["or"],
    ["and"],
    ["==", "!="],
    ["<", "<=", ">", ">="],
    ["+", "-"],
    ["*", "/", "%"]
]

MAX_PRECEDENCE_LEVEL = len(LEFT_ASSOCIATIVE_BINARY_OPERATORS) - 1
MIN_PRECEDENCE_LEVEL = 0


def parse(tokens: list[Token]) -> list[ast.Expression]:
    pos = 0

    def peek() -> Token:
        if pos < len(tokens):
            return tokens[pos]

        return Token(
            loc=tokens[-1].loc,
            type="end",
            text="",
        )

    def consume(expected: str | list[str] | None = None) -> Token:
        nonlocal pos
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f"{token.loc}: expected '{expected}'")
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(f"{token.loc}: expected one of: {comma_separated}")
        pos += 1
        return token

    def parse_literal() -> ast.Literal:
        token = consume()
        if token.type == "int_literal":
            return ast.Literal(int(token.text))
        elif token.type == "bool_literal":
            return ast.Literal(True if token.text == "true" else False)
        raise Exception(
            f"{peek().loc}: expected an integer or boolean literal")

    def parse_identifier() -> ast.Identifier:
        if peek().type != "identifier":
            raise Exception(f"{peek().loc}: expected an identifier")

        token = consume()

        if pos < len(tokens) and tokens[pos].type == "identifier":
            raise Exception(
                f"{peek().loc}: incorrect expression: "
                "identifier should be followed by a binary operator or a statement."
            )

        return ast.Identifier(token.text)

    def parse_func_expr() -> ast.FuncExpr:
        token = consume()
        consume("(")

        arguments = []

        if peek().text != ")":
            arguments.append(parse_expression())
            while peek().text == ",":
                consume(",")
                arguments.append(parse_expression())

        consume(")")

        return ast.FuncExpr(
            ast.Identifier(token.text),
            arguments
        )

    def parse_if_expr() -> ast.IfExpr:
        consume("if")
        if_expr = parse_expression()
        consume("then")
        then_expr = parse_expression()
        else_expr = parse_expression() if peek().text == "else" and consume("else") else None
        return ast.IfExpr(
            if_=if_expr,
            then=then_expr,
            else_=else_expr
        )

    def parse_expression(
            precedence_level: int = MIN_PRECEDENCE_LEVEL) -> ast.Expression:
        if precedence_level > MAX_PRECEDENCE_LEVEL:
            return parse_factor()

        left = parse_expression(precedence_level + 1)

        while peek(
        ).text in LEFT_ASSOCIATIVE_BINARY_OPERATORS[precedence_level]:
            op_token = consume()
            right = parse_expression(precedence_level + 1)
            left = ast.BinaryOp(left, op_token.text, right)

        return left

    def parse_factor() -> ast.Expression:
        if peek().text == "(":
            return parse_parenthesized()
        elif peek().type in ["int_literal", "bool_literal"]:
            return parse_literal()
        elif peek().type == "identifier":
            if pos + 1 < len(tokens) and tokens[pos + 1].text == "(":
                return parse_func_expr()
            return parse_identifier()
        elif peek().type == "keyword":
            return parse_if_expr()
        else:
            raise Exception(
                f"{peek().loc}: expected an integer literal, identifier or a keyword")

    def parse_parenthesized() -> ast.Expression:
        consume("(")
        expr = parse_expression()
        consume(")")
        return expr

    def parse_source_code() -> list[ast.Expression]:
        if not tokens:
            raise Exception(
                "token list must not be empty."
            )

        expressions = []
        while peek().type != "end":
            expressions.append(parse_expression())
        return expressions

    return parse_source_code()
