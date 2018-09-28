from abc import ABCMeta, abstractmethod

from z3 import *

class Stmt:
    __metaclass__ = ABCMeta

    def __init__(self, expr):
        self.expr = expr

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def is_assignment(self):
        pass

    @abstractmethod
    def is_condition(self):
        pass


class AssignmentStmt(Stmt):

    def __init__(self,expr):
        assert (is_eq(expr))
        self.lhs = expr.arg(0)
        self.rhs = expr.arg(1)
        super().__init__(expr)

    def __str__(self):
        return self.lhs.__str__() + " := " + self.rhs.__str__()

    def __repr__(self):
        return self.__str__()

    def is_condition(self):
        return False

    def is_assignment(self):
        return True


class ConditionStmt(Stmt):
    op = Z3_OP_EQ
    expr = True

    def __init__(self,expr):
        assert (is_bool(expr))
        if expr.num_args() < 2:
            print("error")
        self.op = expr.decl()
        super().__init__(expr)

    def __str__(self):
        return "[[" + self.expr.__str__() + "]]"

    def __repr__(self):
        return self.__str__()

    def is_condition(self):
        return True

    def is_assignment(self):
        return False
