from abc import ABCMeta, abstractmethod


class Trace():
    __metaclass__ = ABCMeta

    def __init__(self,tr):
        self.trace = tr

    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        return self.__str__()

    def get_curr(self):
        return self.curr

    def get_trace(self):
        return self.trace

    def __iter__(self):
        return self

    @abstractmethod
    def __next__(self):
        pass

    def next(self):
        return self.__next__()


class ForwardTrace(Trace):

    def __init__(self,tr):
        super(ForwardTrace, self).__init__(tr)
        self.curr = 1

    def __str__(self):
        res = ""
        i = 1
        for stmt in self.trace:
            res = res + str(i) + ". " + str(self.trace[i - 1]) + "\n"
            i = i + 1
        return res

    def __next__(self):
        if self.curr == len(self.trace) + 1:
            self.curr = 1
            raise StopIteration
        else:
            self.curr += 1
            return self.trace[self.curr - 1 - 1] # previous value, zero based


class BackwardTrace(Trace):

    def __init__(self,tr):
        super(BackwardTrace, self).__init__(tr)
        self.curr = len(tr)

    def __str__(self):
        res = ""
        i = len(self.trace)
        while i >= 1:
            res = res + str(i) + ". " + str(self.trace[i - 1]) + "\n"
            i = i - 1
        return res

    def __next__(self):
        if self.curr == 0:
            self.curr = len(self.trace)
            raise StopIteration
        else:
            self.curr -= 1
            return self.trace[self.curr + 1 - 1] # previous value, zero based
