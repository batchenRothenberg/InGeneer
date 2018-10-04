from domain import Domain
from stmt import *
from utils import *
from interval import *


class IntervalDomain(Domain):

    def do_step(self,I, st, model):
        if st.is_assignment():
            return interval_assignment_pre_step(I, st)
        else:
            assert st.is_condition()
            cond = st.expr
            if is_and(cond):
                return Interval.intersection([interval_condition_pre_step(I, c) for c in cond.chidren()])
            elif is_or(cond):
                # arbitrarily choose to satisfy the first disjunct
                return interval_condition_pre_step(I, cond.arg(0))
            elif is_not(cond):
                # arbitrarily choose to satisfy the first disjunct
                neg_cond = negate_condition(cond)
                return interval_condition_pre_step(I, neg_cond)
            else:
                return interval_condition_pre_step(I, cond)

    def check_sat(self, formula, stmt, model):
        return True

    def is_bottom(self, I):
        return I.is_bottom()

    def is_top(self, I):
        return I.is_top()

    def intersection(self, formulas):
        return IntervalSet.intersection(formulas)

    def get_top(self):
        return IntervalSet.get_top()

    def get_bottom(self):
        return IntervalSet.get_bottom()

    def choose(self, formulas, model):
        chosen_indices = []
        unchosen_indices = []
        for i in range(len(formulas)):
            if self.is_bottom(formulas[i]):
                unchosen_indices.append(i)
            else:
                chosen_indices.append(i)
        return chosen_indices, unchosen_indices


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
