from generalizer import Generalizer
from enum import Enum
from stmt import *


class Simplification(Enum):
    NONE = 1
    ONCE_AT_END = 2
    ALWAYS = 3


class WPGeneralizer(Generalizer):

    def __init__(self, trace, record_annotation = False, simplification = Simplification.NONE, initial_formula=True):
        super().__init__(trace,record_annotation,initial_formula)
        self.simplification = simplification

    def do_step(self, f, st):
        print("doing precise w.p. step with ", f, " and ", st)
        if isinstance(st, AssignmentStmt):
            weakest_precondition_goal = Goal()
            fresh_var = Const(str(st.lhs) + "'", st.lhs.sort())
            new_f = substitute(f, [(st.lhs, fresh_var)])
            new_assign = (fresh_var == st.rhs)
            weakest_precondition_goal.add(Exists([fresh_var], And(new_assign, new_f)))
            t = Tactic('qe')  # quantifier elimination
            wp = t(weakest_precondition_goal).as_expr()
        else:
            assert (isinstance(st, ConditionStmt))
            wp = And(f, st.expr)
        if self.simplification == Simplification.ALWAYS:
            wp = simplify(wp)
        return wp

    def generalize(self):
        r = super().generalize()
        if self.simplification == Simplification.ONCE_AT_END:
            r = simplify(r)
        return r

    def set_simplification(self,simpl):
        self.simplification = simpl