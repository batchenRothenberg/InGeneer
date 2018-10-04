import sys

MINF = "minf"
INF = "inf"
MAXINT = sys.maxsize
MININT = -sys.maxsize - 1
_UBOT = u'\u27d8'.encode("utf-8")
_UTOP = u'\u27d9'.encode("utf-8")
_UINF = u'\u221E'.encode("utf-8")
_UIN = u'\u220A'.encode("utf-8")


def inf_str_to_number(st):
    assert isinstance(st, str) and (st == INF or st == MINF)
    if st == INF:
        return MAXINT
    else:
        return MININT


class IntervalBorder:

    def __init__(self, n):
        assert (isinstance(n, int) or n == MINF or n == INF)
        self.n = n

    def __str__(self):
        if isinstance(self.n, int):
            return str(self.n)
        if self.n == MINF:
            return "-" + _UINF
        return _UINF

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(self.n, int):
            if isinstance(other, int):
                return self.n == other
            elif isinstance(other, IntervalBorder) and isinstance(other.n, int):
                return self.n == other.n
            else:
                return False
        else:
            assert self.n == MINF or self.n == INF
            if isinstance(other, str):
                return self.n == other
            elif isinstance(other, IntervalBorder) and isinstance(other.n, str):
                return self.n == other.n
            else:
                return False

    def __ne__(self, other):
        return not __eq__(self, other)

    def __lt__(self, other):
        assert (isinstance(other, int) or isinstance(other, IntervalBorder) or other == MINF or other == INF)
        if (isinstance(other, str) and other == MINF) or (isinstance(other, IntervalBorder) and other.n == MINF):
            return False
        if isinstance(self.n, str) and self.n == MINF:
            return True
        if isinstance(self.n, str) and self.n == INF:
            return False
        if (isinstance(other, str) and other == INF) or (isinstance(other, IntervalBorder) and other.n == INF):
            return True
        assert isinstance(self.n, int) and (isinstance(other, int) or isinstance(other, IntervalBorder))
        if isinstance(other, int):
            return self.n < other
        else:
            return self.n < other.n

    def __gt__(self, other):
        assert (isinstance(other, int) or isinstance(other, IntervalBorder) or other == MINF or other == INF)
        if isinstance(other, str) and other == INF:
            return False
        if isinstance(self.n, str) and self.n == INF:
            return True
        if isinstance(self.n, str) and self.n == MINF:
            return False
        if isinstance(other, str) and other == MINF:
            return True
        assert isinstance(self.n, int) and (isinstance(other, int) or isinstance(other, IntervalBorder))
        if isinstance(other, int):
            return self.n > other
        else:
            return self.n > other.n

    def __le__(self, other):
        return __lt__(self, other) or __eq__(self, other)

    def __ge__(self, other):
        return __gt__(self, other) or __eq__(self, other)

    def is_inf(self):
        return isinstance(self.n, str) and self.n == INF

    def is_minf(self):
        return isinstance(self.n, str) and self.n == MINF

    def __radd__(self, other):
        other_is_int = isinstance(other, int)
        self_is_int = isinstance(self.n, int)
        assert (other_is_int or other == MINF or other == INF)

        # Can't add MINF to INF and vice versa
        assert not (not other_is_int and not self_is_int and self.n == INF and other == MINF)
        assert not (not other_is_int and not self_is_int and self.n == MINF and other == INF)

        if (not self_is_int and self.n == MINF) or (not other_is_int and other == MINF):
            return inf_str_to_number(MINF)
        if (not self_is_int and self.n == INF) or (not other_is_int and other == INF):
            return inf_str_to_number(INF)
        else:
            return self.n + other

    def add(self, other):
        assert isinstance(other, IntervalBorder)
        return self.n + other

    def __neg__(self):
        if isinstance(self.n, int):
            return -self.n
        elif self.n == INF:
            return -inf_str_to_number(INF)
        else:
            return inf_str_to_number(INF)


