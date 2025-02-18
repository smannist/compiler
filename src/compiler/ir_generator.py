from compiler import ast, ir
from compiler.tokenizer import Location
from compiler.symtab import SymTab
from compiler.types import Type, Bool, Int, Unit


def generate_ir(
    root_types: dict[ir.IRVar, Type],
    root_expr: ast.Expression
) -> list[ir.Instruction]:
    var_types: dict[ir.IRVar, Type] = root_types.copy()
    var_unit = ir.IRVar("unit")
    var_types[var_unit] = Unit

    ins: list[ir.Instruction] = []

    var_counter = 0
    label_counter = 0

    def new_var(t: Type) -> ir.IRVar:
        nonlocal var_counter
        var_counter += 1
        name = "x" if var_counter == 1 else f"x{var_counter}"
        v = ir.IRVar(name)
        var_types[v] = t
        return v

    def new_label(name: str, loc: Location | None) -> ir.Label:
        nonlocal label_counter
        label_counter += 1
        if label_counter == 1:
            label_name = "start"
        else:
            label_name = f"{name}{label_counter}"
        return ir.Label(location=loc, name=label_name)

    ins.append(new_label(loc=Location(0, 0), name="start"))

    def visit(
        symbol_table: SymTab[ir.IRVar],
        expression: ast.Expression
    ) -> ir.IRVar:
        loc = expression.location

        match expression:
            case ast.Literal():
                match expression.value:
                    case bool():
                        var = new_var(Bool)
                        ins.append(ir.LoadBoolConst(loc, expression.value, var))
                    case int():
                        var = new_var(Int)
                        ins.append(ir.LoadIntConst(loc, expression.value, var))
                    case None:
                        var = var_unit
                    case _:
                        raise Exception(f"{loc}: unsupported literal: {type(expression.value).__name__}"
                        )
                return var

            case ast.Identifier():
                return symbol_table.lookup(expression.name)

            case ast.BinaryOp():
                var_op = symbol_table.lookup(expression.op)
                var_left = visit(symbol_table, expression.left)
                var_right = visit(symbol_table, expression.right)
                var_result = new_var(Int)
                ins.append(
                    ir.Call(
                        loc,
                        var_op,
                        [var_left, var_right],
                        var_result
                    )
                )
                return var_result

            case ast.IfExpr():
                if expression.else_ is None:
                    l_then = new_label("then", loc)
                    l_end = new_label("if_end", loc)

                    var_cond = visit(symbol_table, expression.condition)
                    ins.append(ir.CondJump(loc, var_cond, l_then, l_end))

                    ins.append(l_then)
                    visit(symbol_table, expression.then)

                    ins.append(l_end)
                    return var_unit
                else:
                    l_then = new_label("then", loc)
                    l_else = new_label("else", loc)
                    l_end = new_label("if_end", loc)

                    var_cond = visit(symbol_table, expression.condition)
                    ins.append(ir.CondJump(loc, var_cond, l_then, l_else))
                    ins.append(l_then)

                    var_result = new_var(expression.type)
                    var_then = visit(symbol_table, expression.then)
                    ins.append(ir.Copy(loc, var_then, var_result))
                    ins.append(ir.Jump(loc, l_end))
                    ins.append(l_else)

                    var_else = visit(symbol_table, expression.else_)
                    ins.append(ir.Copy(loc, var_else, var_result))
                    ins.append(l_end)

                    return var_result

            case _:
                raise Exception(f"{loc}: unsupported AST node: {expression}")

    root_symtab = SymTab[ir.IRVar](parent=None)
    for v in root_types.keys():
        root_symtab.add_local(v.name, v)

    var_final_result = visit(root_symtab, root_expr)

    if var_types[var_final_result] == Int:
        ins.append(
            ir.Call(
                root_expr.location,
                ir.IRVar("print_int"),
                [var_final_result],
                new_var(Int)
            )
        )
    elif var_types[var_final_result] == Bool:
        ins.append(
            ir.Call(
                root_expr.location,
                ir.IRVar("print_bool"),
                [var_final_result],
                new_var(Bool)
            )
        )

    return ins
