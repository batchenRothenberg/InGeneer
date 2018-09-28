from stmt import *
from domain import Domain


class PreciseDomain(Domain):

    def __init__(self, simplification = False):
        self.simplification = simplification

    def do_step(self, f, st):
        print("doing precise w.p. step with ", f, " and ", st)
        if st.is_assignment():
            weakest_precondition_goal = Goal()
            fresh_var = Const(str(st.lhs) + "'", st.lhs.sort())
            new_f = substitute(f, [(st.lhs, fresh_var)])
            new_assign = (fresh_var == st.rhs)
            weakest_precondition_goal.add(Exists([fresh_var], And(new_assign, new_f)))
            t = Tactic('qe')  # quantifier elimination
            wp = t(weakest_precondition_goal).as_expr()
        else:
            assert (st.is_condition())
            wp = And(f, st.expr)
        if self.simplification:
            wp = simplify(wp)
        return wp

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