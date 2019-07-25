from z3 import *

# Z3 OPERATORS
Z3_LE_OPS = [Z3_OP_LE,Z3_OP_SLEQ]
Z3_LT_OPS = [Z3_OP_LT,Z3_OP_SLT]
Z3_GE_OPS = [Z3_OP_GE,Z3_OP_SGEQ]
Z3_GT_OPS = [Z3_OP_GT,Z3_OP_SGT]
Z3_EQ_OPS = [Z3_OP_EQ]
Z3_DISTINCT_OPS = [Z3_OP_DISTINCT]
Z3_ADD_OPS = [Z3_OP_ADD,Z3_OP_BADD]
Z3_SUB_OPS = [Z3_OP_SUB,Z3_OP_BSUB]
Z3_MUL_OPS = [Z3_OP_MUL,Z3_OP_BMUL]
Z3_DIV_OPS = [Z3_OP_DIV,Z3_OP_IDIV,Z3_OP_BSDIV,Z3_OP_BSDIV0,Z3_OP_BUDIV,Z3_OP_BUDIV0]
Z3_REM_OPS = [Z3_OP_REM,Z3_OP_BSREM,Z3_OP_BSREM0,Z3_OP_BUREM,Z3_OP_BUREM0]
Z3_MOD_OPS = [Z3_OP_MOD,Z3_OP_BSMOD,Z3_OP_BSMOD0]
Z3_AND_OPS = [Z3_OP_AND,Z3_OP_BAND,Z3_OP_BREDAND]
Z3_OR_OPS = [Z3_OP_OR,Z3_OP_BOR,Z3_OP_BREDOR]


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
        if is_le_or_sle(cond):
            return arg0 > arg1
        if is_lt_or_slt(cond):
            return arg0 >= arg1
        if is_ge_or_sge(cond):
            return arg0 < arg1
        if is_gt_or_sgt(cond):
            return arg0 <= arg1
        if is_eq_or_seq(cond):
            return arg0 != arg1
        if is_distinct_or_sdistinct(cond):
            return arg0 == arg1
        else:
            print("WARNING: could not negate condition " + str(cond))
            return cond


def is_slt(c):
    return is_app_of(c, Z3_OP_SLT)


def is_sleq(c):
    return is_app_of(c, Z3_OP_SLEQ)


def is_sgt(c):
    return is_app_of(c, Z3_OP_SGT)


def is_sgeq(c):
    return is_app_of(c, Z3_OP_SGEQ)


def is_binary_boolean(c):
    return is_lt_or_slt(c) \
            or is_le_or_sle(c) \
            or is_gt_or_sgt(c) \
            or is_ge_or_sge(c) \
            or is_eq_or_seq(c) \
            or is_distinct_or_sdistinct(c)


def is_binary(expr):
    return len(expr.children()) == 2


def is_uminus_on_int_value(expr):
    return is_app_of(expr,Z3_OP_UMINUS) and is_int_value(expr.arg(0))


def is_uminus_on_bv_value(expr):
    return is_app_of(expr,Z3_OP_UMINUS) and is_bv_value(expr.arg(0))


def is_numeral_constant(expr):
    return is_int_value(expr) or is_uminus_on_int_value(expr) or is_bv_value(expr) or is_uminus_on_bv_value(expr)


def evaluate_binary_expr(expr, model):
    assert len(expr.children()) == 2
    arg0 = expr.arg(0)
    arg1 = expr.arg(1)
    arg1_value = model_evaluate_to_const(arg1, model)
    arg0_value = model_evaluate_to_const(arg0, model)
    op = get_op(expr)
    return arg0, arg1, arg0_value, arg1_value, op


def get_op(expr):
    return expr.decl().kind()


def get_id(expr):
    return expr.get_id()


def build_binary_expression(lhs, rhs, op):
    if op in Z3_LE_OPS:
        return lhs <= rhs
    elif op in Z3_LT_OPS:
        return lhs < rhs
    elif op in Z3_GE_OPS:
        return lhs >= rhs
    elif op in Z3_GT_OPS:
        return lhs > rhs
    elif op in Z3_EQ_OPS:
        return lhs == rhs
    elif op in Z3_DISTINCT_OPS:
        return lhs != rhs
    elif op in Z3_ADD_OPS:
        return lhs + rhs
    elif op in Z3_SUB_OPS:
        return lhs - rhs
    elif op in Z3_MUL_OPS:
        return lhs * rhs
    elif op in Z3_DIV_OPS:
        return lhs / rhs
    elif op in Z3_REM_OPS or op in Z3_MOD_OPS:
        return lhs % rhs
    else:
        print("warning Unssoported operator")
        return None


