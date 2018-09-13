from abc import ABC, abstractmethod

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
    pass


class TopologicalSort(ABC):

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


