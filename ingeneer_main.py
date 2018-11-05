import argparse
from z3_utils import *
import sys as _sys
import general_utils
from test_main import strengthen_formula_test


def read_program():
    sys_args = _sys.argv[1:]
    ofile = general_utils.open_file("benchmark_results.csv")
    for file in sys_args:
        constraints = read_smt2(file)
        f = And(constraints)
        strengthen_formula_test(f)


def parse_args_ingeneer():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='?', type=argparse.FileType('rb'),
                        default=sys.stdin,
                        help="name of file to process (STDIN if omitted)")
    args = parser.parse_args()
    return args


def read_smt2(filename):
    formula = parse_smt2_file(filename)
    if is_and(formula):
        return formula.children()
    else:
        return [formula]


if __name__ == "__main__":
    # args = parse_args_ingeneer()
    read_program()

