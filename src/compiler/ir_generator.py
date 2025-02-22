from compiler import ast, ir
from compiler.tokenizer import Location
from compiler.symtab import SymTab
from compiler.types import Type, Bool, Int, Unit

# root_types dont need correct types atm
ROOT_TYPES = {
    ir.IRVar(symbol): Type() for symbol in [
        "+",
        "-",
        "*",
        "/",
        "%",
        ">",
        "<",
        "<=",
        ">",
        ">=",
        "!=",
        "==",
        "print_int",
        "print_bool",
        "read_int",
        "unary_-",
        "unary_not"
    ]
}


def generate_ir(
    root_types: dict[ir.IRVar, Type],
    root_expr: ast.Expression
) -> list[ir.Instruction]:
    var_types: dict[ir.IRVar, Type] = root_types.copy()
    var_unit = ir.IRVar("unit")
    var_types[var_unit] = Unit

    ins: list[ir.Instruction] = []
    labels: dict[str, int] = {}

    var_counter = 0

    def new_var(t: Type) -> ir.IRVar:
        nonlocal var_counter
        var_counter += 1
        name = "x" if var_counter == 1 else f"x{var_counter}"
        v = ir.IRVar(name)
        var_types[v] = t
        return v

    def new_label(name: str, loc: Location | None) -> ir.Label:
        nonlocal labels
        if name not in labels:
            labels[name] = 1
        label_name = name if labels[name] == 1 else f"{name}{labels[name]}"
        labels[name] += 1
        return ir.Label(loc, label_name)

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
                        raise Exception(
                            f"{loc}: unsupported literal: {type(expression.value).__name__}"
                        )
                return var

            case ast.Identifier():
                return symbol_table.lookup(expression.name)

            case ast.LiteralVarDecl():
                var_init = visit(symbol_table, expression.initializer)
                var_name = expression.identifier.name

                if symbol_table.get_local(var_name):
                    raise Exception(
                        f"{loc}: Variable '{var_name}' already declared in the scope."
                    )

                var = new_var(var_types[var_init])
                symbol_table.set(var_name, var, local=True)
                ins.append(ir.Copy(loc, var_init, var))
                return var_unit

            case ast.BinaryOp():
                match expression.op:
                    case "=":
                        if not isinstance(expression.left, ast.Identifier):
                            raise Exception(
                                f"{loc}: Left-hand side of assignment must be an identifier"
                            )
                        var_left = symbol_table.lookup(expression.left.name)
                        var_right = visit(symbol_table, expression.right)
                        ins.append(ir.Copy(loc, var_right, var_left))
                        return var_left
                    case "and" | "or" as op:
                        l_right = new_label(f"{op}_right", loc)
                        l_skip = new_label(f"{op}_skip", loc)
                        l_end = new_label(f"{op}_end", loc)

                        var_left = visit(symbol_table, expression.left)

                        ins.append(ir.CondJump(
                            loc,
                            var_left,
                            l_right if op == "and" else l_skip,
                            l_skip if op == "and" else l_right
                            )
                        )
                        ins.append(l_right)

                        var_right = visit(symbol_table, expression.right)
                        var_result = new_var(Bool)

                        ins.append(ir.Copy(loc, var_right, var_result))
                        ins.append(ir.Jump(loc, l_end))
                        ins.append(l_skip)
                        ins.append(ir.LoadBoolConst(loc, op != "and", var_result))
                        ins.append(ir.Jump(loc, l_end))

                        ins.append(l_end)
                        return var_result
                    case _:
                        var_op = symbol_table.lookup(expression.op)
                        var_left = visit(symbol_table, expression.left)
                        var_right = visit(symbol_table, expression.right)
                        var_result = new_var(Bool if expression.op in ["==", "!="] else expression.type)
                        ins.append(
                            ir.Call(
                                loc,
                                var_op,
                                [var_left, var_right],
                                var_result
                            )
                        )
                        return var_result

            case ast.UnaryOp():
                var_unary_op = symbol_table.lookup("unary_" + expression.op)
                var_value = visit(symbol_table, expression.operand)

                if expression.op == "not":
                    var_result = new_var(Bool)
                elif expression.op == "-":
                    var_result = new_var(Int)

                ins.append(ir.Call(loc, var_unary_op, [var_value], var_result))
                return var_result

            case ast.IfExpr():
                if expression.else_ is not None and not (
                    isinstance(
                        expression.else_,
                        ast.Literal) and expression.else_.value is None
                    ):
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
                else:
                    l_then = new_label("then", loc)
                    l_end = new_label("if_end", loc)
                    var_cond = visit(symbol_table, expression.condition)
                    ins.append(ir.CondJump(loc, var_cond, l_then, l_end))
                    ins.append(l_then)
                    visit(symbol_table, expression.then)
                    ins.append(l_end)
                    return var_unit

            case ast.WhileExpr():
                l_start = new_label("while_start", loc)
                l_body = new_label("while_body", loc)
                l_end = new_label("while_end", loc)

                ins.append(l_start)

                var_cond = visit(symbol_table, expression.condition)
                ins.append(ir.CondJump(loc, var_cond, l_body, l_end))
                ins.append(l_body)

                visit(symbol_table, expression.body)
                ins.append(ir.Jump(loc, l_start))
                ins.append(l_end)
                return var_unit

            case ast.FuncExpr():
                var_ident = symbol_table.lookup(expression.identifier.name)
                var_args = [
                    visit(symbol_table, arg) for arg in expression.arguments
                ]
                var_result = new_var(expression.type)
                ins.append(
                    ir.Call(
                        expression.location,
                        var_ident,
                        var_args,
                        var_result
                    )
                )
                return var_result

            case ast.Statements():
                local_symtab = SymTab[ir.IRVar](parent=symbol_table)
                for expr in expression.expressions:
                    visit(local_symtab, expr)
                if expression.result:
                    return visit(local_symtab, expression.result)
                return var_unit

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
