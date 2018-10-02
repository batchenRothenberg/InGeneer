from collections import defaultdict

from precise_domain import *
from interval_domain import *
from z3 import *
from interval import *
from stmt import *
from trace import *
from utils import *
from generalizer import Generalizer


def test_trace(tr):
    print("Forward:")
    print(tr)
    print(tr.get_curr())
    tr.do_step()
    print(tr.get_curr())
    tr.do_step()
    print(tr.get_curr())
    tr.do_step()
    print(tr.get_curr())
    tr.do_step()
    print(tr.get_curr())
    tr.do_step()
    print(tr.get_curr())
    tr.do_step()
    print(tr.get_curr())
    tr.do_step()
    print(tr.get_curr())
    tr.do_step()
    print(tr.get_curr())
    print("Backward:")
    tr = BackwardTrace(tr.get_trace())
    print(tr)
    print(tr.get_curr())
    tr.do_step()
    print(tr.get_curr())
    tr.do_step()
    print(tr.get_curr())
    tr.do_step()
    print(tr.get_curr())
    tr.do_step()
    print(tr.get_curr())
    tr.do_step()
    print(tr.get_curr())
    tr.do_step()
    print(tr.get_curr())
    tr.do_step()
    print(tr.get_curr())
    tr.do_step()
    print(tr.get_curr())


def test_interval():
    i_1 = Interval("x", 3, 5)
    i_2 = Interval("y", -2, 6)
    i_3 = Interval("var", "minf", "inf")
    i_4 = Interval("x", "minf", 7)
    i_5 = Interval("x", -5, "inf")
    i_6 = Interval("x", -5, -10)
    print(i_1,i_2,i_3)
    print(i_4,i_5,i_6)
    print("is_bottom:",i_1.is_bottom(),i_2.is_bottom(),i_3.is_bottom(),i_4.is_bottom(),i_5.is_bottom(),i_6.is_bottom())
    print("is_top:",i_1.is_top(),i_2.is_top(),i_3.is_top(),i_4.is_top(),i_5.is_top(),i_6.is_top())
    print("len:",len(i_1),len(i_2),len(i_3),len(i_4),len(i_5),len(i_6))
    I_1 = IntervalSet([i_1,i_2,i_3])
    print(I_1)
    I_2 = IntervalSet([])
    print(I_2)
    I_3 = IntervalSet([i_2,i_3,i_6])
    print(I_3)
    I_4 = IntervalSet([i_1,i_2,i_3,i_4])
    print(I_4)


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


def test_interval_generalize(tr):
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
    tr2 = BackwardTrace([c_1, a_1, c_2, c_3, a_2, c_4])
    multitrace2 = BackwardTrace([[c_1, c_1_1], [a_1, a_1_1], [c_2], [c_3], [a_2], [c_4]])
    I = IntervalSet({"x": Interval(3, 7),"y": Interval(-3, 17)})
    I_1 = IntervalSet({"x": Interval(3, 7)})
    interval_generalizer = Generalizer(IntervalDomain())
    r = interval_generalizer.generalize_input(tr2, print_annotation=True)
    print("Final result intervals input generalize from top: ", r, "\n")
    r_1 = interval_generalizer.generalize_input(tr2, initial_formula=I, print_annotation=True)
    print("Final result intervals input generalize from two intervals: ", r_1, "\n")
    r_2 = interval_generalizer.generalize_input(tr2, initial_formula=I_1, print_annotation=True)
    print("Final result intervals input generalize from one interval: ", r_2, "\n")
    r = interval_generalizer.generalize_trace(multitrace2, print_annotation=True)
    print("Final result intervals trace generalize from top: ", r, "\n")
    r_1 = interval_generalizer.generalize_trace(multitrace2, initial_formula=I, print_annotation=True)
    print("Final result intervals trace generalize from two intervals: ", r_1, "\n")
    r_2 = interval_generalizer.generalize_trace(multitrace2, initial_formula=I_1, print_annotation=True)
    print("Final result intervals trace generalize from one interval: ", r_2, "\n")
    r_3 = interval_generalizer.generalize_trace(multitrace2, initial_formula=IntervalSet.get_bottom(), print_annotation=True)
    print("Final result intervals trace generalize from bottom: ", r_3, "\n")

def test_generalize(tr):
    test_wp_generalize(tr)
    test_interval_generalize(tr)


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


def main():
    x = Int('x')
    y = Int('y')
    z = Int('z')
    c_1 = ConditionStmt(x + y >= 8)
    a_1 = AssignmentStmt(z == x + y)
    c_2 = ConditionStmt(x <= y)
    c_3 = ConditionStmt(z >= 9)
    a_2 = AssignmentStmt(z == z - 1)
    c_4 = ConditionStmt(z <= 8)
    tr = BackwardTrace([c_1, a_1, c_2, c_3, a_2, c_4])
    # test_trace(tr)
    # test_interval()
    test_generalize(tr)
    # test_interval_intersection()
    # help_simplify()
    # test_sort()


if __name__ == "__main__":
    main()
