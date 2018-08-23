import sys

MINF = "minf"
INF = "inf"
_UBOT = u'\u27D8'
_UTOP = u'\u27D9'
_UINF = u'\u221E'
_UIN = u'\u220A'


class Interval:

    def __init__(self, var, low, high):
        assert (isinstance(low, int) or low == MINF)
        assert (isinstance(high, int) or high == INF)
        self.low = low
        self.high = high
        self.var = var

    def __str__(self):
        l = str(self.low)
        h = str(self.high)
        if self.low == MINF:
            l = "-" + _UINF
        if self.high == INF:
            h = _UINF
        if self.is_bottom():
            return self.var + _UIN + u'\u27C2'
        return self.var + _UIN + "[" + l + "," + h + "]"

    def __repr__(self):
        return str(self)

    def is_bottom(self):
        return isinstance(self.low, int) and isinstance(self.high, int) and self.high < self.low

    def is_top(self):
        return self.low == MINF and self.high == INF

    def is_infinite(self):
        return self.low == MINF or self.high == INF

    def __len__(self):
        if self.is_bottom():
            return 0
        if isinstance(self.low, int) and isinstance(self.high, int):
            return self.high - self.low
        assert (self.is_infinite())
        return sys.maxsize

    def len_string(self):
        if self.is_infinite():
            return INF
        else:
            return len(self)


class IntervalSet:

    def __init__(self, intervals):
        self.dict = {i.var: i for i in intervals if not i.is_top()}

    def __str__(self):
        if self.is_top():
            return _UTOP
        if self.is_bottom():
            return _UBOT
        res = ""
        for v in self.dict.values():
            res = res + str(v) + " "
        return res

    def __repr__(self):
        return str(self)

    def is_top(self):
        return len(self.dict) == 0

    def is_bottom(self):
        return any([v.is_bottom() for v in self.dict.values()])