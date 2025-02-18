import compiler.ast as ast
from compiler.tokenizer import Token
from compiler.types import Int, Bool, Unit, Type

# bottom level has highest precedence
BINARY_OPERATORS = [
    ["="],
    ["or"],
    ["and"],
    ["==", "!="],
    ["<", "<=", ">", ">="],
    ["+", "-"],
    ["*", "/", "%"]
]

UNARY_OPERATORS = ["-", "not"]


class ParsingException(Exception):
    pass


class EmptyListException(Exception):
    pass


def parse(tokens: list[Token]) -> ast.Expression:
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
            raise ParsingException(
                f"{token.loc}: expected '{expected}' but got {token.text}")
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise ParsingException(
                f"{token.loc}: expected one of: {comma_separated}")
        pos += 1
        return token

    def parse_literal() -> ast.Literal:
        token = consume()
        if token.type == "int_literal":
            return ast.Literal(value=int(token.text), location=token.loc)
        elif token.type == "bool_literal":
            return ast.Literal(
                value=True if token.text == "true" else False,
                location=token.loc)
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

        return ast.Identifier(name=token.text, location=token.loc)

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
            identifier=ast.Identifier(name=token.text, location=token.loc),
            arguments=arguments,
            location=token.loc
        )

    def parse_if_expr() -> ast.IfExpr:
        consume("if")
        condition = parse_expression()
        token = consume("then")
        then_expr = parse_expression()

        if isinstance(condition, ast.LiteralVarDecl):
            raise ParsingException(
                f"{peek().loc}: variable declarations are not allowed as a part of 'if' condition.")
        if isinstance(then_expr, ast.LiteralVarDecl):
            raise ParsingException(
                f"{peek().loc}: variable declarations are not allowed as a part of 'then' condition.")

        if peek().text == "else":
            token = consume("else")
            else_expr = parse_expression()
            if isinstance(else_expr, ast.LiteralVarDecl):
                raise ParsingException(
                    f"{peek().loc}: variable declarations are not allowed as a part of 'else' condition.")
            return ast.IfExpr(
                condition=condition,
                then=then_expr,
                else_=else_expr,
                location=token.loc)

        return ast.IfExpr(
            condition=condition,
            then=then_expr,
            location=token.loc)

    def parse_while_expr() -> ast.WhileExpr:
        consume("while")
        condition = parse_expression()
        if isinstance(condition, ast.LiteralVarDecl):
            raise ParsingException(
                f"{peek().loc}: variable declarations are not allowed as a part of 'while' condition.")
        token = consume("do")
        body = parse_statements()
        return ast.WhileExpr(
            condition=condition,
            body=body,
            location=token.loc)

    def parse_literal_var_decl(require_semicolon: bool = False) -> ast.LiteralVarDecl:
        consume("var")
        identifier = parse_identifier()
        declared_type = parse_type() if peek().text == ":" else Unit
        consume("=")
        initializer = parse_expression()
        if require_semicolon:
            consume(";")
        return ast.LiteralVarDecl(
            identifier=identifier,
            initializer=initializer,
            type=declared_type,
            location=identifier.location
        )

    def parse_type() -> Type:
        consume(":")
        token = consume()
        if token.text == "Int":
            return Int
        elif token.text == "Bool":
            return Bool
        elif token.text == "Unit":
            return Unit
        raise ParsingException(f"{token.loc}: unknown literal type {token.text}")

    def parse_unary_op() -> ast.UnaryOp:
        if peek().text in UNARY_OPERATORS:
            token = consume()
            operand = parse_factor()
            return ast.UnaryOp(
                op=token.text,
                operand=operand,
                location=token.loc)
        raise ParsingException(f"{peek().loc}: expected unary operator")

    def parse_expression(
            precedence_level: int = 0) -> ast.Expression:
        if precedence_level > len(BINARY_OPERATORS) - 1:
            return parse_factor()

        left = parse_expression(precedence_level + 1)

        while peek().text in BINARY_OPERATORS[precedence_level]:
            op_token = consume()
            op = op_token.text
            right = parse_expression(
                precedence_level if op == "=" else precedence_level + 1)
            left = ast.BinaryOp(
                left=left,
                op=op,
                right=right,
                location=op_token.loc)

        return left

    def parse_factor() -> ast.Expression:
        token = peek()
        match token:
            case Token(text="("):
                return parse_parenthesized()
            case Token(text="{"):
                return parse_statements()
            case Token(text="-") | Token(text="not") if is_unary():
                return parse_unary_op()
            case Token(type="int_literal" | "bool_literal"):
                return parse_literal()
            case Token(type="identifier"):
                if pos + 1 < len(tokens) and tokens[pos + 1].text == "(":
                    return parse_func_expr()
                return parse_identifier()
            case Token(type="keyword", text="if"):
                return parse_if_expr()
            case Token(type="keyword", text="while"):
                return parse_while_expr()
            case Token(type="keyword", text="var"):
                return parse_literal_var_decl()
            case _:
                raise ParsingException(
                    f"{token.loc}: expected an integer literal or an identifier"
                )

    def parse_parenthesized() -> ast.Expression:
        consume("(")
        expr = parse_expression()
        consume(")")
        return expr

    def parse_statements() -> ast.Statements:
        consume("{")
        expressions = []

        while peek().text != "}":
            expr = parse_expression()
            token = peek()

            if token.text == ";":
                expressions.append(expr)
                consume(";")
            elif token.text == "}":
                token = consume("}")
                return ast.Statements(
                    expressions=expressions,
                    result=expr,
                    location=token.loc)
            elif tokens[pos - 1].text not in ["{", "}", ";"]:
                raise ParsingException(
                    f"{peek().loc}: consecutive result expressions are not allowed.")
            else:
                expressions.append(expr)

        token = consume("}")
        return ast.Statements(expressions=expressions, location=token.loc)

    def parse_source_code() -> ast.Expression | ast.Statements:
        if not tokens:
            raise EmptyListException("token list must not be empty.")

        items: list[tuple[ast.Expression, bool]] = []

        while peek().type != "end":
            expr = parse_expression()

            if isinstance(expr, ast.LiteralVarDecl) and peek().text == "var":
                consume(";")

            if peek().text == ";":
                consume(";")
                items.append((expr, True))
            else:
                items.append((expr, False))

        if len(items) == 1 and not items[0][1]:
            if isinstance(items[0][0], ast.LiteralVarDecl):
                items[0][0].as_expression = True
            return items[0][0]

        last_expr, terminated = items[-1]
        if not terminated:
            if isinstance(last_expr, ast.LiteralVarDecl):
                last_expr.as_expression = True
            result_expr = last_expr
            exprs = [expr for expr, _ in items[:-1]]
        else:
            result_expr = ast.Literal(value=None, location=None)
            exprs = [expr for expr, _ in items]

        return ast.Statements(
            expressions=exprs,
            result=result_expr,
            location=peek().loc
        )

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
