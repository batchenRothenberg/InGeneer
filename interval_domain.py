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
                if is_int(assigned_var) or is_bv(assigned_var):
                    new_value = model_evaluate_to_const(assignment_expr,model)
                    new_model = update_model(model,[(assigned_var,new_value)])
                    return f.interval_set.is_variable_in_range(assigned_var,new_value) and model_evaluate_to_const(And(f.unsimplified_demands),new_model)
                else:
                    assert is_bool(assigned_var)
                    old_value = model_evaluate_to_const(assigned_var,model)
                    new_value = model_evaluate_to_const(assignment_expr,model)
                    return old_value == new_value
            else:
                assert stmt.is_condition()
                cond = stmt.expr
                return model_evaluate_to_const(cond,model)

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
        if is_bool(assigned_var):
            if model_evaluate_to_const(assigned_var,model):
                return self._condition_pre_step(f, assignment_expr, model)
            else:
                return self._condition_pre_step(f, Not(assignment_expr), model)
        else:
            assert (is_int(assigned_var) or is_bv(assigned_var))
            res = f.__deepcopy__()
            res.substitute_var_with_expr(assigned_var,assignment_expr,model)
            return res

    def _condition_pre_step(self, f, cond, model):
        res = f.__deepcopy__()
        res.strengthen_and_add_condition(cond, model)
        return res





