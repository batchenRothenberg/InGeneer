from abc import ABC, abstractmethod


class Generalizer(ABC):

    annotation = []

    def __init__(self,trace,record_annotation,initial_formula=True):
        self.trace = trace
        self.initial_formula = initial_formula
        assert record_annotation==True or record_annotation==False
        self.record_annotation = record_annotation

    def generalize(self):
        formula = self.initial_formula
        print(formula)
        if self.record_annotation:
            self.annotation.append(formula)
        for stmt in self.trace:
            formula = self.do_step(formula,stmt)
            print(formula)
            if self.record_annotation:
                self.annotation.append(formula)
        return formula

    @abstractmethod
    def do_step(self,formula,stmt):
        pass

    def get_annotation(self):
        return self.annotation