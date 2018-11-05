from z3 import *
from interval import *
from z3_utils import negate_condition, is_binary_boolean, evaluate_binary_expr, build_binary_expression, \
    is_binary, reverse_operator, binary_bool_op_to_string, print_all_models, get_children_values, is_uminus_on_int_value


class StrenghenedFormula():

    def __init__(self, debug = False):
        self.unsimplified_demands = []
        self.interval_set = IntervalSet.get_top()
        self.debug = debug

    def add_unsimplified_demand(self, demand):
        self.unsimplified_demands.append(demand)

    def __str__(self):
        return "unsimplified demands: " + str(self.unsimplified_demands) + " Interval set: " + str(self.interval_set)

    def __repr__(self):
        return str(self)

    def add_interval(self, var, interval):
        self.interval_set.add_interval(var, interval)

    def _strengthen_conjunct(self, conjunct, model):
        if is_not(conjunct):
            self._strengthen_conjunct(negate_condition(conjunct.arg(0)), model)
        elif is_binary_boolean(conjunct):
            lhs, rhs, lhs_value, rhs_value, op = evaluate_binary_expr(conjunct, model)
            self._strengthen_binary_boolean_conjunct(lhs, lhs_value, rhs_value, op, model)
        else:
            self.add_unsimplified_demand(conjunct)

    def _add_interval_for_binary_boolean(self, var, var_value, rhs_value, op):
        if op == Z3_OP_LE:
            self.add_interval(str(var), Interval(MINF, rhs_value))
        elif op == Z3_OP_LT:
            self.add_interval(str(var), Interval(MINF, rhs_value - 1))
        elif op == Z3_OP_GE:
            self.add_interval(str(var), Interval(rhs_value, INF))
        elif op == Z3_OP_GT:
            self.add_interval(str(var), Interval(rhs_value + 1, INF))
        elif op == Z3_OP_EQ:
            self.add_interval(str(var), Interval(rhs_value, rhs_value))
        else:
            assert False

    @staticmethod
    def _replace_distinct_with_ineq(lhs_value, rhs_value):
        if lhs_value > rhs_value:
            return Z3_OP_GT
        else:
            assert lhs_value < rhs_value
            return Z3_OP_LT

    def _strengthen_add(self, lhs_children, lhs_children_values, op, rhs_value, model):
        num_children = len(lhs_children)
        if op == Z3_OP_LE:
            lhs_value = sum(lhs_children_values)
            diff = rhs_value - lhs_value
            assert diff >= 0
            minimal_addition = diff // num_children
            extra_addition = diff - (minimal_addition * num_children)
            count_given_extra_addition = 0
            i = 0
            while count_given_extra_addition < extra_addition:
                value_i = lhs_children_values[i]
                self._strengthen_binary_boolean_conjunct(lhs_children[i], value_i, value_i + minimal_addition + 1, op, model)
                count_given_extra_addition += 1
                i += 1
            while i < num_children:
                value_i = lhs_children_values[i]
                self._strengthen_binary_boolean_conjunct(lhs_children[i], value_i, value_i + minimal_addition, op, model)
                i += 1
        elif op == Z3_OP_LT:
            self._strengthen_add(lhs_children, lhs_children_values, Z3_OP_LE, rhs_value - 1, model)
        elif op == Z3_OP_GE:
            lhs_value = sum(lhs_children_values)
            diff = lhs_value - rhs_value
            assert diff >= 0
            minimal_subtraction = diff // num_children
            extra_subtraction = diff - (minimal_subtraction * num_children)
            count_given_extra_subtraction = 0
            i = 0
            while count_given_extra_subtraction < extra_subtraction:
                value_i = lhs_children_values[i]
                self._strengthen_binary_boolean_conjunct(lhs_children[i], value_i, value_i - minimal_subtraction - 1, op,
                                                         model)
                count_given_extra_subtraction += 1
                i += 1
            while i < num_children:
                value_i = lhs_children_values[i]
                self._strengthen_binary_boolean_conjunct(lhs_children[i], value_i, value_i - minimal_subtraction, op,
                                                         model)
                i += 1
        elif op == Z3_OP_GT:
            self._strengthen_add(lhs_children, lhs_children_values, Z3_OP_GE, rhs_value + 1, model)
        elif op == Z3_OP_EQ:
            for i in range(0,num_children-1):
                self._strengthen_binary_boolean_conjunct(lhs_children[i], lhs_children_values[i], lhs_children_values[i], op, model)

    def get_unsimplified_formula(self):
        return And(self.unsimplified_demands)

    def print_all_solutions(self, limit=100):
        if len(self.unsimplified_demands) == 0:
            return self.interval_set.print_all_values(limit)
        elif self.interval_set.is_top():
            return print_all_models(self.get_unsimplified_formula(),limit)
        else:
            print("Printing all solutions of mixed demands anf intervals")
            interval_formula = self.interval_set.as_formula()
            f = And(interval_formula, self.get_unsimplified_formula())
            return print_all_models(f, limit)

    def _strengthen_mul_by_constant(self, constant, var, var_value, op, rhs_value, model):
        division_rounded_down = rhs_value // constant
        if constant > 0:
            should_round_up = (op == Z3_OP_GE or op == Z3_OP_GT) and rhs_value % constant != 0
            self._strengthen_binary_boolean_conjunct(var, var_value, division_rounded_down + should_round_up, op, model)
        elif constant < 0:
            reversed_op = reverse_operator(op)
            should_round_up = (reversed_op == Z3_OP_GE or reversed_op == Z3_OP_GT) and rhs_value % constant != 0
            self._strengthen_binary_boolean_conjunct(var, var_value, division_rounded_down + should_round_up, reversed_op, model)

    def _strengthen_binary_boolean_conjunct(self, lhs, lhs_value, rhs_value, op, model):
        if self.debug:
            print("Strnghening: " + str(lhs) + " " + binary_bool_op_to_string(op) + " " + str(rhs_value))
        if op == Z3_OP_DISTINCT:
            ineq_op = self._replace_distinct_with_ineq(lhs_value, rhs_value)
            self._strengthen_binary_boolean_conjunct(lhs, lhs_value, rhs_value, ineq_op, model)
            return
        if is_const(lhs):
            self._add_interval_for_binary_boolean(lhs, lhs_value, rhs_value, op)
        elif is_app_of(lhs, Z3_OP_UMINUS):
            arg0 = lhs.arg(0)
            self._strengthen_binary_boolean_conjunct(arg0, -lhs_value, -rhs_value, reverse_operator(op), model)
        elif is_app_of(lhs, Z3_OP_ADD):
            children_values = get_children_values(lhs, model)
            self._strengthen_add(lhs.children(), children_values, op, rhs_value, model)
        elif is_binary(lhs):
            lhs_arg0, lhs_arg1, lhs_arg0_val, lhs_arg1_val, lhs_op = evaluate_binary_expr(lhs, model)
            if lhs_op == Z3_OP_SUB:
                self._strengthen_add([lhs_arg0,-lhs_arg1],[lhs_arg0_val,-lhs_arg1_val], op, rhs_value, model)
            elif lhs_op == Z3_OP_MUL:
                if is_int_value(lhs_arg0) or is_uminus_on_int_value(lhs_arg0):
                    self._strengthen_mul_by_constant(lhs_arg0_val, lhs_arg1, lhs_arg1_val, op, rhs_value, model)
                elif is_int_value(lhs_arg1) or is_uminus_on_int_value(lhs_arg1):
                    self._strengthen_mul_by_constant(lhs_arg1_val, lhs_arg0, lhs_arg0_val, op, rhs_value, model)
            else:
                self.add_unsimplified_demand(build_binary_expression(lhs, IntVal(rhs_value), op))
        else:
            self.add_unsimplified_demand(build_binary_expression(lhs, IntVal(rhs_value), op))


