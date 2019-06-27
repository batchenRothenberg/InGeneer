
class Generalizer:

    def __init__(self, domain, debug=False):
        self.domain = domain
        self.annotation = []
        self.safe_statements_set = set()
        self.debug = debug

    def generalize_input(self, trace, initial_formula="default", model = None, record_annotation=False, print_annotation=False):
        return self._generalize(trace, initial_formula, model, self.domain.do_step, record_annotation, print_annotation)

    def generalize_trace(self, multitrace, initial_formula="default", model = None, record_annotation=False, print_annotation=False):
        self.safe_statements_set = set()
        self._generalize(multitrace, initial_formula, model, self.do_group_step, record_annotation, print_annotation)
        if self.debug:
            print("Safe statements: "+str(self.safe_statements_set))
        return self.safe_statements_set

    def _generalize(self, abstract_trace, initial_formula, model, step_function, record_annotation, print_annotation):
        if str(initial_formula) == "default":
            initial_formula = self.domain.get_top()
        formula = initial_formula
        if print_annotation or self.debug:
            print(formula)
        if record_annotation:
            self.annotation.append(formula)
        for stmt in abstract_trace:
            if print_annotation or self.debug:
                print("Doing step with "+str(stmt))
            formula = step_function(formula,stmt, model)
            if print_annotation or self.debug:
                print(formula)
            if record_annotation:
                self.annotation.append(formula)
        return formula

    def get_annotation(self):
        return self.annotation

    def do_group_step(self, formula, group, model):
        formulas = []
        for stmt in group:
            if self.debug:
                print("Doing group step with "+str(stmt))
            if self.domain.does_step_lead_to_state_in_model(formula, stmt, model):
                formula_i = self.domain.do_step(formula,stmt, model)
                formulas.append(formula_i)
                if self.debug:
                    print("Stmt is sat. formula_i is: "+str(formula_i))
            else:
                self.safe_statements_set.add(stmt)
                if self.debug:
                    print("Stmt isn't sat.")
        chosen_indices, unchosen_indices = self.domain.choose(formulas, model)
        chosen_formulas = [formulas[i] for i in chosen_indices]
        unselected_stmts = [group[i] for i in unchosen_indices]
        self.safe_statements_set.update(unselected_stmts)
        if chosen_formulas == []:
            return self.domain.get_bottom()
        return self.domain.intersection(chosen_formulas)
