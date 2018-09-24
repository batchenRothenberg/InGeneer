
class Generalizer:

    def __init__(self, domain):
        self.domain = domain
        self.annotation = []
        self.selected_multitrace = []

    def generalize_input(self, trace, initial_formula="default", record_annotation=False, print_annotation=False):
        return self._generalize(trace, initial_formula, self.domain.do_step, record_annotation, print_annotation)

    def generalize_trace(self, multitrace, initial_formula="default", record_annotation=False, print_annotation=False):
        self.selected_multitrace = []
        self._generalize(multitrace, initial_formula, self.do_group_step, record_annotation, print_annotation)
        return self.selected_multitrace

    def _generalize(self, abstract_trace, initial_formula, step_function, record_annotation, print_annotation):
        if initial_formula == "default":
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
        selected_stmts = []
        for stmt in group:
            formula_i = self.domain.do_step(formula,stmt)
            if not self.domain.is_bottom(formula_i):
                formulas.append(formula_i)
                selected_stmts.append(stmt)
        self.selected_multitrace.append(selected_stmts)
        if formulas == []:
            return self.domain.get_bottom()
        return self.domain.intersection(formulas)
