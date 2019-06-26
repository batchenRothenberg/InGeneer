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
import formula_strengthener


x = Int('x')
y = Int('y')
z = Int('z')
t = Int('t')
r = Int('r')
w = Int('w')
c_1_0 = ConditionStmt(x + y >= 8)
c_1_1 = ConditionStmt(x - y >= 8)
c_1_2 = ConditionStmt(x + y > 8)
c_1_3 = ConditionStmt(x + y < 8)
a_1_0 = AssignmentStmt(z == x + y)
a_1_1 = AssignmentStmt(z == x - y)
c_2_0 = ConditionStmt(x < 0)
c_2_1 = ConditionStmt(x > 0)
c_2_2 = ConditionStmt(x <= 0)
c_3_0 = ConditionStmt(z >= 9)
c_3_1 = ConditionStmt(z > 9)
c_3_2 = ConditionStmt(z < 9)
a_2_0 = AssignmentStmt(t == z - 1)
a_2_1 = AssignmentStmt(t == z + 1)
c_4_0 = ConditionStmt(t <= 8)
a_3_0 = AssignmentStmt(z == 9)
a_4_0 = AssignmentStmt(r == x - 1)
a_4_1 = AssignmentStmt(r == x + 1)
a_5_0 = AssignmentStmt(w == z + 3)
a_5_1 = AssignmentStmt(w == z - 3)
tr_TFT = BackwardTrace([c_1_0, a_1_0, c_2_2, c_3_0, a_2_0, c_4_0])
mt_TFT = BackwardTrace([[c_1_0, c_1_1, c_1_2, c_1_3], [a_1_0, a_1_1], [c_2_0,c_2_1,c_2_2], [c_3_0,c_3_1,c_3_2], [a_2_0,a_2_1], [c_4_0]])



def test_interval_domain():
    stren_top = StrenghenedFormula.get_top(True)
    interval_domain = IntervalDomain(True)
    print(mt_TFT)
    print(tr_TFT)
    model = get_model_from_SSA_trace(tr_TFT)
    print(model)
    res = stren_top
    for stmt in tr_TFT:
        print(str(stmt))
        res = interval_domain.do_step(res,stmt,model)
        print(str(res))


def test_generalization_with_interval():
    interval_domain = IntervalDomain(True)
    model = get_model_from_SSA_trace(tr_TFT)
    g = Generalizer(interval_domain,True)
    g.generalize_trace(mt_TFT,model=model,print_annotation=True)


def main():
    # test_interval_domain()
    test_generalization_with_interval()

if __name__ == "__main__":
    main()

