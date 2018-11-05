from stmt import *
from domain import Domain
from z3_utils import simplify_and_propagate_ineqs

class PreciseDomain(Domain):

    def __init__(self, simplification = False):
        self.simplification = simplification

    def do_step(self, f, st, model):
        if st.is_assignment():
            new_f = substitute(f, [(st.lhs, st.rhs)])
            wp = new_f
        else:
            assert (st.is_condition())
            wp = And(f, st.expr)
        if self.simplification:
            wp = simplify_and_propagate_ineqs(wp)
        return wp

    def check_sat(self, formula, stmt, model):
        if model is None:
            return True
        else:
            return is_true(model.evaluate(And(formula,stmt.expr)))

    def set_simplification(self,simpl):
        self.simplification = simpl

    def is_bottom(self, formula):
        return is_false(formula)

    def is_top(self, formula):
        return is_true(formula)

    def intersection(self, formulas):
        if len(formulas) >= 2:
            return And(formulas)
        elif len(formulas) == 1:
            return formulas[0]
        else:
            return PreciseDomain.get_top()

    def get_top(self):
        return BoolVal(True)

    def get_bottom(self):
        return BoolVal(False)

    def choose(self, formulas, model):
        chosen_indices = [i for i in range(len(formulas))]
        unchosen_indices = []
        return chosen_indices, unchosen_indices