from compiler import ir
from compiler.tokenizer import tokenize, Location
from compiler.parser import parse
from compiler.ir_generator import generate_ir
from compiler.types import Int


def test_generate_ir_for_1_plus_2_times_3():
    # root_types dont need correct types atm
    root_types = {
        ir.IRVar("+"): Int,
        ir.IRVar("*"): Int,
        ir.IRVar("print_int"): Int,
    }
    instructions = generate_ir(root_types, parse(tokenize("1 + 2 * 3")))
    expected_instructions = [
        ir.Label(Location(0, 0), "start"),
        ir.LoadIntConst(Location(1, 1), 1, ir.IRVar("x")),
        ir.LoadIntConst(Location(1, 5), 2, ir.IRVar("x2")),
        ir.LoadIntConst(Location(1, 9), 3, ir.IRVar("x3")),
        ir.Call(Location(1, 7), ir.IRVar("*"), [ir.IRVar("x2"), ir.IRVar("x3")], ir.IRVar("x4")),
        ir.Call(Location(1, 3), ir.IRVar("+"), [ir.IRVar("x"), ir.IRVar("x4")], ir.IRVar("x5")),
        ir.Call(Location(1, 3), ir.IRVar("print_int"), [ir.IRVar("x5")], ir.IRVar("x6"))
    ]
    assert len(instructions) == len(expected_instructions)
    for inst, exp_inst in zip(instructions, expected_instructions):
        assert inst == exp_inst
