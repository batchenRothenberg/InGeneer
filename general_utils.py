from abc import ABCMeta, abstractmethod
import csv


def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped


def timed(func):
    def func_wrapper(*args, **kwargs):
        import time
        s = time.clock()
        result = func(*args, **kwargs)
        e = time.clock()
        return result, e-s
    return func_wrapper


def open_file(file):
    ofile = open(file, "wb")
    return ofile


def close_file(ofile):
    ofile.close()


class TopologicalSort():
    __metaclass__ = ABCMeta

    def __init__(self,root):
        self.root = root

    @abstractmethod
    def get_children(self, node):
        pass

    @abstractmethod
    def process(self, node):
        pass

    def _sort_aux(self, node, visited, res):
        visited.append(node)
        for child in self.get_children(node):
            if child not in visited:
                self._sort_aux(child, visited, res)
        res.insert(0,self.process(node))

    def sort(self):
        """
        Returns a topological sort of the graph beginning in root,
        when all edges are reversed (i.e., root should be the last).
        the children of each node in the graph are determined by @get_children_func(node).
        :return: a list of node representations, ordered according to the topological sort found.
        The representation of a node is determined by @process_func(node).
        """
        res = []
        self._sort_aux(self.root, [], res)
        return res


