import compiler.ast as ast
from compiler.tokenizer import Token

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

    def parse_literal() -> ast.Literal:
        token = consume()
        if token.type == "int_literal":
            return ast.Literal(int(token.text))
        elif token.type == "bool_literal":
            return ast.Literal(True if token.text == "true" else False)
        raise Exception(f"{peek().loc}: expected an integer or boolean literal")

    def parse_identifier() -> ast.Identifier:
        if peek().type != "identifier":
            raise Exception(f"{peek().loc}: expected an identifier")
        if proceeding_type() == "identifier":
            raise Exception(
                f"{peek(offset=1).loc}: incorrect expression: "
                "identifier should be followed by a binary operator or a statement."
            )
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
        elif peek().type == "int_literal" or peek().type == "bool_literal":
            return parse_literal()
        elif peek().type == "identifier" and proceeding_text() == "(":
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
            expressions.append(parse_expression())

        return expressions

    def proceeding_text() -> str:
        return peek(offset=1).text

    def proceeding_type() -> str:
        return peek(offset=1).type

    return parse_source_code()
