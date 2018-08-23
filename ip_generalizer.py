from generalizer import Generalizer
from stmt import *
from z3getvars import *
from interval import *

class IPGeneralizer(Generalizer):

    def __init__(self, trace, input=None, record_annotation=False, initial_formula=IntervalSet([])):
        super().__init__(trace,record_annotation,initial_formula)
        self.input = input

    def do_step(self,I, st):
        print("doing interval w.p. step with ", I, " and ", st)
        if isinstance(st, AssignmentStmt):
            return interval_assignment_pre_step(I, st)
        else:
            assert isinstance(st, ConditionStmt)
            cond = st.expr
            if is_and(cond):
                return interval_intersection([interval_condition_pre_step(I, c) for c in cond.chidren()])
            elif is_or(cond):
                # arbitrarily choose to satisfy the first disjunct
                return interval_condition_pre_step(I, cond.arg(0))
            elif is_not(cond):
                # arbitrarily choose to satisfy the first disjunct
                neg_cond = negate_condition(cond)
                return interval_condition_pre_step(I, neg_cond)
            else:
                return interval_condition_pre_step(I, cond)


def interval_assignment_pre_step(I, st):
    return I


def interval_condition_pre_step(I, cond):
    # simplified_expr = simplify(st.expr,arith_lhs=True)
    # linear_combination = simplified_expr.arg(0)
    # var_to_coeff_dict = get_vars_and_coefficients(linear_combination)
    # constant = simplified_expr.arg(1).as_long()
    # upper_bound = I.max_value(linear_combination)
    # lower_bound = I.min_value(linear_combination)
    # print(linear_combination,constant,var_to_coeff_dict)
    return I
