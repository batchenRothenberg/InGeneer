import timeit
from collections import defaultdict

from precise_domain import *
from interval_domain import *
from z3 import *
from interval import *
from stmt import *
from trace import *
from z3_utils import *
from general_utils import *
from generalizer import Generalizer

x = Int('x')
y = Int('y')
z = Int('z')
t = Int('t')
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

i_1 = Interval(3, 5)
i_2 = Interval(-2, 6)
i_3 = Interval("minf", "inf")
i_4 = Interval("minf", 7)
i_5 = Interval(-5, "inf")
i_6 = Interval(-5, -10)
i_7 = Interval(5, 0)
i_8 = Interval(-1, 4)
i_9 = Interval(4, 8)
i_10 = Interval(-10, -2)

I_1 = IntervalSet({"x": Interval(3, 7), "y": Interval(-3, 17)})
I_2 = IntervalSet({"x": Interval(3, 7)})
I_3 = IntervalSet({"x": i_1,"y": i_2})
I_4 = IntervalSet({"x": i_1,"y": i_2, "z": i_4})
I_5 = IntervalSet.get_top()
I_6 = IntervalSet.get_bottom()
I_7 = IntervalSet({"x": i_10,"y": i_7, "z": i_5})
I_8 = IntervalSet({"x": i_1,"y": i_2, "z": i_8, "w": i_9, "t":i_10})

f_1 = Or(x==0, y==1)
f_2 = Not(And(x > 0, x < 3))
f_3 = Or(Not(x < 0), And(Not(y > 7), y < 4))
f_4 = Not(Or(Not(x < 0), And(Not(y > 7), y < 4)))
f_5 = Implies(x > 0, y < 0)
f_6 = If(x > 0, y < 0, y > 0)
f_7 = Implies(And(Not(If(x > 0, y < 0, y > 0)), Or(z <= 7, x <= 8)), y == 2)

interval_domain = IntervalDomain()
interval_generalizer = Generalizer(interval_domain, debug=True)
wp_domain = PreciseDomain()
wp_generalizer = Generalizer(wp_domain, debug=True)


def test_interval():
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
    assert Interval.intersection([i_1, i_8]) == Interval(3,4)
    assert Interval.intersection([i_9, i_1]) == Interval(4,5)
    assert Interval.intersection([i_9, i_1, i_8]) == Interval(4,4)
    assert Interval.intersection([i_9, i_1, i_8, i_4]) == Interval(4,4)
    assert Interval.intersection([i_10, i_8]) == Interval(-1,-2)
    assert Interval.intersection([i_10, i_8]) == i_6
    assert Interval.intersection([i_10, i_8, i_2, i_3, i_1]) == i_6
    print("SUCCESS: test_interval")


def test_interval_set():
    assert not I_1.is_top()
    assert not I_2.is_top()
    assert not I_3.is_top()
    assert not I_4.is_top()
    assert I_5.is_top()
    assert not I_6.is_top()
    assert not I_7.is_top()
    assert not I_1.is_bottom()
    assert not I_2.is_bottom()
    assert not I_3.is_bottom()
    assert not I_4.is_bottom()
    assert not I_5.is_bottom()
    assert I_6.is_bottom()
    assert I_7.is_bottom()
    I_1.add_interval("z", i_1)
    assert I_1 == IntervalSet({"x": Interval(3, 7), "y": Interval(-3, 17), "z": i_1})
    I_1.add_interval("z", i_1)
    assert I_1 == IntervalSet({"x": Interval(3, 7), "y": Interval(-3, 17), "z": i_1})
    I_1.add_interval("z", i_8)
    assert I_1 != IntervalSet({"x": Interval(3, 7), "y": Interval(-3, 17), "z": i_1})
    assert I_1 == IntervalSet({"x": Interval(3, 7), "y": Interval(-3, 17), "z": Interval(3,4)})
    I_1.add_interval("x", i_8)
    assert I_1 == IntervalSet({"x": Interval(3, 4), "y": Interval(-3, 17), "z": Interval(3,4)})
    I_1.add_interval("y", i_10)
    assert I_1 == IntervalSet({"x": Interval(3, 4), "y": Interval(-3, -2), "z": Interval(3,4)})
    oldI_1 = I_1
    I_1.add_interval("y", i_8)
    assert oldI_1 == I_1
    I_1.add_interval("x", Interval.get_top())
    assert oldI_1 == I_1
    I_1.add_interval("x", Interval.get_bottom())
    assert I_1.is_bottom()
    assert "False" == str(I_1.as_formula())
    assert "And(x <= 7, x >= 3)" == str(I_2.as_formula())
    assert "And(y <= 6, y >= -2, x <= 5, x >= 3)" == str(I_3.as_formula())
    assert "And(y <= 6, y >= -2, x <= 5, x >= 3, z <= 7)" == str(I_4.as_formula())
    assert is_true(I_5.as_formula())
    assert is_false(I_6.as_formula())
    assert is_false(I_7.as_formula())
    print("SUCCESS: test_interval_Set")

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
    pass
    # r = max_with_minf([MINF, -3, -7, MINF, MINF, -4])
    # print(r)
    # r = max_with_minf([MINF, MINF, MINF, MINF, MINF, MINF])
    # print(r)
    # r = min_with_inf([INF, -3, -7, INF, INF, -4])
    # print(r)
    # r = min_with_inf([INF, INF, INF, INF, INF, INF])
    # print(r)
    # r = interval_intersection([Interval("x", 3, 9), Interval("x", -2, 7), Interval("x", MINF, 3)])
    # print(r)
    # r = interval_intersection([Interval("x", MINF, 19), Interval("x", MINF, 17), Interval("x", MINF, 63)])
    # print(r)
    # r = interval_intersection([Interval("x", 33, INF), Interval("x", -22, INF), Interval("x", MINF, INF)])
    # print(r)
    # r = interval_intersection([Interval("x", 0, 6), Interval("x", 8, 60)])
    # print(r)
    # r = interval_intersection([Interval("x", 0, 6), Interval("x", 6, INF)])
    # print(r)
    # TODO: fix test!


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
    r_1 = interval_generalizer.generalize_trace(mt_TFT, initial_formula=I_1, record_annotation=True)
    assert len(r_1)==0
    r_2 = interval_generalizer.generalize_trace(mt_TFT, initial_formula=I_2, print_annotation=True, record_annotation=True)
    assert len(r_2)==0
    r_3 = interval_generalizer.generalize_trace(mt_TFT, initial_formula=interval_domain.get_bottom())
    assert len(r_3)==0
    print("SUCCESS: test_interval_generalize_trace")