def op_to_string(op):
    if op in Z3_LE_OPS:
        return "<="
    elif op in Z3_LT_OPS:
        return "<"
    elif op in Z3_GE_OPS:
        return ">="
    elif op in Z3_GT_OPS:
        return ">"
    elif op in Z3_EQ_OPS:
        return "=="
    elif op in Z3_DISTINCT_OPS:
        return "!="
    elif op in Z3_AND_OPS:
        return "and"
    elif op in Z3_OR_OPS:
        return "or"
    elif op in Z3_ADD_OPS:
        return "+"
    elif op in Z3_SUB_OPS:
        return "-"
    elif op in Z3_MUL_OPS:
        return "*"
    elif op in Z3_DIV_OPS:
        return "/"
    elif op in Z3_MOD_OPS:
        return "%"
    elif op in Z3_REM_OPS:
        return "%"
    elif op == Z3_OP_UMINUS:
        return "-"
    else:
        print("warning Unssoported operator")
        return None


def reverse_boolean_operator(op):
    if op == Z3_OP_LE:
        return Z3_OP_GE
    elif op == Z3_OP_LT:
        return Z3_OP_GT
    elif op == Z3_OP_GE:
        return Z3_OP_LE
    elif op == Z3_OP_GT:
        return Z3_OP_LT
    elif op == Z3_OP_SLEQ:
        return Z3_OP_SGEQ
    elif op == Z3_OP_SLT:
        return Z3_OP_SGT
    elif op == Z3_OP_SGEQ:
        return Z3_OP_SLEQ
    elif op == Z3_OP_SGT:
        return Z3_OP_SLT
    elif op == Z3_OP_EQ:
        return Z3_OP_EQ
    elif op == Z3_OP_DISTINCT:
        return Z3_OP_DISTINCT
    else:
        print("warning Unssoported operator")
        return None


# Further simplifies a bitvector constraint by making sure that the rhs contains only constants
# lhs and rhs are only simplified if their op is +
def bitvector_simplify(bv_c):
    if is_not(bv_c):
        return Not(bitvector_simplify(bv_c.arg(0)))
    elif len(bv_c.children()) == 0:
        return bv_c
    else:
        lhs = bv_c.arg(0)
        rhs = bv_c.arg(1)
        # Calculate constant and non constant
        lhs_nonconstants, lhs_constants = separate_constant_arguments(lhs)
        rhs_nonconstants, rhs_constants = separate_constant_arguments(rhs)
        if len(lhs_constants)==0 and len(rhs_nonconstants)==0:
            return bv_c
        else:
            new_lhs = concat_with_minus(lhs_nonconstants,rhs_nonconstants)
            new_rhs = concat_with_minus(rhs_constants,lhs_constants)
            return build_binary_expression(sum_without_zero(new_lhs),sum_without_zero(new_rhs),get_op(bv_c))


def sum_without_zero(list_of_expr):
    if len(list_of_expr)==0:
        return 0
    else:
        sum = list_of_expr[0]
        for e in list_of_expr[1:]:
            sum = sum + e
        return sum


# list=[e_1,e_2,..,e_k], list_to_negate=[t_1,t_2,...,t_k]
# result = [e_1,e_2,...,e_k,-t_1,-t_2,...,-t_k]
def concat_with_minus(list, list_to_negate):
    negated_list = [apply_unary_minus(x) for x in list_to_negate]
    return list+negated_list


def apply_unary_minus(expr):
    if is_app_of(expr,Z3_OP_UMINUS):
        return expr.arg(0)
    else:
        return -expr


# Gets an expr e and returns a tuple of two lists:
# A list of all nonconstant sub-expressions in it, and a list of all constants sub-expressions.
# A sub-expression is either the entire expr e, or e_i if e=e_1+e_2+...+e_k
# A sub-expression is constant iff is_numeral_constant() returns true
def separate_constant_arguments(expr):
    constants = []
    nonconstants = []
    if is_numeral_constant(expr):
        constants.append(expr)
    elif get_op(expr) not in Z3_ADD_OPS:
        nonconstants.append(expr)
    else:
        for c in expr.children():
            if is_numeral_constant(c):
                constants.append(c)
            else:
                nonconstants.append(c)
    return nonconstants , constants


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
        s.add(get_blocking_formula_from_model(m))
    if count == limit:
        print("max number of models reached")
    return count


