from collections import defaultdict

from precise_domain import *
from interval_domain import *
from z3 import *
from interval import *
from stmt import *
from trace import *
from utils import *
from generalizer import Generalizer

x = Int('x')
y = Int('y')
z = Int('z')
c_1_0 = ConditionStmt(x + y >= 8)
c_1_1 = ConditionStmt(x - y >= 8)
c_1_2 = ConditionStmt(x + y > 8)
c_1_3 = ConditionStmt(x + y < 8)
a_1_0 = AssignmentStmt(z == x + y)
a_1_1 = AssignmentStmt(z == x - y)
c_2_0 = ConditionStmt(x >= 0)
c_2_1 = ConditionStmt(x > 0)
c_2_2 = ConditionStmt(x < 0)
c_3_0 = ConditionStmt(z >= 9)
c_3_1 = ConditionStmt(z > 9)
c_3_2 = ConditionStmt(z < 9)
a_2_0 = AssignmentStmt(z == z - 1)
a_2_1 = AssignmentStmt(z == z + 1)
c_4_0 = ConditionStmt(z <= 8)
a_3_0 = AssignmentStmt(z == 9)
a_4_0 = AssignmentStmt(x == x - 1)
a_4_1 = AssignmentStmt(x == x + 1)
a_5_0 = AssignmentStmt(z == z + 3)
a_5_1 = AssignmentStmt(z == z - 3)
tr_TFT = BackwardTrace([c_1_0, a_1_0, c_2_2, c_3_0, a_2_0, c_4_0])
mt_TFT = BackwardTrace([[c_1_0, c_1_1, c_1_2, c_1_3], [a_1_0, a_1_1], [c_2_0,c_2_1,c_2_2], [c_3_0,c_3_1,c_3_2], [a_2_0,a_2_1], [c_4_0]])

I = IntervalSet({"x": Interval(3, 7), "y": Interval(-3, 17)})
I_1 = IntervalSet({"x": Interval(3, 7)})
interval_domain = IntervalDomain()
interval_generalizer = Generalizer(interval_domain, debug=True)
wp_domain = PreciseDomain()
wp_generalizer = Generalizer(wp_domain, debug=True)


def test_interval():
    i_1 = Interval(3, 5)
    i_2 = Interval(-2, 6)
    i_3 = Interval("minf", "inf")
    i_4 = Interval("minf", 7)
    i_5 = Interval(-5, "inf")
    i_6 = Interval(-5, -10)
    i_7 = Interval(5, 0)
    assert not i_1.is_bottom()
    assert not i_2.is_bottom()
    assert not i_3.is_bottom()
    assert not i_4.is_bottom()
    assert not i_5.is_bottom()
    assert i_6.is_bottom()
    assert i_7.is_bottom()
    assert not i_1.is_top()
    assert not i_2.is_top()
    assert i_3.is_top()
    assert not i_4.is_top()
    assert not i_5.is_top()
    assert not i_6.is_top()
    assert not i_7.is_top()
    assert len(i_1) == 2
    assert len(i_2) == 8
    assert len(i_3) == MAXINT
    assert len(i_4) == MAXINT
    assert len(i_5) == MAXINT
    assert len(i_6) == 0
    assert len(i_7) == 0
    assert i_1.len_string() == "2"
    assert i_2.len_string() == "8"
    assert i_3.len_string() == INF
    assert i_4.len_string() == INF
    assert i_5.len_string() == INF
    assert i_6.len_string() == "0"
    assert i_7.len_string() == "0"
    assert not i_1.is_infinite()
    assert not i_2.is_infinite()
    assert i_3.is_infinite()
    assert i_4.is_infinite()
    assert i_5.is_infinite()
    assert not i_6.is_infinite()
    assert not i_7.is_infinite()
    assert i_6 == i_7
    assert i_2 == i_2
    assert i_4 == i_4
    assert i_1 != i_2
    assert i_3 != i_4
    assert i_3 != i_6
    assert Interval.intersection([i_1,i_2]) == i_1
    assert i_1 == Interval.intersection([i_1,i_2])
    assert Interval.intersection([i_6, i_7]) == i_6
    assert Interval.intersection([i_6, i_7]) == i_7
    assert Interval.intersection([i_6, i_1]) == i_6
    assert Interval.intersection([i_4, i_7]) == i_6
    assert Interval.intersection([i_1, i_2, i_3]) == i_1
    assert Interval.intersection([i_4, i_6, i_1]) == i_6
    assert Interval.intersection([i_2, i_3, i_5]) == i_2
    assert Interval.intersection([i_2]) == i_2
    assert Interval.intersection([i_6]) == i_6
    i_8 = Interval(-1, 4)
    i_9 = Interval(4, 8)
    assert Interval.intersection([i_1, i_8]) == Interval(3,4)
    assert Interval.intersection([i_9, i_1]) == Interval(4,5)
    assert Interval.intersection([i_9, i_1, i_8]) == Interval(4,4)
    assert Interval.intersection([i_9, i_1, i_8, i_4]) == Interval(4,4)
    i_10 = Interval(-10,-2)
    assert Interval.intersection([i_10, i_8]) == Interval(-1,-2)
    assert Interval.intersection([i_10, i_8]) == i_6
    assert Interval.intersection([i_10, i_8, i_2, i_3, i_1]) == i_6
    print("SUCCESS: test_interval")

