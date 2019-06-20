from abc import ABCMeta, abstractmethod


class Domain:
    __metaclass__ = ABCMeta

    @abstractmethod
    def do_step(self, formula, stmt, model):
        pass

    @abstractmethod
    def does_step_lead_to_state_in_model(self, formula, stmt, model):
        pass

    @abstractmethod
    def is_bottom(self, formula):
        pass

    @abstractmethod
    def is_top(self, formula):
        pass

    @abstractmethod
    def intersection(self, formulas):
        pass

    @abstractmethod
    def get_top(self):
        pass

    @abstractmethod
    def get_bottom(self):
        pass

    @abstractmethod
    def choose(self, formulas, model):
        """Sould split the indices of formulas list (0...len(formulas)-1) into two lists:
        chosen indices - a list of indices of all formulas that are chosen.
        unchosen indices - a list of indices of all formulas that are left out.
        Both lists should be returned as a tuple (chosen_indices,unchosen_indices).
        """
        pass