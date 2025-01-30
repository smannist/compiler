from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.interpreter import interpret

def test_interpret_basic_sum() -> None:
    source_code = "2 + 3"
    tokens = tokenize(source_code)
    parsed = parse(tokens)
    result = interpret(parsed)
    assert result == 5
