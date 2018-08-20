from z3 import *


class AssignmentStmt:

    def __init__(self,expr):
        assert (is_eq(expr))
        self.lhs = expr.arg(0)
        self.rhs = expr.arg(1)
        self.expr = expr

    def __str__(self):
        return self.lhs.__str__() + " := " + self.rhs.__str__()

    def __repr__(self):
        return self.__str__()


class ConditionStmt:
    op = Z3_OP_EQ
    expr = True

    def __init__(self,expr):
        assert (is_bool(expr))
        if expr.num_args() < 2:
            print("error")
        self.expr = expr
        self.op = expr.decl()

    def __str__(self):
        return "[[" + self.expr.__str__() + "]]"

    def __repr__(self):
        return self.__str__()
