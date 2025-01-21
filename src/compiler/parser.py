import compiler.ast as ast
from compiler.tokenizer import Token


def parse(tokens: list[Token]) -> ast.Expression:
    if not tokens:
        raise Exception(
            "token list must not be empty."
        )

    pos = 0

    def peek(offset: int = 0) -> Token:
        if pos + offset < len(tokens):
            return tokens[pos + offset]

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

    def parse_int_literal() -> ast.Literal:
        if peek().type != "int_literal":
            raise Exception(f"{peek().loc}: expected an integer literal")
        token = consume()
        return ast.Literal(int(token.text))

    def parse_bool_literal() -> ast.Literal:
        if peek().type != "bool_literal":
            raise Exception(f"{peek().loc}: expected bool literal")
        token = consume()
        return ast.Literal(True if token.text == "true" else False)

    def parse_identifier() -> ast.Identifier:
        if peek().type != "identifier":
            raise Exception(f"{peek().loc}: expected an identifier")
        if check_next_type() == "identifier":
            raise Exception(f"{peek(offset=1).loc}: incorrect expression: identifier should be followed by a binary operator or a statement.")
        token = consume()
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
        required_keywords = ["if", "then"]
        expressions = []

        for keyword in required_keywords:
            consume(keyword)
            expressions.append(parse_expression())

        if peek().text == "else":
            consume("else")
            expressions.append(parse_expression())
        else:
            expressions.append(None)

        return ast.IfExpr(
            if_=expressions[0],
            then=expressions[1],
            else_=expressions[2]
        )

    def parse_term() -> ast.Expression:
        left = parse_factor()

        while peek().text in ["*", "/"]:
            operator_token = consume()
            operator = operator_token.text
            right = parse_factor()
            left = ast.BinaryOp(
                left,
                operator,
                right
            )

        return left

    def parse_expression() -> ast.Expression:
        left = parse_term()

        while peek().text in ["+", "-"]:
            operator_token = consume()
            operator = operator_token.text
            right = parse_term()
            left = ast.BinaryOp(
                left,
                operator,
                right
            )

        return left

    def parse_factor() -> ast.Expression:
        if peek().text == "(":
            return parse_parenthesized()
        elif peek().type == "int_literal":
            return parse_int_literal()
        elif peek().type == "bool_literal":
            return parse_bool_literal()
        elif peek().type == "identifier" and check_next_text() == "(":
            return parse_func_expr()
        elif peek().type == "identifier":
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

    def parse_source_code() -> ast.Expression:
        expressions = []

        while peek().type != "end":
            expression = parse_expression()
            expressions.append(expression)

        return expressions

    def check_next_text():
        return peek(offset=1).text

    def check_next_type():
        return peek(offset=1).type

    return parse_source_code()
