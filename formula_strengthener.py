from z3 import is_and

from interval import IntervalSet
from utils import remove_or


class StrenghenedFormula():

    def __init__(self):
        self.unsimplified_demands = []
        self.interval_set = IntervalSet.get_top()

    def add_unsimplified_demand(self, demand):
        self.unsimplified_demands.append(demand)

    def __str__(self):
        return "unsimplified demands: " + str(self.unsimplified_demands) + " Interval set: " + str(self.interval_set)

    def __repr__(self):
        return str(self)


def strengthen(f, model):
    res = StrenghenedFormula()
    f_as_and = remove_or(f, model)
    print("f_as_and: "+str(f_as_and))
    if is_and(f_as_and):
        for c in f_as_and.children():
            strength_res = strengthen_conjunct(c, model)
            if not strength_res:
                res.add_unsimplified_demand(c)
    else: # f_is_and is an atomic boolean constraint
        strength_res = strengthen_conjunct(f_as_and, model)
        if not strength_res:
            res.add_unsimplified_demand(f_as_and)
    return res


def strengthen_conjunct(conjunct, model):
    return False
