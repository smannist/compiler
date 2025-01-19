import re as regex
from dataclasses import dataclass


@dataclass(frozen=True)
class L:
    line: int
    column: int

    def __str__(self) -> str:
        return f"L(line={self.line}, column={self.column})"

    def __eq__(self, class_to_compare: object) -> bool:
        return class_to_compare is L


@dataclass(frozen=True)
class Token:
    loc: L
    type: str | None
    text: str

    def __str__(self) -> str:
        return f'Token(loc={self.loc}, type="{self.type}", text="{self.text}")'


TOKEN_PATTERNS = {
    "int_literal": r'(?P<int_literal>\b[1-9][0-9]*\b|\b0\b)',
    "bool_literal": r'(?P<bool_literal>\b(true|false)\b)',
    "keyword": r'(?<!\S)(?P<keyword>var|while|if|else|then)(?!\S)',
    "unary_op": r'(?<!\S)(?P<unary_op>not)(?!\S)',
    "binary_op": r'(?<!\S)(?P<binary_op>!=|==|<=|>=|<|>|\+|\/|\*|\-|=)(?!\S)',
    "punctuation": r'(?P<punctuation>[(),;{}:])',
    "newline": r'(?P<newline>\n)',
    "whitespace": r'(?P<whitespace>[ \t]+)',
    "comment": r'(?P<comment>[#].*?(\n|$)|[//].*?(\n|$))',
    "identifier": r'(?P<identifier>_?[A-Za-z_]+[a-zA-Z0-9_]*)',
    "except": r'(?P<except>.)',
}


def tokenize(source_code: str) -> list[Token]:
    tokens = []

    line = 0
    column = 0

    pattern = regex.compile("|".join(TOKEN_PATTERNS.values()))

    for match in regex.finditer(pattern, source_code):
        token_type = match.lastgroup
        value = match.group()

        if token_type == "newline" or token_type == "comment":
            line += 1
            column = 0
            continue
        elif token_type == "whitespace":
            column += len(value)
            continue
        elif token_type == "except":
            raise RuntimeError(
                f"Caught unexpected value: '{value}' at position ({line},{column}).")

        tokens.append(Token(L(line, column), token_type, value))

        column += len(value)

    return tokens