# From: https://stackoverflow.com/questions/11867611/z3py-checking-all-solutions-for-equation
def get_blocking_formula_from_model(model):
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


def create_dictionary_from_model(model):
    dict = {}
    for d in model.decls():
        dict[d.name()] = (d(), model[d])
    return dict


def create_model_from_dictionary(dict):
    s = Solver()
    for var_name in dict.keys():
            var,value = dict[var_name]
            s.add(var == value)
    s.check()
    return s.model()


def get_model_from_SSA_trace(trace):
    s = Solver()
    f = []
    for stmt in trace:
        f.append(stmt.expr)
    s.add(And(f))
    s.check()
    return s.model()

# list_of_tuples should contain pairs of variables and updated values, as z3 objects, e.g.:
# x = Int(x)
# update_model(m,[(x,IntVal(7))]) will update model m s.t. variable x gets value 7 (other variables remain unchanged)
# also update_model(m,[(x,7)]) will work
def update_model(model, list_of_tuples):
    d = create_dictionary_from_model(model)
    for var,val in list_of_tuples:
        d[var.get_id()]=(var,val)
    return create_model_from_dictionary(d)


def get_children_values(expr, model):
    res = []
    for c in expr.children():
        res.append(model_evaluate_to_const(c,model))
    return res


def is_le_or_sle(expr):
    return True in [is_app_of(expr,op) for op in Z3_LE_OPS]

def is_lt_or_slt(expr):
    return True in [is_app_of(expr, op) for op in Z3_LT_OPS]

def is_ge_or_sge(expr):
    return True in [is_app_of(expr, op) for op in Z3_GE_OPS]

def is_gt_or_sgt(expr):
    return True in [is_app_of(expr, op) for op in Z3_GT_OPS]

def is_eq_or_seq(expr):
    return True in [is_app_of(expr, op) for op in Z3_EQ_OPS]

def is_distinct_or_sdistinct(expr):
    return True in [is_app_of(expr, op) for op in Z3_DISTINCT_OPS]

def is_add_or_sadd(expr):
    return True in [is_app_of(expr, op) for op in Z3_ADD_OPS]

def is_sub_or_ssub(expr):
    return True in [is_app_of(expr, op) for op in Z3_SUB_OPS]

def is_mul_or_smul(expr):
    return True in [is_app_of(expr, op) for op in Z3_MUL_OPS]

def is_div_or_sdiv(expr):
    return True in [is_app_of(expr, op) for op in Z3_DIV_OPS]

def is_rem_or_srem(expr):
    return True in [is_app_of(expr, op) for op in Z3_REM_OPS]

def is_mod_or_smod(expr):
    return True in [is_app_of(expr, op) for op in Z3_MOD_OPS]


def model_evaluate_to_const(expr, model):
    if is_bool(expr):
        res_true = is_true(model.evaluate(expr))
        res_false = is_false(model.evaluate(expr))
        assert res_false or res_true
        return res_true
    else:
        assert is_int(expr) or is_bv(expr)
        return model.evaluate(expr).as_long()


def strict_to_nonstrict_bool_op(op):
    if op==Z3_OP_LT:
        return Z3_OP_LE
    elif op==Z3_OP_SLT:
        return Z3_OP_SLEQ
    elif op ==Z3_OP_GT:
        return Z3_OP_GE
    elif op==Z3_OP_SGT:
        return Z3_OP_SGEQ
    else:
        assert False


def nonstrict_to_strict_bool_op(op):
    if op==Z3_OP_LE:
        return Z3_OP_LT
    elif op==Z3_OP_SLEQ:
        return Z3_OP_SLT
    elif op ==Z3_OP_GE:
        return Z3_OP_GT
    elif op==Z3_OP_SGEQ:
        return Z3_OP_SGT
    else:
        assert False


def evaluate_phi_function(phi, model):
    if model_evaluate_to_const(phi.guard, model):
        return phi.true_var
    else:
        return phi.false_var
