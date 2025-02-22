from pytest import CaptureFixture
from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.interpreter import interpret, build_interpreter_root_symtab


symtab = build_interpreter_root_symtab()


def test_interpret_basic_sum() -> None:
    assert interpret(parse(tokenize("2 + 3")), symtab) == 5


def test_interpret_basic_sum_with_unary() -> None:
    assert interpret(parse(tokenize("-2 + 3")), symtab) == 1


def test_interpret_basic_sub_with_unaries() -> None:
    assert interpret(parse(tokenize("-2 - -4")), symtab) == 2


def test_interpret_basic_division() -> None:
    assert interpret(parse(tokenize("8 / 2")), symtab) == 4


def test_interpret_basic_multi() -> None:
    assert interpret(parse(tokenize("8 * 2")), symtab) == 16


def test_interpret_basic_modulo() -> None:
    assert interpret(parse(tokenize("2 % 2")), symtab) == 0


def test_interpret_less_than() -> None:
    assert interpret(parse(tokenize("2 < 4")), symtab) == True


def test_interpret_greater_than() -> None:
    assert interpret(parse(tokenize("2 > 4")), symtab) == False


def test_interpret_LEQ() -> None:
    assert interpret(parse(tokenize("2 <= 4")), symtab) == True


def test_interpret_GEQ() -> None:
    assert interpret(parse(tokenize("2 >= 4")), symtab) == False


def test_interpret_is_equal_false() -> None:
    assert interpret(parse(tokenize("2 == 4")), symtab) == False


def test_interpret_is_equal_true() -> None:
    assert interpret(parse(tokenize("2 == 2")), symtab) == True


def test_interpret_is_not_equal_true() -> None:
    assert interpret(parse(tokenize("2 != 4")), symtab) == True


def test_interpret_is_not_equal_false() -> None:
    assert interpret(parse(tokenize("2 != 2")), symtab) == False


def test_interpret_var_decl_unit() -> None:
    assert interpret(parse(tokenize("x = 123;")), symtab) == None


def test_interpret_var_decl() -> None:
    assert interpret(parse(tokenize("x = 123")), symtab) == 123


def test_fun_print_int(capfd: CaptureFixture[str]) -> None:
    interpret(parse(tokenize("x = 123; y = 200; print_int(x);")), symtab)
    assert capfd.readouterr().out == "123\n"
    assert interpret(parse(tokenize("x = 123; y = 200; print_int(x);")), symtab) == None


def test_interpret_variable_shadowing(capfd: CaptureFixture[str]) -> None:
    source_code = """
    {
        var x = 1;
        {
            var x = 2; # shadows the x in the outer scope
            var y = 3; # local to this inner block scope
            print_int(x); # should print 2
            print_int(y); # should print 3
        }
        print_int(x); # should print 1
    }
    """
    interpret(parse(tokenize(source_code)), symtab)
    assert capfd.readouterr().out == "2\n3\n1\n"


def test_short_circuiting_1() -> None:
    source_code = """
        var evaluated_right_hand_side = false;
        true or { evaluated_right_hand_side = true; true };
        evaluated_right_hand_side  # Should be false
    """
    assert interpret(parse(tokenize(source_code)), symtab) == False


def test_short_circuiting_2() -> None:
    source_code = """
        var evaluated_right_hand_side = true;
        true or { evaluated_right_hand_side = true; true };
        evaluated_right_hand_side  # Should be true
    """
    assert interpret(parse(tokenize(source_code)), symtab) == True


def test_interpret_while_expr(capfd: CaptureFixture[str]) -> None:
    source_code = """
    x = 1;
    while x < 100 do {
        x = x + 1;
    };
    print_int(x);
    """
    interpret(parse(tokenize(source_code)), symtab)
    assert capfd.readouterr().out == "100\n"
