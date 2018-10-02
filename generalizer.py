
class Generalizer:

    def __init__(self, domain):
        self.domain = domain
        self.annotation = []
        self.safe_statements_set = {}

    def generalize_input(self, trace, initial_formula="default", record_annotation=False, print_annotation=False):
        return self._generalize(trace, initial_formula, self.domain.do_step, record_annotation, print_annotation)

    def generalize_trace(self, multitrace, initial_formula="default", record_annotation=False, print_annotation=False):
        self.safe_statements_set = {}
        self._generalize(multitrace, initial_formula, self.do_group_step, record_annotation, print_annotation)
        return self.safe_statements_set

    def _generalize(self, abstract_trace, initial_formula, step_function, record_annotation, print_annotation):
        if str(initial_formula) == "default":
            initial_formula = self.domain.get_top()
        formula = initial_formula
        if print_annotation:
            print(formula)
        if record_annotation:
            self.annotation.append(formula)
        for stmt in abstract_trace:
            formula = step_function(formula,stmt)
            if print_annotation:
                print(formula)
            if record_annotation:
                self.annotation.append(formula)
        return formula

    def get_annotation(self):
        return self.annotation

    def do_group_step(self, formula, group):
        formulas = []
        for stmt in group:
            formula_i = self.domain.do_step(formula,stmt)
            if self.domain.is_bottom(formula_i):
                self.safe_statements_set.add(stmt)
            else:
                formulas.append(formula_i)
        if formulas == []:
            return self.domain.get_bottom()
        return self.domain.intersection(formulas)
