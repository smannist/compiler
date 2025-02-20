import re as regex
from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    line: int
    column: int

    def __str__(self) -> str:
        return f"L(line={self.line}, column={self.column})"

    def __eq__(self, class_to_compare: object) -> bool:
        return isinstance(class_to_compare, Location)


@dataclass(frozen=True)
class Token:
    loc: Location
    type: str | None
    text: str

    def __str__(self) -> str:
        return f'Token(loc={self.loc}, type="{self.type}", text="{self.text}")'


TOKEN_PATTERNS = {
    "comment": r'(//.*?(\n|$)|#.*?(\n|$)|/\*.*?\*/)',
    "int_literal": r'\b[0-9]+\b',
    "bool_literal": r'\b(true|false)\b',
    "unary_op": r'\bnot\b',
    "binary_op": r'and|or|!=|==|<=|>=|<|>|\%=?|\+=?|\/=?|\*=?|\-=?|\=(?!\d)',
    "keyword": r'\bvar|while|if|else|then|do|Int|Bool\b',
    "punctuation": r'[(),;{}:]',
    "newline": r'\n',
    "whitespace": r'[ \t]+',
    "identifier": r'_?[A-Za-z_]+[a-zA-Z0-9_]*',
    "except": r'.',
}


def tokenize(source_code: str) -> list[Token]:
    tokens = []

    line = 1
    column = 1

    pattern = regex.compile(
        "|".join(
            f"(?P<{token_type}>{pattern})" for token_type,
            pattern in TOKEN_PATTERNS.items()
        )
    )

    for match in regex.finditer(pattern, source_code):
        token_type = match.lastgroup
        value = match.group()

        if token_type == "newline" or token_type == "comment":
            line += 1
            column = 1
            continue
        elif token_type == "whitespace":
            column += len(value)
            continue
        elif token_type == "except":
            raise RuntimeError(
                f"Caught unexpected value: '{value}' at position ({line},{column})."
            )

        tokens.append(
            Token(
                Location(line, column),
                token_type,
                value
            )
        )

        column += len(value)

    return tokens
