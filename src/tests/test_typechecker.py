from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.type_checker import typecheck
from compiler.symtab import build_type_symtab
from compiler.types import Int, Unit, Bool


symtab = build_type_symtab()


def test_typecheck_simple_plus_operation_without_semi() -> None:
    assert typecheck(parse(tokenize("2 + 3")), symtab) == Int


def test_typecheck_simple_plus_operation_with_semi() -> None:
    assert typecheck(parse(tokenize("2 + 3;")), symtab) == Unit


def test_typecheck_simple_minus_operation_without_semi() -> None:
    assert typecheck(parse(tokenize("2 - 3")), symtab) == Int


def test_typecheck_simple_minus_operation_with_semi() -> None:
    assert typecheck(parse(tokenize("2 - 3;")), symtab) == Unit


def test_typecheck_var_decl() -> None:
    assert typecheck(parse(tokenize("var x = 123; x")), symtab) == Int


def test_typecheck_var_decl_sum() -> None:
    assert typecheck(parse(tokenize("var x = 123; var y = 200; x + y")), symtab) == Int


def test_typecheck_var_decl_no_result() -> None:
    assert typecheck(parse(tokenize("var x = 123; x;")), symtab) == Unit


def test_typecheck_var_decl_no_result_2() -> None:
    assert typecheck(parse(tokenize("var x = 123; x;")), symtab) == Unit


def test_typecheck_correct_bool_comparison_int_literal() -> None:
    assert typecheck(parse(tokenize("var y = 200; var x = 123; x == y")), symtab) == Bool


def test_typecheck_correct_bool_comparison_bool_literal() -> None:
    assert typecheck(parse(tokenize("var y = true; var x = false; x == y")), symtab) == Bool


def test_typecheck_assignment() -> None:
    assert typecheck(parse(tokenize("var x = 123; x = 200")), symtab) == Int 


def test_unary_not() -> None:
    assert typecheck(parse(tokenize("not false")), symtab) == Bool


def test_unary_minus() -> None:
    assert typecheck(parse(tokenize("-2")), symtab) == Int


def test_block_statement_semicolon() -> None:
    assert typecheck(parse(tokenize("{ 123; }")), symtab) == Unit


def test_empty_block_statement() -> None:
    assert typecheck(parse(tokenize("{ }")), symtab) == Unit


def test_if_then_else() -> None:
    assert typecheck(parse(tokenize("var x = 123; var y = 5; if x > 10 then x = 13 else y")), symtab) == Int


def test_typecheck_and_operator() -> None:
    assert typecheck(parse(tokenize("true or false")), symtab) == Bool


def test_typecheck_typed_variabled_decl_int_no_semi() -> None:
    assert typecheck(parse(tokenize("var x: Int = 1 + 1")), symtab) == Int


def test_typecheck_typed_variabled_decl_int_semi() -> None:
    assert typecheck(parse(tokenize("var x: Int = 1 + 1;")), symtab) == Unit


def test_typecheck_typed_variabled_decl_bool_no_semi() -> None:
    assert typecheck(parse(tokenize("var x: Bool = false")), symtab) == Bool


def test_typecheck_incorrect_bool_comparison() -> None:
    try:
        typecheck(parse(tokenize("var y = false; var x = 123; x == y")), symtab)
    except TypeError as e:
        assert str(e) == "Invalid types for binary operation '=='"
    else:
        assert False, "Expected TypeError was not raised"


def test_typecheck_incorrect_not_types() -> None:
    try:
        typecheck(parse(tokenize("not 2")), symtab)
    except TypeError as e:
        assert str(e) == "Unary operator 'not' is not defined for type IntType()"
    else:
        assert False, "Expected TypeError was not raised"


def test_typecheck_incorrect_minus_types() -> None:
    try:
        typecheck(parse(tokenize("-false")),symtab)
    except TypeError as e:
        assert str(e) == "Unary operator '-' is not defined for type BoolType()"
    else:
        assert False, "Expected TypeError was not raised"