def test_interval_set():
    # todo: Add TEST
    # I_1 = IntervalSet([i_1,i_2,i_3])
    # print(I_1)
    # I_2 = IntervalSet([])
    # print(I_2)
    # I_3 = IntervalSet([i_2,i_3,i_6])
    # print(I_3)
    # I_4 = IntervalSet([i_1,i_2,i_3,i_4])
    # print(I_4)
    pass

def test_wp_generalize(tr):
    x = Int('x')
    y = Int('y')
    z = Int('z')
    c_1 = ConditionStmt(x + y >= 8)
    c_1_1 = ConditionStmt(x - y >= 8)
    a_1 = AssignmentStmt(z == x + y)
    a_1_1 = AssignmentStmt(z == x - y)
    c_2 = ConditionStmt(x <= y)
    c_3 = ConditionStmt(z >= 9)
    a_2 = AssignmentStmt(z == z - 1)
    c_4 = ConditionStmt(z <= 8)
    multitrace = BackwardTrace([[c_1, c_1_1], [a_1, a_1_1], [c_2], [c_3], [a_2], [c_4]])
    wp_gen_no_simpl = Generalizer(PreciseDomain(False))
    wp_gen_with_simpl = Generalizer(PreciseDomain(True))
    r = wp_gen_no_simpl.generalize_input(tr,print_annotation=True)
    print("Final result generalize input from top no simplification: ", r, "\n")
    simplify(r)
    print("Final result generalize input from top simplify once at end: ", r, "\n")
    r = wp_gen_with_simpl.generalize_input(tr,print_annotation=True)
    print("Final result generalize input from top simplify after each step: ", r, "\n")
    r = wp_gen_no_simpl.generalize_trace(multitrace,print_annotation=True)
    print("Final result generalize trace from top no simplification: ", r, "\n")
    r = wp_gen_with_simpl.generalize_trace(multitrace, print_annotation=True)
    print("Final result generalize trace from top simplify after each step: ", r, "\n")
    r = wp_gen_no_simpl.generalize_trace(multitrace, initial_formula=PreciseDomain().get_bottom(), print_annotation=True)
    print("Final result generalize trace from bottom no simplification: ", r, "\n")

