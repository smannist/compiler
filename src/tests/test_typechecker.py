from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.type_checker import typecheck, SymTab
from compiler.types import Int, Unit


def test_typecheck_simple_plus_operation_without_semi() -> None:
    assert typecheck(parse(tokenize("2 + 3")), SymTab()) == Int


def test_typecheck_simple_plus_operation_with_semi() -> None:
    assert typecheck(parse(tokenize("2 + 3;")), SymTab()) == Unit


def test_typecheck_simple_minus_operation_without_semi() -> None:
    assert typecheck(parse(tokenize("2 - 3")), SymTab()) == Int


def test_typecheck_simple_minus_operation_with_semi() -> None:
    assert typecheck(parse(tokenize("2 - 3;")), SymTab()) == Unit


#def test_typecheck_one_var_decl_sum() -> None:
#    assert typecheck(parse(tokenize("var x = 123; x + 200")), SymTab()) == Int()


#def test_typecheck_two_var_decl_sum() -> None:
#    assert typecheck(parse(tokenize("var x = 123; var y = 200; x + y")), SymTab()) == Int()


#def test_typecheck_two_var_decl_sum_no_result() -> None:
#    assert typecheck(parse(tokenize("var x = 123; var y = 200; x + y;")), SymTab()) == Unit()


#def test_typecheck_assignment() -> None:
#    assert typecheck(parse(tokenize("var x = 123; x = 200; x")), SymTab()) == Int()
