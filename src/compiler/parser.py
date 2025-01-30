import compiler.ast as ast
from compiler.tokenizer import Token

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
MAX_PRECEDENCE_LEVEL = len(BINARY_OPERATORS) - 1
MIN_PRECEDENCE_LEVEL = 0


class ParsingException(Exception):
    pass


class EmptyListException(Exception):
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
            raise ParsingException(f"{token.loc}: expected '{expected}' but got {token.text}")
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
            return ast.Literal(value=True if token.text == "true" else False, location=token.loc)
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
            raise ParsingException(f"{peek().loc}: variable declarations are not allowed as a part of 'if' condition.")
        if isinstance(then_expr, ast.LiteralVarDecl) or isinstance(then_expr, ast.LiteralVarDecl):
            raise ParsingException(f"{peek().loc}: variable declarations are not allowed as a part of 'then' condition.")

        if peek().text == "else":
            token = consume("else")
            else_expr = parse_expression()
            if isinstance(else_expr, ast.LiteralVarDecl):
                raise ParsingException(f"{peek().loc}: variable declarations are not allowed as a part of 'else' condition.")
            return ast.IfExpr(condition=condition, then=then_expr, else_=else_expr, location=token.loc)

        return ast.IfExpr(condition=condition, then=then_expr, location=token.loc)

    def parse_while_expr() -> ast.WhileExpr:
        consume("while")
        condition = parse_expression()
        if isinstance(condition, ast.LiteralVarDecl) or isinstance(condition, ast.LiteralVarDecl):
            raise ParsingException(f"{peek().loc}: variable declarations are not allowed as a part of 'while' condition.")
        token = consume("do")
        body = parse_statements()
        return ast.WhileExpr(condition=condition, body=body, location=token.loc)

    def parse_literal_var_decl_top_level() -> list[ast.LiteralVarDecl]: # for anything outside block e.g. top level vars
        var_declarations = []
        while peek().text == "var":
            consume("var")
            identifier = parse_identifier()
            consume("=")
            initializer = parse_literal()
            token = consume(";")
            var_declarations.append(ast.LiteralVarDecl(identifier=identifier, initializer=initializer, location=token.loc))        
        return var_declarations

    def parse_literal_var_decl_inside_block() -> ast.LiteralVarDecl: # for vars inside blocks
        consume("var")
        identifier = parse_identifier()
        token = consume("=")
        initializer = parse_literal()
        return ast.LiteralVarDecl(identifier=identifier, initializer=initializer, location=token.loc)

    def parse_unary_op() -> ast.UnaryOp:
        if peek().text in UNARY_OPERATORS:
            token = consume()
            operand = parse_expression()
            return ast.UnaryOp(op=token.text, operand=operand, location=token.loc)
        raise ParsingException(f"{peek().loc}: expected unary operator")

    def parse_expression(precedence_level: int = MIN_PRECEDENCE_LEVEL) -> ast.Expression:
        if precedence_level > MAX_PRECEDENCE_LEVEL:
            return parse_factor()

        left = parse_expression(precedence_level + 1)

        while peek().text in BINARY_OPERATORS[precedence_level]:
            op_token = consume()
            op = op_token.text
            right = parse_expression(precedence_level if op == "=" else precedence_level + 1)
            left = ast.BinaryOp(left=left, op=op, right=right, location=op_token.loc)

        return left

    def parse_factor() -> ast.Expression:
        token = peek()
        match token:
            case Token(text="("):
                return parse_parenthesized()
            case Token(text="{"):
                return parse_statements()
            case Token(type="unary_op") | Token(text="-") if is_unary():
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
                return parse_literal_var_decl_inside_block() # used for vars inside blocks for now
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
                return ast.Statements(expressions=expressions, result=expr, location=token.loc)
            elif tokens[pos - 1].text not in ["{", "}", ";"]:
                raise ParsingException(f"{peek().loc}: consecutive result expressions are not allowed.")
            else:
                expressions.append(expr)

        token = consume("}")
        return ast.Statements(expressions=expressions, location=token.loc)

    def parse_source_code() -> list[ast.Expression]:
        if not tokens:
            raise EmptyListException("token list must not be empty.")

        top_level_vars: list[ast.Expression] = []
        expressions: list[ast.Expression] = []

        while peek().type != "end":
            if peek().text == "var":
                var_decls = parse_literal_var_decl_top_level()
                top_level_vars.extend(var_decls)
            else:
                expr = parse_expression()
                if peek().text == ";" and not expressions:
                    consume(";")
                    expressions.append(ast.Statements(expressions=[expr], location=peek().loc))
                elif expressions:
                    if isinstance(expressions[0], ast.Statements):
                        expressions[0].expressions.append(expr)
                else:
                    expressions.append(expr)

        if top_level_vars:
            if not expressions:
                return ast.Statements(expressions=top_level_vars, location=peek().loc)
            elif isinstance(expressions[0], ast.Statements):
                for var_decl in top_level_vars[::-1]:
                    expressions[0].expressions.insert(0, var_decl)
            else:
                statements = ast.Statements(expressions=expressions, location=peek().loc)
                for var_decl in top_level_vars[::-1]:
                    statements.expressions.insert(0, var_decl)
                return statements

        return expressions[0]

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