def test_interval_intersection():
    r = max_with_minf([MINF, -3, -7, MINF, MINF, -4])
    print(r)
    r = max_with_minf([MINF, MINF, MINF, MINF, MINF, MINF])
    print(r)
    r = min_with_inf([INF, -3, -7, INF, INF, -4])
    print(r)
    r = min_with_inf([INF, INF, INF, INF, INF, INF])
    print(r)
    r = interval_intersection([Interval("x", 3, 9), Interval("x", -2, 7), Interval("x", MINF, 3)])
    print(r)
    r = interval_intersection([Interval("x", MINF, 19), Interval("x", MINF, 17), Interval("x", MINF, 63)])
    print(r)
    r = interval_intersection([Interval("x", 33, INF), Interval("x", -22, INF), Interval("x", MINF, INF)])
    print(r)
    r = interval_intersection([Interval("x", 0, 6), Interval("x", 8, 60)])
    print(r)
    r = interval_intersection([Interval("x", 0, 6), Interval("x", 6, INF)])
    print(r)


def test_generalize():
    # test_wp_generalize_trace()
    test_wp_generalize_input()
    # test_interval_generalize_trace()
    # test_interval_generalize_input()

def test_wp_generalize_trace():
    # NO SIMPLIFICATION
    r = wp_generalizer.generalize_trace(mt_TFT, print_annotation=False)
    print(r)
    r_1 = wp_generalizer.generalize_trace(mt_TFT, initial_formula=x>8, record_annotation=True, print_annotation=False)
    print(r_1)
    r_2 = wp_generalizer.generalize_trace(mt_TFT, initial_formula=y>8, record_annotation=True, print_annotation=False)
    print(r_2)
    r_3 = wp_generalizer.generalize_trace(mt_TFT, initial_formula=wp_domain.get_bottom())
    print(r_3)
    # SIMPLIFICATION
    wp_domain.set_simplification(True)
    r = wp_generalizer.generalize_trace(mt_TFT, print_annotation=False)
    print(r)
    r_1 = wp_generalizer.generalize_trace(mt_TFT, initial_formula=x>8, record_annotation=True, print_annotation=False)
    print(r_1)
    r_2 = wp_generalizer.generalize_trace(mt_TFT, initial_formula=y>8, record_annotation=True, print_annotation=False)
    print(r_2)
    r_3 = wp_generalizer.generalize_trace(mt_TFT, initial_formula=wp_domain.get_bottom())
    print(r_3)
    wp_domain.set_simplification(False)
    print("SUCCESS: test_wp_generalize_trace")

def test_wp_generalize_input():
    # NO SIMPLIFICATION
    # r = wp_generalizer.generalize_input(tr_TFT, print_annotation=True)
    # print(r)
    r_1 = wp_generalizer.generalize_input(tr_TFT, initial_formula=x > 8, record_annotation=True, print_annotation=True)
    print(r_1)
    print("simplified: " + str(simplify_and_propagate_ineqs(r_1)))
    # r_2 = wp_generalizer.generalize_input(tr_TFT, initial_formula=y > 8, print_annotation=True, record_annotation=True)
    # print(r_2)
    # r_3 = wp_generalizer.generalize_input(tr_TFT, initial_formula=wp_domain.get_bottom(), print_annotation=True)
    # print(r_3)
    # WITH SIMPLIFICATION
    wp_domain.set_simplification(True)
    # r = wp_generalizer.generalize_input(tr_TFT, print_annotation=True)
    # print(r)
    r_1 = wp_generalizer.generalize_input(tr_TFT, initial_formula=x > 8, record_annotation=True, print_annotation=True)
    print(r_1)
    # r_2 = wp_generalizer.generalize_input(tr_TFT, initial_formula=y > 8, print_annotation=True, record_annotation=True)
    # print(r_2)
    # r_3 = wp_generalizer.generalize_input(tr_TFT, initial_formula=wp_domain.get_bottom(), print_annotation=True)
    # print(r_3)
    wp_domain.set_simplification(False)
    print("SUCCESS: test_wp_generalize_input")