def strengthen(f, model, debug = False):
    res = StrenghenedFormula(debug)
    f_as_and = remove_or(f, model)
    if debug:
        print("f_as_and: "+str(f_as_and))
    if is_and(f_as_and):
        for c in f_as_and.children():
            res._strengthen_conjunct(c, model)
    else: # f_is_and is an atomic boolean constraint
        res._strengthen_conjunct(f_as_and, model)
    return res


def remove_or(f, guiding_model):
    goal = Goal()
    goal.add(f)
    t_1 = Tactic('nnf')
    # nnf_formula = t_1(goal).as_expr()
    nnf_formula = Then(t_1,With('simplify',arith_lhs=True))(goal).as_expr()
    res = _remove_or_aux(nnf_formula,guiding_model)
    return res


def _remove_or_aux(nnf_formula, guiding_model):
    # Every sub-formula that isn't an 'or' or an 'and' stops the recursion.
    # We assume conversion to nnf already removed other operators, such as Implies, Ite, etc.
    if not is_or(nnf_formula) and not is_and(nnf_formula):
        return nnf_formula
    # Step cases:
    if is_or(nnf_formula):
        for c in nnf_formula.children():
            if is_true(guiding_model.evaluate(c)):
                return _remove_or_aux(c, guiding_model)
        assert False
    else:
        assert is_and(nnf_formula)
        new_children=[]
        for c in nnf_formula.children():
            new_children.append(_remove_or_aux(c,guiding_model))
        return And(new_children)