def test_interval_generalize_input():
    r = interval_generalizer.generalize_input(tr_TFT,print_annotation=True)
    assert interval_domain.is_top(r)
    r_1 = interval_generalizer.generalize_input(tr_TFT, initial_formula=I_1, record_annotation=True)
    assert r_1 == I_1
    r_2 = interval_generalizer.generalize_input(tr_TFT, initial_formula=I_2, print_annotation=True, record_annotation=True)
    assert r_2 == I_2
    r_3 = interval_generalizer.generalize_input(tr_TFT, initial_formula=interval_domain.get_bottom())
    assert interval_domain.is_bottom(r_3)
    print("SUCCESS: test_interval_generalize_input")

def test_sort():
    class Graph(TopologicalSort):
        def __init__(self, root):
            super(Graph, self).__init__(root)
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
    s = Solver()
    s.push()
    s.add(f_1)
    s.check()
    m = s.model()
    # print("f is: "+ str(f_1) +" model is: " + str(s.model()))
    r = formula_strengthener.remove_or(f_1,m)
    assert (str(r) == "x == 0")
    s.pop()
    s.push()
    s.add(f_2)
    s.check()
    m = s.model()
    # print("f is: "+ str(f_2) +" model is: " + str(s.model()))
    r = formula_strengthener.remove_or(f_2,m)
    assert (str(r) == "Not(x < 3)")
    s.pop()
    s.push()
    s.add(f_3)
    s.check()
    m = s.model()
    # print("f is: "+ str(f_3) +" model is: " + str(s.model()))
    r = formula_strengthener.remove_or(f_3,m)
    assert(str(r) == "And(Not(y > 7), y < 4)")
    s.pop()
    s.push()
    s.add(f_4)
    s.check()
    m = s.model()
    # print("f is: "+ str(f_4) +" model is: " + str(s.model()))
    r = formula_strengthener.remove_or(f_4,m)
    assert(str(r)=="And(x < 0, Not(y < 4))")
    s.pop()
    s.push()
    s.add(f_5)
    s.check()
    m = s.model()
    # print("f is: " + str(f_5) + " model is: " + str(s.model()))
    r = formula_strengthener.remove_or(f_5,m)
    assert(str(r)=="y < 0")
    s.pop()
    s.push()
    s.add(f_6)
    s.check()
    m = s.model()
    # print("f is: " + str(f_6) + " model is: " + str(s.model()))
    r = formula_strengthener.remove_or(f_6,m)
    assert(str(r)=="And(y < 0, x > 0)")
    s.pop()
    s.push()
    s.add(f_7)
    s.check()
    m = s.model()
    # print("f is: " + str(f_7) + " model is: " + str(s.model()))
    r = formula_strengthener.remove_or(f_7, m)
    assert(str(r)=="And(Not(z <= 7), Not(x <= 8))")
    print("test_remove_or SUCCESS")