def test_interval_generalize_trace():
    r = interval_generalizer.generalize_trace(mt_TFT, print_annotation=True)
    assert len(r)==0
    r_1 = interval_generalizer.generalize_trace(mt_TFT, initial_formula=I, record_annotation=True)
    assert len(r_1)==0
    r_2 = interval_generalizer.generalize_trace(mt_TFT, initial_formula=I_1, print_annotation=True, record_annotation=True)
    assert len(r_2)==0
    r_3 = interval_generalizer.generalize_trace(mt_TFT, initial_formula=interval_domain.get_bottom())
    assert len(r_3)==0
    print("SUCCESS: test_interval_generalize_trace")

def test_interval_generalize_input():
    r = interval_generalizer.generalize_input(tr_TFT,print_annotation=True)
    assert interval_domain.is_top(r)
    r_1 = interval_generalizer.generalize_input(tr_TFT, initial_formula=I, record_annotation=True)
    assert r_1 == I
    r_2 = interval_generalizer.generalize_input(tr_TFT, initial_formula=I_1,print_annotation=True, record_annotation=True)
    assert r_2 == I_1
    r_3 = interval_generalizer.generalize_input(tr_TFT, initial_formula=interval_domain.get_bottom())
    assert interval_domain.is_bottom(r_3)
    print("SUCCESS: test_interval_generalize_input")

def test_sort():
    class Graph(TopologicalSort):
        def __init__(self, root):
            super().__init__(root)
            self.graph = defaultdict(list)  # dictionary containing adjacency List

        # function to add an edge to graph
        def addEdge(self, u, v):
            self.graph[u].append(v)

        def get_children(self, node):
            return self.graph[node]

        def process(self, node):
            return str(node)

    g = Graph(1)
    g.addEdge(2, 5)
    g.addEdge(0, 5)
    g.addEdge(0, 4)
    g.addEdge(1, 4)
    g.addEdge(3, 2)
    g.addEdge(1, 3)
    r = g.sort()
    print("sort ",r)


def test_remove_or():
    f = Or(x==0, y==1)
    s = Solver()
    s.push()
    s.add(f)
    s.check()
    m = s.model()
    print("f is: "+ str(f) +" model is: " + str(s.model()))
    r = remove_or(f,m)
    print(r)
    f = Not(And(x>0, x<3))
    s.pop()
    s.push()
    s.add(f)
    s.check()
    m = s.model()
    print("f is: "+ str(f) +" model is: " + str(s.model()))
    r = remove_or(f,m)
    print(r)
    f = Or(Not(x<0),And(Not(y>7),y<4))
    s.pop()
    s.push()
    s.add(f)
    s.check()
    m = s.model()
    print("f is: "+ str(f) +" model is: " + str(s.model()))
    r = remove_or(f,m)
    print(r)
    f = Not(Or(Not(x<0),And(Not(y>7),y<4)))
    s.pop()
    s.push()
    s.add(f)
    s.check()
    m = s.model()
    print("f is: "+ str(f) +" model is: " + str(s.model()))
    r = remove_or(f,m)
    print(r)
    f = Implies(x>0, y<0)
    s.pop()
    s.push()
    s.add(f)
    s.check()
    m = s.model()
    print("f is: " + str(f) + " model is: " + str(s.model()))
    r = remove_or(f,m)
    print(r)
    f = If(x>0,y<0,y>0)
    s.pop()
    s.push()
    s.add(f)
    s.check()
    m = s.model()
    print("f is: " + str(f) + " model is: " + str(s.model()))
    r = remove_or(f,m)
    print(r)
    f = Implies(And(Not(If(x > 0, y < 0, y > 0)),Or(z<=7, x<=8)),y==2)
    s.pop()
    s.push()
    s.add(f)
    s.check()
    m = s.model()
    print("f is: " + str(f) + " model is: " + str(s.model()))
    r = remove_or(f, m)
    print(r)


def main():
    # test_interval()
    # test_interval_set()
    # test_generalize()
    # test_interval_intersection()
    # describe_tactics()
    # test_sort()
    test_remove_or()


if __name__ == "__main__":
    main()

