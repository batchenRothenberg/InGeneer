from generalizer import Generalizer
from stmt import *


class IPGeneralizer(Generalizer):

    def __init__(self,trace,input = None, record_annotation = False, initial_formula=True):
        super().__init__(trace,record_annotation,initial_formula)
        self.input = input

    def do_step(self,I, st):
        print("doing interval w.p. step with ", I, " and ", st)
        if isinstance(st, AssignmentStmt):
            return self.interval_assignment_wp_step(I, st)
        else:
            assert isinstance(st, ConditionStmt)
            return self.interval_condition_wp_step(I, st)

    def interval_assignment_wp_step(self, I, st):
        pass

    def interval_condition_wp_step(self, I, st):
        pass