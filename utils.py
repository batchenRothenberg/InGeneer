import csv
import timeit
from abc import ABCMeta, abstractmethod

from z3 import *
import formula_strengthener


# Wrapper for allowing Z3 ASTs to be stored into Python Hashtables.
class AstRefKey:
    def __init__(self, n):
        self.n = n

    def __hash__(self):
        return self.n.hash()

    def __eq__(self, other):
        return self.n.eq(other.n)

    def __repr__(self):
        return str(self.n)


def askey(n):
    assert isinstance(n, AstRef)
    return AstRefKey(n)


def get_vars(f):
    r = set()

    def collect(f):
        if is_const(f):
            if f.decl().kind() == Z3_OP_UNINTERPRETED and not askey(f) in r:
                r.add(askey(f))
        else:
            for c in f.children():
                collect(c)

    collect(f)
    return r


def get_vars_and_coefficients(f):
    """Returns a dictionary mapping each variable to its coefficient in f
    (f should be a linear combination of int variables)"""
    r = {}

    def collect(f):
        if is_mul(f):
            assert is_int_value(f.arg(0))
            assert f.arg(1).decl().kind() == Z3_OP_UNINTERPRETED
            if not askey(f.arg(1)) in r.keys():
                r[askey(f.arg(1))]=f.arg(0)
        elif f.decl().kind() == Z3_OP_UNINTERPRETED and not askey(f) in r:
            r[askey(f)] = 1
        else:
            for c in f.children():
                collect(c)

    collect(f)
    return r


def negate_condition(cond):
    if cond.num_args() < 2:
        print("WARNING: could not negate condition "+str(cond))
        return cond
    else:
        arg0 = cond.arg(0)
        arg1 = cond.arg(1)
        if is_le(cond):
            return arg0 > arg1
        if is_lt(cond):
            return arg0 >= arg1
        if is_ge(cond):
            return arg0 < arg1
        if is_gt(cond):
            return arg0 <= arg1
        if is_eq(cond):
            return arg0 != arg1
        if is_distinct(cond):
            return arg0 == arg1
        else:
            print("WARNING: could not negate condition " + str(cond))
            return cond


def is_binary_boolean(c):
    return is_lt(c) or is_le(c) or is_gt(c) or is_ge(c) or is_eq(c) or is_distinct(c)


def is_binary(expr):
    return len(expr.children()) == 2


def is_uminus_on_int_value(expr):
    return is_app_of(expr,Z3_OP_UMINUS) and is_int_value(expr.arg(0))


def evaluate_binary_expr(expr, model):
    assert len(expr.children()) == 2
    arg0 = expr.arg(0)
    arg1 = expr.arg(1)
    arg1_value = model.evaluate(arg1).as_long()
    arg0_value = model.evaluate(arg0).as_long()
    op = expr.decl().kind()
    return arg0, arg1, arg0_value, arg1_value, op


def build_binary_expression(lhs, rhs, op):
    if op == Z3_OP_LE:
        return lhs <= rhs
    elif op == Z3_OP_LT:
        return lhs < rhs
    elif op == Z3_OP_GE:
        return lhs >= rhs
    elif op == Z3_OP_GT:
        return lhs > rhs
    elif op == Z3_OP_EQ:
        return lhs == rhs
    elif op == Z3_OP_DISTINCT:
        return lhs != rhs
    elif op == Z3_OP_ADD:
        return lhs + rhs
    elif op == Z3_OP_SUB:
        return lhs - rhs
    elif op == Z3_OP_MUL:
        return lhs * rhs
    elif op == Z3_OP_DIV:
        return lhs / rhs
    else:
        print("warning Unssoported operator")
        return None


def binary_bool_op_to_string(op):
    if op == Z3_OP_LE:
        return "<="
    elif op == Z3_OP_LT:
        return "<"
    elif op == Z3_OP_GE:
        return ">="
    elif op == Z3_OP_GT:
        return ">"
    elif op == Z3_OP_EQ:
        return "=="
    elif op == Z3_OP_DISTINCT:
        return "!="
    else:
        print("warning Unssoported operator")
        return None


def reverse_operator(op):
    if op == Z3_OP_LE:
        return Z3_OP_GE
    elif op == Z3_OP_LT:
        return Z3_OP_GT
    elif op == Z3_OP_GE:
        return Z3_OP_LE
    elif op == Z3_OP_GT:
        return Z3_OP_LT
    elif op == Z3_OP_EQ:
        return Z3_OP_EQ
    elif op == Z3_OP_DISTINCT:
        return Z3_OP_DISTINCT
    else:
        print("warning Unssoported operator")
        return None


def simplify_and_propagate_ineqs(f):
    goal = Goal()
    goal.add(f)
    t_1 = Tactic('simplify')
    t_2 = Tactic('propagate-ineqs')
    t = Then(t_1,t_2)
    return t(goal).as_expr()


