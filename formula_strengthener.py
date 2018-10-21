from z3 import *
from interval import *
from utils import remove_or, negate_condition, is_binary_boolean


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
        _strengthen_binary_boolean_conjunct(conjunct, model, res)
    else:
        res.add_unsimplified_demand(conjunct)


def _add_interval_for_binary_boolean(lhs, rhs_value, res, conjunct, lhs_value):
    if is_le(conjunct):
        res.add_interval(str(lhs), Interval(MINF, rhs_value))
    elif is_lt(conjunct):
        res.add_interval(str(lhs), Interval(MINF, rhs_value - 1))
    elif is_ge(conjunct):
        res.add_interval(str(lhs), Interval(rhs_value, INF))
    elif is_gt(conjunct):
        res.add_interval(str(lhs), Interval(rhs_value + 1, INF))
    elif is_eq(conjunct):
        res.add_interval(str(lhs), Interval(rhs_value, rhs_value))
    elif is_distinct(conjunct):
        if lhs_value > rhs_value:
            res.add_interval(str(lhs), Interval(rhs_value + 1, INF))
        else:
            assert lhs_value < rhs_value
            res.add_interval(str(lhs), Interval(MINF, rhs_value - 1))


def _strengthen_binary_boolean_conjunct(conjunct, model, res):
    lhs, rhs, lhs_value, rhs_value = _evaluate_binary_conjunct(conjunct,model)
    print("rhs value: " + str(rhs_value) + " lhs_value: " + str(lhs_value))
    if is_const(lhs):
        _add_interval_for_binary_boolean(lhs,rhs_value,res, conjunct, lhs_value)
    else:
        res.add_unsimplified_demand(conjunct)


def _evaluate_binary_conjunct(conjunct, model):
    lhs = conjunct.arg(0)
    rhs = conjunct.arg(1)
    rhs_value = model.evaluate(rhs).as_long()
    lhs_value = model.evaluate(lhs).as_long()
    return lhs, rhs, lhs_value, rhs_value