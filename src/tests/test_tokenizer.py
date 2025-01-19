from compiler.tokenizer import tokenize, Token, L

def test_tokenizer_basics() -> None:
    assert tokenize("aaa 123 bbb while false // not \n not ==") == [
        Token(loc=L, type="identifier", text="aaa"),
        Token(loc=L, type="int_literal", text="123"),
        Token(loc=L, type="identifier", text="bbb"),
        Token(loc=L, type="keyword", text="while"),
        Token(loc=L, type="bool_literal", text="false"),
        Token(loc=L, type="unary_op", text="not"),
        Token(loc=L, type="binary_op", text="=="),
]
