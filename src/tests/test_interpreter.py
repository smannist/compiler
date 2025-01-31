from pytest import CaptureFixture
from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.interpreter import interpret, SymTab


def test_interpret_basic_sum() -> None:
    assert interpret(parse(tokenize("2 + 3")), SymTab()) == 5


def test_interpret_basic_sum_with_unary() -> None:
    assert interpret(parse(tokenize("-2 + 3")), SymTab()) == 1


def test_interpret_basic_sub_with_unaries() -> None:
    assert interpret(parse(tokenize("-2 - -4")), SymTab()) == 2


def test_interpret_basic_division() -> None:
    assert interpret(parse(tokenize("8 / 2")), SymTab()) == 4


def test_interpret_basic_multi() -> None:
    assert interpret(parse(tokenize("8 * 2")), SymTab()) == 16


def test_interpret_basic_modulo() -> None:
    assert interpret(parse(tokenize("2 % 2")), SymTab()) == 0


def test_interpret_less_than() -> None:
    assert interpret(parse(tokenize("2 < 4")), SymTab()) == True


def test_interpret_greater_than() -> None:
    assert interpret(parse(tokenize("2 > 4")), SymTab()) == False


def test_interpret_LEQ() -> None:
    assert interpret(parse(tokenize("2 <= 4")), SymTab()) == True


def test_interpret_GEQ() -> None:
    assert interpret(parse(tokenize("2 >= 4")), SymTab()) == False


def test_interpret_is_equal_false() -> None:
    assert interpret(parse(tokenize("2 == 4")), SymTab()) == False


def test_interpret_is_equal_true() -> None:
    assert interpret(parse(tokenize("2 == 2")), SymTab()) == True


def test_interpret_is_not_equal_true() -> None:
    assert interpret(parse(tokenize("2 != 4")), SymTab()) == True


def test_interpret_is_not_equal_false() -> None:
    assert interpret(parse(tokenize("2 != 2")), SymTab()) == False


def test_interpret_var_decl_unit() -> None:
    assert interpret(parse(tokenize("x = 123;")), SymTab()) == None


def test_interpret_var_decl() -> None:
    assert interpret(parse(tokenize("x = 123")), SymTab()) == 123


def test_fun_print_int_as_result_expression(capfd: CaptureFixture[str]) -> None:
    interpret(parse(tokenize("x = 123; y = 200; print_int(x)")), SymTab())
    captured = capfd.readouterr()
    assert captured.out == "123\n"


def test_fun_print_int_without_expression(capfd: CaptureFixture[str]) -> None:
    interpret(parse(tokenize("x = 123; y = 200; print_int(x);")), SymTab())
    captured = capfd.readouterr()
    assert captured.out == ""
    assert interpret(parse(tokenize("x = 123; y = 200; print_int(x);")), SymTab()) == None