def test_formula_strengthener():
    ofile = open_file("results.csv")
    f = And(((x + y)*(x + 1) <= 8),(y <= 2),(x + z > 3))
    strengthen_formula_test(f, ofile)
    f = (x > 0)
    strengthen_formula_test(f, ofile)
    f = Implies(And(Not(If(x > 0, y < 0, y > 0)), Or(z <= 7, x <= 8)), y == 2)
    strengthen_formula_test(f, ofile)
    f = And(x > 0, And(y<0, x>=7))
    strengthen_formula_test(f, ofile)
    f = And(x <= 0, y + z <= 7)
    strengthen_formula_test(f, ofile)
    f = And(x > 0, x - t <= 3, 5*y >= 4, y + z <= 7, z == 5, t != 4)
    strengthen_formula_test(f, ofile)
    f = And(-7*z+2*t-6*y!=5)
    strengthen_formula_test(f)
    close_file(ofile)


def strengthen_formula_test(f, file = None, debug = False):
    s = Solver()
    s.add(f)
    s.check()
    m = s.model()
    r = formula_strengthener.strengthen(f, m, debug=debug)
    wrapped = wrapper(formula_strengthener.strengthen, f, m)
    stren_time = timeit.timeit(wrapped, number=1)
    res_ten_sol_stren_f, ten_sol_stren_f_time = timed(r.print_all_solutions)(10)
    res_ten_sol_f, ten_sol_f_time = timed(print_all_models)(f,10)
    res_hundred_sol_stren_f, hundred_sol_stren_f_time = timed(r.print_all_solutions)(100)
    res_hundred_sol_f, hundred_sol_f_time = timed(print_all_models)(f,100)
    res_huge_sol_stren_f, huge_sol_stren_f_time = timed(r.print_all_solutions)(10000)
    res_huge_sol_f, huge_sol_f_time = timed(print_all_models)(f,10000)

    if file is None:
        print("f is: " + str(f))
        print("strengthened f: " + str(r))
        print("time to strengthen f: " + str(stren_time))
        print("time to find first 10 solutions of strengthened f: " + str(ten_sol_stren_f_time))
        print("number of solutions found: " + str(res_ten_sol_stren_f))
        print("time to find first 10 solutions of f: " + str(ten_sol_f_time))
        print("number of solutions found: " + str(res_ten_sol_f))
        print("time to find first 100 solutions of strengthened f: " + str(hundred_sol_stren_f_time))
        print("number of solutions found: " + str(res_hundred_sol_stren_f))
        print("time to find first 100 solutions of f: " + str(hundred_sol_f_time))
        print("number of solutions found: " + str(res_hundred_sol_f))
        print("time to find first 10000 solutions of strengthened f: " + str(huge_sol_stren_f_time))
        print("number of solutions found: " + str(res_huge_sol_stren_f))
        print("time to find first 10000 solutions of f: " + str(huge_sol_f_time))
        print("number of solutions found: " + str(res_huge_sol_f))

    else:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow([str(f),
                         str(r),
                         str(stren_time),
                         str(ten_sol_stren_f_time),
                         str(ten_sol_f_time),
                         str(hundred_sol_stren_f_time),
                         str(hundred_sol_f_time),
                         str(huge_sol_stren_f_time),
                         str(huge_sol_f_time)
                         ])


def test_interval_get_values():
    assert [v for v in i_1.get_all_values_generator()]==[3,4,5]
    assert [v for v in i_2.get_all_values_generator()]==[-2,-1,0,1,2,3,4,5,6]
    assert [v for v in i_6.get_all_values_generator()]==[]
    assert [v for v in i_7.get_all_values_generator()]==[]
    assert [v for v in i_8.get_all_values_generator()]==[-1,0,1,2,3,4]
    assert [v for v in i_9.get_all_values_generator()]==[4,5,6,7,8]
    assert [v for v in i_10.get_all_values_generator()]==[-10,-9,-8,-7,-6,-5,-4,-3,-2]
    count = 0
    res = []
    for v in i_4.get_all_values_generator():
        if count == 5:
            break
        res.append(v)
        count += 1
    assert res == [7,6,5,4,3]
    res, count = [], 0
    for v in i_5.get_all_values_generator():
        if count == 5:
            break
        res.append(v)
        count += 1
    assert res == [-5,-4,-3,-2,-1]
    print("SUCCESS: test_interval_get_values")


def test_interval_set_get_values():
    print("Printing at most 100 models of "+str(I_1))
    I_1.print_all_values()
    print("Printing at most 100 models of "+str(I_2))
    I_2.print_all_values()
    print("Printing at most 100 models of "+str(I_3))
    I_3.print_all_values()
    print("Printing at most 100 models of "+str(I_4))
    I_4.print_all_values()
    print("Printing at most 100 models of "+str(I_5))
    I_5.print_all_values()
    print("Printing at most 100 models of "+str(I_6))
    I_6.print_all_values()
    print("Printing at most 100 models of "+str(I_7))
    I_7.print_all_values()
    print("Printing at most 1000 models of "+str(I_8))
    I_8.print_all_values(limit=1000)

def main():
    # test_interval()
    # test_interval_set()
    # test_generalize()
    # test_interval_intersection()
    # describe_tactics()
    # help_simplify()
    # test_sort()
    # test_remove_or()
    test_formula_strengthener()
    # test_interval_get_values()
    # test_interval_set_get_values()


if __name__ == "__main__":
    main()

