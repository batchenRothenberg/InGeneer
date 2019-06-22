from domain import Domain
from precise_domain import PreciseDomain
from formula_strengthener import StrenghenedFormula,strengthen
from stmt import *
from z3_utils import *
from interval import *


class IntervalDomain(Domain):

    ''' Class implementing abstract 'domain' class
        for formulas consisting of an IntervalSet (upper and lower bounds for variables)
        and a precise formula - manipulated using the precise domain (weakest-precondition)
    '''
    def __init__(self, debug=False):
        self.debug = debug

    def do_step(self, f, stmt, model):
        if stmt.is_assignment():
            return self._assignment_pre_step(f, stmt, model)
        else:
            assert stmt.is_condition()
            cond = stmt.expr
            return self._condition_pre_step(f, cond, model)

    def does_step_lead_to_state_in_model(self, f, stmt, model):
        if model is None:
            return True
        else:
            if stmt.is_assignment():
                assigned_var = stmt.lhs
                assignment_expr = stmt.rhs
                new_value = model.evaluate(assignment_expr)
                new_model = update_model(model,[(assigned_var,new_value)])
                return f.interval_set.is_var_in_range(assigned_var,new_value) and new_model.evaluate(And(f.unsimplified_demands))
            else:
                assert stmt.is_condition()
                cond = stmt.expr
                return model.evaluate(cond)

    def is_bottom(self, f):
        return f.is_bottom()

    def is_top(self, f):
        return f.is_top()

    def intersection(self, formulas):
        return StrenghenedFormula.intersection(formulas)

    def get_top(self):
        return StrenghenedFormula.get_top(self.debug)

    def get_bottom(self):
        return StrenghenedFormula.get_bottom(self.debug)

    def choose(self, formulas, model):
        chosen_indices = [i for i in range(len(formulas))]
        unchosen_indices = []
        return chosen_indices, unchosen_indices

    def _assignment_pre_step(self, f, stmt, model):
        assigned_var = stmt.lhs
        assignment_expr = stmt.rhs
        if assigned_var not in f.interval_set:
            return f
        else:
            var_interval = f.interval_set.get_interval(assigned_var)
            f_copy = IntervalSet.get_top().intersect(f)
            f_copy.delete_interval(assigned_var)
            cond = And(var_interval.low <= assignment_expr, assignment_expr <= var_interval.high)
            return self._condition_pre_step(f_copy, cond, model)

    def _condition_pre_step(self, f, cond, model):
        strengthened_condition =  strengthen(cond,model,self.debug)
        return StrenghenedFormula.intersection([f,strengthened_condition])
