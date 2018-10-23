from z3 import *
from interval import *
from utils import remove_or, negate_condition, is_binary_boolean, evaluate_binary_expr, build_binary_expression, \
    is_binary, reverse_operator


class StrenghenedFormula():

    def __init__(self):
        self.unsimplified_demands = []
        self.interval_set = IntervalSet.get_top()

    def add_unsimplified_demand(self, demand):
        self.unsimplified_demands.append(demand)

    def __str__(self):
        return "unsimplified demands: " + str(self.unsimplified_demands) + " Interval set: " + str(self.interval_set)

    def __repr__(self):
        return str(self)

    def add_interval(self, var, interval):
        self.interval_set.add_interval(var, interval)


def strengthen(f, model):
    res = StrenghenedFormula()
    f_as_and = remove_or(f, model)
    print("f_as_and: "+str(f_as_and))
    if is_and(f_as_and):
        for c in f_as_and.children():
            _strengthen_conjunct(c, model, res)
    else: # f_is_and is an atomic boolean constraint
        _strengthen_conjunct(f_as_and, model, res)
    return res


def _strengthen_conjunct(conjunct, model, res):
    if is_not(conjunct):
        _strengthen_conjunct(negate_condition(conjunct.arg(0)), model, res)
    elif is_binary_boolean(conjunct):
        lhs, rhs, lhs_value, rhs_value, op = evaluate_binary_expr(conjunct, model)
        _strengthen_binary_boolean_conjunct(lhs, lhs_value, rhs_value, op, model, res)
    else:
        res.add_unsimplified_demand(conjunct)


def _add_interval_for_binary_boolean(var, var_value, rhs_value, op, res):
    if op == Z3_OP_LE:
        res.add_interval(str(var), Interval(MINF, rhs_value))
    elif op == Z3_OP_LT:
        res.add_interval(str(var), Interval(MINF, rhs_value - 1))
    elif op == Z3_OP_GE:
        res.add_interval(str(var), Interval(rhs_value, INF))
    elif op == Z3_OP_GT:
        res.add_interval(str(var), Interval(rhs_value + 1, INF))
    elif op == Z3_OP_EQ:
        res.add_interval(str(var), Interval(rhs_value, rhs_value))
    elif op == Z3_OP_DISTINCT:
        _add_interval_for_binary_boolean(var, var_value, rhs_value, _replace_distinct_with_ineq(var_value, rhs_value), res)


def _replace_distinct_with_ineq(lhs_value, rhs_value):
    if lhs_value > rhs_value:
        return Z3_OP_GT
    else:
        assert lhs_value < rhs_value
        return Z3_OP_LT


def _strengthen_add(lhs_arg0, lhs_arg1, lhs_arg0_val, lhs_arg1_val, op, rhs_value, model, res):
    # print("strengthening add: ",lhs)
    if op == Z3_OP_LE:
        lhs_value = lhs_arg0_val + lhs_arg1_val
        diff = rhs_value - lhs_value
        assert diff >= 0
        first_addition = diff // 2
        second_addition = diff - first_addition
        _strengthen_binary_boolean_conjunct(lhs_arg0, lhs_arg0_val, lhs_arg0_val + first_addition, op, model, res)
        _strengthen_binary_boolean_conjunct(lhs_arg1, lhs_arg1_val, lhs_arg1_val + second_addition, op, model, res)


def _strengthen_mul_by_constant(lhs_arg0, lhs_arg1, lhs_arg0_val, lhs_arg1_val, op, rhs_value, model, res):
    if is_int_value(lhs_arg0):
        constant = lhs_arg0_val
        var = lhs_arg1
        var_value = lhs_arg1_val
    else:
        assert is_int_value(lhs_arg1)
        constant = lhs_arg1_val
        var = lhs_arg0
        var_value = lhs_arg0_val
    if op == Z3_OP_DISTINCT:
        ineq_op = _replace_distinct_with_ineq(constant * var_value, rhs_value)
        _strengthen_mul_by_constant(lhs_arg0, lhs_arg1, lhs_arg0_val, lhs_arg1_val, ineq_op, rhs_value, model, res)
        return
    if constant > 0:
        is_round_up = (op == Z3_OP_GE or op == Z3_OP_GT)
        _strengthen_binary_boolean_conjunct(var,var_value,rhs_value//constant+is_round_up,op,model,res)
    elif constant < 0:
        reversed_op = reverse_operator(op)
        is_round_up = (reversed_op == Z3_OP_GE or reversed_op == Z3_OP_GT)
        _strengthen_binary_boolean_conjunct(var,var_value,rhs_value//constant+is_round_up,reversed_op,model,res)


def _strengthen_binary_boolean_conjunct(lhs, lhs_value, rhs_value, op, model, res):
    print("lhs " + str(lhs) + " rhs_value: " + str(rhs_value))
    if is_const(lhs):
        _add_interval_for_binary_boolean(lhs, lhs_value, rhs_value, op, res)
    elif is_app_of(lhs, Z3_OP_UMINUS):
        arg0 = lhs.arg(0)
        _strengthen_binary_boolean_conjunct(arg0, -lhs_value, -rhs_value, reverse_operator(op), model, res)
    elif is_binary(lhs):
        lhs_arg0, lhs_arg1, lhs_arg0_val, lhs_arg1_val, lhs_op = evaluate_binary_expr(lhs, model)
        if lhs_op == Z3_OP_ADD:
            _strengthen_add(lhs_arg0, lhs_arg1, lhs_arg0_val, lhs_arg1_val, op, rhs_value, model, res)
        elif lhs_op == Z3_OP_SUB:
            _strengthen_add(lhs_arg0, -lhs_arg1, lhs_arg0_val, -lhs_arg1_val, op, rhs_value, model, res)
        elif lhs_op == Z3_OP_MUL and (is_int_value(lhs_arg0) or is_int_value(lhs_arg1)):
            _strengthen_mul_by_constant(lhs_arg0, lhs_arg1, lhs_arg0_val, lhs_arg1_val, op, rhs_value, model, res)
        else:
            res.add_unsimplified_demand(build_binary_expression(lhs, IntVal(rhs_value), op))
    else:
        res.add_unsimplified_demand(build_binary_expression(lhs,IntVal(rhs_value),op))
