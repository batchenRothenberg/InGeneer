from wp_generalizer import *
from ip_generalizer import *
from z3 import *
from interval import *
from stmt import *
from trace import *


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


def test_generalize(tr):
    I = IntervalSet([])
    I_1 = IntervalSet([Interval("x", 3, 7)])
    #r = generalize(I, tr, interval_wp_step)
    #print(r)
    #r = generalize(I_1, tr, interval_wp_step())
    #print(r)
    wp_gen = WPGeneralizer(tr,simplification=Simplification.NONE)
    r = wp_gen.generalize()
    print("Final result no simplification: ", r)
    wp_gen.set_simplification(Simplification.ONCE_AT_END)
    r = wp_gen.generalize()
    print("Final result simplify once at end: ", r)
    wp_gen.set_simplification(Simplification.ALWAYS)
    r = wp_gen.generalize()
    print("Final result simplify after each step: ", r)


def main():
    x = Int('x')
    y = Int('y')
    z = Int('z')
    c_1 = ConditionStmt(x + y >= 8)
    a_1 = AssignmentStmt(z == x + y)
    c_2 = ConditionStmt(x <= 0)
    c_3 = ConditionStmt(z >= 9)
    a_2 = AssignmentStmt(z == z - 1)
    c_4 = ConditionStmt(z <= 8)
    tr = BackwardTrace([c_1, a_1, c_2, c_3, a_2, c_4])
    # test_trace(tr)
    # test_interval()
    test_generalize(tr)


if __name__ == "__main__":
    main()