class Interval:

    # def __init__(self, low, high):
    #     assert (isinstance(low, int) or isinstance(low, IntervalBorder) or low == MINF)
    #     assert (isinstance(high, int) or isinstance(high, IntervalBorder) or high == INF)
    #     if isinstance(low, IntervalBorder):
    #         self.low = IntervalBorder(low.n)
    #     else:
    #         self.low = IntervalBorder(low)
    #     if isinstance(high, IntervalBorder):
    #         self.high = IntervalBorder(high.n)
    #     else:
    #         self.high = IntervalBorder(high)

    def __init__(self, low, high):
        assert (isinstance(low, int) or low == MINF)
        assert (isinstance(high, int) or high == INF)
        self.low = IntervalBorder(low)
        self.high = IntervalBorder(high)

    def __str__(self):
        l = str(self.low)
        h = str(self.high)
        if self.is_bottom():
            return u'\u27C2'
        return "[" + l + "," + h + "]"

    def __repr__(self):
        return str(self)

    def is_bottom(self):
        return self.high < self.low

    def is_top(self):
        return self.low.is_minf() and self.high.is_inf()

    def is_infinite(self):
        return self.low.is_minf() or self.high.is_inf()

    def __len__(self):
        if self.is_bottom():
            return 0
        elif self.is_infinite():
            return inf_str_to_number(INF)
        else:
            assert isinstance(self.low.n, int) and isinstance(self.high.n, int)
            return self.high.n - self.low.n

    def len_string(self):
        if self.is_infinite():
            return INF
        else:
            return str(len(self))

    @staticmethod
    def intersection(intervals):
        max_low = max([i.low for i in intervals])
        min_high = min([i.high for i in intervals])
        return Interval(max_low.n, min_high.n)

    def __eq__(self, other):
        return self.low == other.low and self.high == other.high

    def __ne__(self, other):
        return not __eq__(self, other)


class IntervalSet:

    def __init__(self, intervals):
        self.dict = intervals

    def __str__(self):
        if self.is_top():
            return _UTOP
        if self.is_bottom():
            return _UBOT
        res = ""
        for k in self.dict.keys():
            v = self.dict[k]
            res = res + str(k) + ":" + str(v) + " "
        return res

    def __repr__(self):
        return str(self)

    def is_top(self):
        return len(self.dict) == 0

    def is_bottom(self):
        return any([v.is_bottom() for v in self.dict.values()])

    @staticmethod
    def get_top():
        return IntervalSet({})

    @staticmethod
    def get_bottom():
        return IntervalSet({"bottom_var":Interval(4, 3)})

    def intersect(self, other):
        """
        The result of the intersection of self and other is stored in self
        :param other: another @IntervalSet to perform intersection with
        :return: None
        """
        for var in other.dict.keys():
            if var in self.dict.keys():
                self.dict[var] = Interval.intersection([self.dict[var],other.dict[var]])
            else:
                self.dict[var] = other.dict[var]

    @staticmethod
    def intersection(intervalsets):
        res = IntervalSet.get_top()
        for intervalset in intervalsets:
            res.intersect(intervalset)
        return res

    def __eq__(self, other):
        return self.dict == other.dict

    def __ne__(self, other):
        return not __eq__(self, other)


def max_of_two_with_minf(n, m):
    if isinstance(n, str):
        assert n == MINF
        return m
    elif isinstance(m, str):
        assert m == MINF
        return n
    else:
        assert isinstance(n, int) and isinstance(m, int)
        if n > m:
            return n
        else:
            return m


def max_with_minf(numbers):
    max = MINF
    for n in numbers:
        max = max_of_two_with_minf(max, n)
    return max


def min_of_two_with_inf(n, m):
    if isinstance(n, str):
        assert n == INF
        return m
    elif isinstance(m, str):
        assert m == INF
        return n
    else:
        # assert isinstance(n, int) and isinstance(m, int)
        if n < m:
            return n
        else:
            return m


def min_with_inf(numbers):
    min = INF
    for n in numbers:
        min = min_of_two_with_inf(min, n)
    return min

