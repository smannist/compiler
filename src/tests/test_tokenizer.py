from compiler.tokenizer import tokenize, Token, Location

L = Location(0,0)

def test_tokenizer_passes_white_space() -> None:
    assert tokenize("   x   ") == [
        Token(loc=L, type="identifier", text="x"),
    ]

def test_tokenizer_passes_comments() -> None:
    assert tokenize("// this is a a comment \n x # this is a also a comment \n y") == [
        Token(loc=L, type="identifier", text="x"),
        Token(loc=L, type="identifier", text="y")
    ]

def test_tokenizer_passes_multiline_comments() -> None:
    source_code = """
    /* this is a multiline comment and it ends now */ print_int(123);
    """
    assert tokenize(source_code) == [
        Token(loc=L, type="identifier", text="print_int"),
        Token(loc=L, type="punctuation", text="("),
        Token(loc=L, type="int_literal", text="123"),
        Token(loc=L, type="punctuation", text=")"),
        Token(loc=L, type="punctuation", text=";")
    ]

def test_expression_without_whitespace_tokenized_correctly() -> None:
    assert tokenize("x+z-2-4") == [
        Token(loc=L, type="identifier", text="x"),
        Token(loc=L, type="binary_op", text="+"),
        Token(loc=L, type="identifier", text="z"),
        Token(loc=L, type="binary_op", text="-"),
        Token(loc=L, type="int_literal", text="2"),
        Token(loc=L, type="binary_op", text="-"),
        Token(loc=L, type="int_literal", text="4")
    ]

def test_expression_with_whitespace_tokenized_correctly() -> None:
    assert tokenize("x + z - 2 - 4") == [
        Token(loc=L, type="identifier", text="x"),
        Token(loc=L, type="binary_op", text="+"),
        Token(loc=L, type="identifier", text="z"),
        Token(loc=L, type="binary_op", text="-"),
        Token(loc=L, type="int_literal", text="2"),
        Token(loc=L, type="binary_op", text="-"),
        Token(loc=L, type="int_literal", text="4")
    ]

def test_unary_operator_is_recognised() -> None:
    assert tokenize("x not 3") == [
        Token(loc=L, type="identifier", text="x"),
        Token(loc=L, type="unary_op", text="not"),
        Token(loc=L, type="int_literal", text="3")
    ]

def test_boolean_literal_are_recognised() -> None:
    assert tokenize("true false false true") == [
        Token(loc=L, type="bool_literal", text="true"),
        Token(loc=L, type="bool_literal", text="false"),
        Token(loc=L, type="bool_literal", text="false"),
        Token(loc=L, type="bool_literal", text="true")
    ]

def test_keywords_are_recognised():
        assert tokenize("while var if else then") == [
        Token(loc=L, type="keyword", text="while"),
        Token(loc=L, type="keyword", text="var"),
        Token(loc=L, type="keyword", text="if"),
        Token(loc=L, type="keyword", text="else"),
        Token(loc=L, type="keyword", text="then")
    ]

def test_punctuation_recognised():
    assert tokenize("{(),;{}:") == [
        Token(loc=L, type="punctuation", text="{"),
        Token(loc=L, type="punctuation", text="("),
        Token(loc=L, type="punctuation", text=")"),
        Token(loc=L, type="punctuation", text=","),
        Token(loc=L, type="punctuation", text=";"),
        Token(loc=L, type="punctuation", text="{"),
        Token(loc=L, type="punctuation", text="}"),
        Token(loc=L, type="punctuation", text=":"),
    ]

def test_complex_source_code_tokenization():
    source_code = """
    var n: Int = read_int();
    print_int(n);
    while n > 1 do {
        if n % 2 == 0 then {
            n = n / 2;
        } else {
            n = 3 * n + 1;
        }
        print_int(n);
    }
    """
    assert tokenize(source_code) == [
        Token(loc=L, type="keyword", text="var"),
        Token(loc=L, type="identifier", text="n"),
        Token(loc=L, type="punctuation", text=":"),
        Token(loc=L, type="identifier", text="Int"),
        Token(loc=L, type="binary_op", text="="),
        Token(loc=L, type="identifier", text="read_int"),
        Token(loc=L, type="punctuation", text="("),
        Token(loc=L, type="punctuation", text=")"),
        Token(loc=L, type="punctuation", text=";"),
        Token(loc=L, type="identifier", text="print_int"),
        Token(loc=L, type="punctuation", text="("),
        Token(loc=L, type="identifier", text="n"),
        Token(loc=L, type="punctuation", text=")"),
        Token(loc=L, type="punctuation", text=";"),
        Token(loc=L, type="keyword", text="while"),
        Token(loc=L, type="identifier", text="n"),
        Token(loc=L, type="binary_op", text=">"),
        Token(loc=L, type="int_literal", text="1"),
        Token(loc=L, type="keyword", text="do"),
        Token(loc=L, type="punctuation", text="{"),
        Token(loc=L, type="keyword", text="if"),
        Token(loc=L, type="identifier", text="n"),
        Token(loc=L, type="binary_op", text="%"),
        Token(loc=L, type="int_literal", text="2"),
        Token(loc=L, type="binary_op", text="=="),
        Token(loc=L, type="int_literal", text="0"),
        Token(loc=L, type="keyword", text="then"),
        Token(loc=L, type="punctuation", text="{"),
        Token(loc=L, type="identifier", text="n"),
        Token(loc=L, type="binary_op", text="="),
        Token(loc=L, type="identifier", text="n"),
        Token(loc=L, type="binary_op", text="/"),
        Token(loc=L, type="int_literal", text="2"),
        Token(loc=L, type="punctuation", text=";"),
        Token(loc=L, type="punctuation", text="}"),
        Token(loc=L, type="keyword", text="else"),
        Token(loc=L, type="punctuation", text="{"),
        Token(loc=L, type="identifier", text="n"),
        Token(loc=L, type="binary_op", text="="),
        Token(loc=L, type="int_literal", text="3"),
        Token(loc=L, type="binary_op", text="*"),
        Token(loc=L, type="identifier", text="n"),
        Token(loc=L, type="binary_op", text="+"),
        Token(loc=L, type="int_literal", text="1"),
        Token(loc=L, type="punctuation", text=";"),
        Token(loc=L, type="punctuation", text="}"),
        Token(loc=L, type="identifier", text="print_int"),
        Token(loc=L, type="punctuation", text="("),
        Token(loc=L, type="identifier", text="n"),
        Token(loc=L, type="punctuation", text=")"),
        Token(loc=L, type="punctuation", text=";"),
        Token(loc=L, type="punctuation", text="}")
    ]

def test_incorrect_source_code_raises_an_error() -> None:
    try:
        tokenize("x !#¤")
    except RuntimeError as e:
        assert str(e) == "Caught unexpected value: '!' at position (0,2)."
    else:
        assert False, "Expected RuntimeError was not raised"
