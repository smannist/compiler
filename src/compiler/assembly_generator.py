import dataclasses
from compiler import ir
from compiler.intrinsics import all_intrinsics, IntrinsicArgs


class Locals:
    """Knows the memory location of every local variable."""
    _var_to_location: dict[ir.IRVar, str]
    _stack_used: int

    def __init__(self, variables: list[ir.IRVar]) -> None:
        self._var_to_location = {}
        for index, var in enumerate(variables):
            offset = 8 * (index + 1)
            self._var_to_location[var] = f"-{offset}(%rbp)"
        self._stack_used = 8 * len(variables)

    def get_ref(self, v: ir.IRVar) -> str:
        """Returns an Assembly reference like `-24(%rbp)`
        for the memory location that stores the given variable"""
        return self._var_to_location[v]

    def stack_used(self) -> int:
        """Returns the number of bytes of stack space needed for the local variables."""
        return self._stack_used


def get_all_ir_variables(instructions: list[ir.Instruction]) -> list[ir.IRVar]:
    result_list: list[ir.IRVar] = []
    result_set: set[ir.IRVar] = set()

    def add(v: ir.IRVar) -> None:
        if v not in result_set:
            result_list.append(v)
            result_set.add(v)

    for insn in instructions:
        for field in dataclasses.fields(insn):
            value = getattr(insn, field.name)
            if isinstance(value, ir.IRVar):
                add(value)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, ir.IRVar):
                        add(v)
    return result_list


def generate_assembly(instructions: list[ir.Instruction]) -> str:
    lines = []
    def emit(line: str) -> None:
        lines.append(line)

    locals = Locals(
        variables=get_all_ir_variables(instructions)
    )

    emit(".extern print_int")
    emit(".extern print_bool")
    emit(".extern read_int")
    emit(".global main")
    emit(".type main, @function")
    emit(".section .text")
    emit("main:")
    emit("pushq %rbp")
    emit("movq %rsp, %rbp")
    emit(f"subq ${locals.stack_used()}, %rsp")

    for insn in instructions:
        match insn:
            case ir.Label():
                emit("")
                emit(f".L{insn.name}:")

            case ir.LoadIntConst():
                if -2**31 <= insn.value < 2**31:
                    emit(f"movq ${insn.value}, {locals.get_ref(insn.dest)}")
                else:
                    emit(f"movabsq ${insn.value}, %rax")
                    emit(f"movq %rax, {locals.get_ref(insn.dest)}")

            case ir.LoadBoolConst():
                bool_val = 1 if insn.value else 0
                emit(f"movq ${bool_val}, {locals.get_ref(insn.dest)}")

            case ir.Copy():
                emit(f"movq {locals.get_ref(insn.source)}, %rax")
                emit(f"movq %rax, {locals.get_ref(insn.dest)}")

            case ir.CondJump():
                emit(f"cmpq $0, {locals.get_ref(insn.cond)}")
                emit(f"jne .L{insn.then_label.name}")
                emit(f"jmp .L{insn.else_label.name}")

            case ir.Jump():
                emit(f"jmp .L{insn.label.name}")

            case ir.Call():
                intrinsic = all_intrinsics.get(insn.fun.name)
                if intrinsic:
                    arg_refs = [locals.get_ref(arg) for arg in insn.args]
                    result_reg = "%rax"
                    intrinsic(IntrinsicArgs(arg_refs, result_reg, emit))
                    emit(f"movq {result_reg}, {locals.get_ref(insn.dest)}")
                else:
                    reg_order = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]
                    for i, arg in enumerate(insn.args):
                        if i < len(reg_order):
                            emit(f"movq {locals.get_ref(arg)}, {reg_order[i]}")
                    emit(f"call {insn.fun.name}")
                    emit(f"movq %rax, {locals.get_ref(insn.dest)}")

    emit("")
    emit("movq %rbp, %rsp")
    emit("popq %rbp")
    emit("ret")

    return "\n".join(lines)
