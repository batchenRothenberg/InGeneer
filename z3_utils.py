from z3 import *


# Wrapper for allowing Z3 ASTs to be stored into Python Hashtables.
class AstRefKey:
    def __init__(self, n):
        self.n = n

    def __hash__(self):
        return self.n.hash()

    def __eq__(self, other):
        return self.n.eq(other.n)

    def __repr__(self):
        return str(self.n)


def askey(n):
    assert isinstance(n, AstRef)
    return AstRefKey(n)


def get_vars(f):
    r = set()

    def collect(f):
        if is_const(f):
            if f.decl().kind() == Z3_OP_UNINTERPRETED and not askey(f) in r:
                r.add(askey(f))
        else:
            for c in f.children():
                collect(c)

    collect(f)
    return r


def get_vars_and_coefficients(f):
    """Returns a dictionary mapping each variable to its coefficient in f
    (f should be a linear combination of int variables)"""
    r = {}

    def collect(f):
        if is_mul(f):
            assert is_int_value(f.arg(0))
            assert f.arg(1).decl().kind() == Z3_OP_UNINTERPRETED
            if not askey(f.arg(1)) in r.keys():
                r[askey(f.arg(1))]=f.arg(0)
        elif f.decl().kind() == Z3_OP_UNINTERPRETED and not askey(f) in r:
            r[askey(f)] = 1
        else:
            for c in f.children():
                collect(c)

    collect(f)
    return r


def negate_condition(cond):
    if cond.num_args() < 2:
        print("WARNING: could not negate condition "+str(cond))
        return cond
    else:
        arg0 = cond.arg(0)
        arg1 = cond.arg(1)
        if is_le(cond):
            return arg0 > arg1
        if is_lt(cond):
            return arg0 >= arg1
        if is_ge(cond):
            return arg0 < arg1
        if is_gt(cond):
            return arg0 <= arg1
        if is_eq(cond):
            return arg0 != arg1
        if is_distinct(cond):
            return arg0 == arg1
        else:
            print("WARNING: could not negate condition " + str(cond))
            return cond


def is_binary_boolean(c):
    return is_lt(c) or is_le(c) or is_gt(c) or is_ge(c) or is_eq(c) or is_distinct(c)


def is_binary(expr):
    return len(expr.children()) == 2


def is_uminus_on_int_value(expr):
    return is_app_of(expr,Z3_OP_UMINUS) and is_int_value(expr.arg(0))


def evaluate_binary_expr(expr, model):
    assert len(expr.children()) == 2
    arg0 = expr.arg(0)
    arg1 = expr.arg(1)
    arg1_value = model.evaluate(arg1).as_long()
    arg0_value = model.evaluate(arg0).as_long()
    op = expr.decl().kind()
    return arg0, arg1, arg0_value, arg1_value, op


def build_binary_expression(lhs, rhs, op):
    if op == Z3_OP_LE:
        return lhs <= rhs
    elif op == Z3_OP_LT:
        return lhs < rhs
    elif op == Z3_OP_GE:
        return lhs >= rhs
    elif op == Z3_OP_GT:
        return lhs > rhs
    elif op == Z3_OP_EQ:
        return lhs == rhs
    elif op == Z3_OP_DISTINCT:
        return lhs != rhs
    elif op == Z3_OP_ADD:
        return lhs + rhs
    elif op == Z3_OP_SUB:
        return lhs - rhs
    elif op == Z3_OP_MUL:
        return lhs * rhs
    elif op == Z3_OP_DIV:
        return lhs / rhs
    else:
        print("warning Unssoported operator")
        return None


def binary_bool_op_to_string(op):
    if op == Z3_OP_LE:
        return "<="
    elif op == Z3_OP_LT:
        return "<"
    elif op == Z3_OP_GE:
        return ">="
    elif op == Z3_OP_GT:
        return ">"
    elif op == Z3_OP_EQ:
        return "=="
    elif op == Z3_OP_DISTINCT:
        return "!="
    else:
        print("warning Unssoported operator")
        return None


def reverse_operator(op):
    if op == Z3_OP_LE:
        return Z3_OP_GE
    elif op == Z3_OP_LT:
        return Z3_OP_GT
    elif op == Z3_OP_GE:
        return Z3_OP_LE
    elif op == Z3_OP_GT:
        return Z3_OP_LT
    elif op == Z3_OP_EQ:
        return Z3_OP_EQ
    elif op == Z3_OP_DISTINCT:
        return Z3_OP_DISTINCT
    else:
        print("warning Unssoported operator")
        return None


def simplify_and_propagate_ineqs(f):
    goal = Goal()
    goal.add(f)
    t_1 = Tactic('simplify')
    t_2 = Tactic('propagate-ineqs')
    t = Then(t_1,t_2)
    return t(goal).as_expr()


def print_all_models(f, limit=10000):
    s = Solver()
    s.add(f)
    count = 0
    while count < limit and s.check() == sat:
        count += 1
        m = s.model()
        print(m)
        s.add(get_formula_from_model(m))
    if count == limit:
        print("max number of models reached")
    return count


# From: https://stackoverflow.com/questions/11867611/z3py-checking-all-solutions-for-equation
def get_formula_from_model(model):
    block = []
    for d in model:
        # d is a declaration
        if d.arity() > 0:
            raise Z3Exception("uninterpreted functions are not supported")
        # create a constant from declaration
        c = d()
        if is_array(c) or c.sort().kind() == Z3_UNINTERPRETED_SORT:
            raise Z3Exception("arrays and uninterpreted sorts are not supported")
        block.append(c != model[d])
    # print(Or(block))
    return (Or(block))


def get_children_values(expr, model):
    res = []
    for c in expr.children():
        res.append(model.evaluate(c).as_long())
    return res
