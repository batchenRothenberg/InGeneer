from abc import ABCMeta, abstractmethod

from z3 import *


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


def simplify_and_propagate_ineqs(f):
    goal = Goal()
    goal.add(f)
    t_1 = Tactic('simplify')
    t_2 = Tactic('propagate-ineqs')
    t = Then(t_1,t_2)
    return t(goal).as_expr()


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


