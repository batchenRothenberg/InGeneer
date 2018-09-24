from abc import ABCMeta, abstractmethod


class Domain:
    __metaclass__ = ABCMeta

    @abstractmethod
    def do_step(self, formula, stmt):
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