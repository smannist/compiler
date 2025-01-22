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

UNARY_OPERATORS = ["-", "not"]

MAX_PRECEDENCE_LEVEL = len(LEFT_ASSOCIATIVE_BINARY_OPERATORS) - 1
MIN_PRECEDENCE_LEVEL = 0


class ParsingException(Exception):
    pass


class EmptyListExpection(Exception):
    pass


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
            raise ParsingException(f"{token.loc}: expected '{expected}'")
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise ParsingException(
                f"{token.loc}: expected one of: {comma_separated}")
        pos += 1
        return token

    def parse_literal() -> ast.Literal:
        token = consume()
        if token.type == "int_literal":
            return ast.Literal(int(token.text))
        elif token.type == "bool_literal":
            return ast.Literal(True if token.text == "true" else False)
        raise ParsingException(
            f"{peek().loc}: expected an integer or boolean literal")

    def parse_identifier() -> ast.Identifier:
        if peek().type != "identifier":
            raise ParsingException(f"{peek().loc}: expected an identifier")

        token = consume()

        if pos < len(tokens) and tokens[pos].type == "identifier":
            raise ParsingException(
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
        condition_expr = parse_expression()
        consume("then")
        then_expr = parse_expression()
        else_expr = parse_expression() if peek().text == "else" and consume("else") else None
        return ast.IfExpr(
            condition_expr,
            then_expr,
            else_expr
        )

    def parse_unary_op() -> ast.UnaryOp:
        if peek().text in UNARY_OPERATORS:
            op = consume().text
            operand = parse_expression()
            return ast.UnaryOp(op, operand)
        raise ParsingException(f"{peek().loc}: expected unary operator")

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
        elif peek().type == "unary_op" or peek().text == "-" and is_unary():
            return parse_unary_op()
        elif peek().type in ["int_literal", "bool_literal"]:
            return parse_literal()
        elif peek().type == "identifier":
            if pos + 1 < len(tokens) and tokens[pos + 1].text == "(":
                return parse_func_expr()
            return parse_identifier()
        elif peek().type == "keyword":
            return parse_if_expr()
        else:
            raise ParsingException(
                f"{peek().loc}: expected an integer literal or an identifier")

    def parse_parenthesized() -> ast.Expression:
        consume("(")
        expr = parse_expression()
        consume(")")
        return expr

    def parse_source_code() -> list[ast.Expression]:
        if not tokens:
            raise EmptyListExpection(
                "token list must not be empty."
            )

        expressions = []
        while peek().type != "end":
            expressions.append(parse_expression())
        return expressions

    def is_unary() -> bool:
        if pos == 0:
            return True
        prev_token = tokens[pos - 1]
        return prev_token.type in [
            "binary_op",
            "unary_op",
            "punctuation",
            "keyword"] or prev_token.text == "("

    return parse_source_code()