def print_all_models(f, limit=10000):
    s = Solver()
    s.add(f)
    count = 0
    while count < limit and s.check() == sat:
        count += 1
        m = s.model()
        print(m)
        s.add(get_formula_from_model(m))
    if count == limit:
        print("max number of models reached")
    return count


# From: https://stackoverflow.com/questions/11867611/z3py-checking-all-solutions-for-equation
def get_formula_from_model(model):
    block = []
    for d in model:
        # d is a declaration
        if d.arity() > 0:
            raise Z3Exception("uninterpreted functions are not supported")
        # create a constant from declaration
        c = d()
        if is_array(c) or c.sort().kind() == Z3_UNINTERPRETED_SORT:
            raise Z3Exception("arrays and uninterpreted sorts are not supported")
        block.append(c != model[d])
    # print(Or(block))
    return (Or(block))


def get_children_values(expr, model):
    res = []
    for c in expr.children():
        res.append(model.evaluate(c).as_long())
    return res


def remove_or(f, guiding_model):
    goal = Goal()
    goal.add(f)
    t = Tactic('nnf')
    nnf_formula = t(goal).as_expr()
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


def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped


def strengthen_formula_test(f, file = None, debug = False):
    s = Solver()
    s.add(f)
    s.check()
    m = s.model()
    r = formula_strengthener.strengthen(f, m, debug=debug)
    wrapped = wrapper(formula_strengthener.strengthen, f, m)
    stren_time = timeit.timeit(wrapped, number=1)
    res_ten_sol_stren_f, ten_sol_stren_f_time = timed(r.print_all_solutions)(10)
    res_ten_sol_f, ten_sol_f_time = timed(print_all_models)(f,10)
    res_hundred_sol_stren_f, hundred_sol_stren_f_time = timed(r.print_all_solutions)(100)
    res_hundred_sol_f, hundred_sol_f_time = timed(print_all_models)(f,100)
    res_huge_sol_stren_f, huge_sol_stren_f_time = timed(r.print_all_solutions)(10000)
    res_huge_sol_f, huge_sol_f_time = timed(print_all_models)(f,10000)

    if file is None:
        print("f is: " + str(f))
        print("strengthened f: " + str(r))
        print("time to strengthen f: " + str(stren_time))
        print("time to find first 10 solutions of strengthened f: " + str(ten_sol_stren_f_time))
        print("number of solutions found: " + str(res_ten_sol_stren_f))
        print("time to find first 10 solutions of f: " + str(ten_sol_f_time))
        print("number of solutions found: " + str(res_ten_sol_f))
        print("time to find first 100 solutions of strengthened f: " + str(hundred_sol_stren_f_time))
        print("number of solutions found: " + str(res_hundred_sol_stren_f))
        print("time to find first 100 solutions of f: " + str(hundred_sol_f_time))
        print("number of solutions found: " + str(res_hundred_sol_f))
        print("time to find first 10000 solutions of strengthened f: " + str(huge_sol_stren_f_time))
        print("number of solutions found: " + str(res_huge_sol_stren_f))
        print("time to find first 10000 solutions of f: " + str(huge_sol_f_time))
        print("number of solutions found: " + str(res_huge_sol_f))

    else:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow([str(f),
                         str(r),
                         str(stren_time),
                         str(ten_sol_stren_f_time),
                         str(ten_sol_f_time),
                         str(hundred_sol_stren_f_time),
                         str(hundred_sol_f_time),
                         str(huge_sol_stren_f_time),
                         str(huge_sol_f_time)
                         ])


def timed(func):
    def func_wrapper(*args, **kwargs):
        import time
        s = time.clock()
        result = func(*args, **kwargs)
        e = time.clock()
        return result, e-s
    return func_wrapper


def open_file(file):
    ofile = open(file, "wb")
    return ofile


def close_file(ofile):
    ofile.close()


class TopologicalSort():
    __metaclass__ = ABCMeta

    def __init__(self,root):
        self.root = root

    @abstractmethod
    def get_children(self, node):
        pass

    @abstractmethod
    def process(self, node):
        pass

    def _sort_aux(self, node, visited, res):
        visited.append(node)
        for child in self.get_children(node):
            if child not in visited:
                self._sort_aux(child, visited, res)
        res.insert(0,self.process(node))

    def sort(self):
        """
        Returns a topological sort of the graph beginning in root,
        when all edges are reversed (i.e., root should be the last).
        the children of each node in the graph are determined by @get_children_func(node).
        :return: a list of node representations, ordered according to the topological sort found.
        The representation of a node is determined by @process_func(node).
        """
        res = []
        self._sort_aux(self.root, [], res)
        return res


