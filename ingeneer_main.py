import argparse
import sys
from z3 import *


def read_program(args):
    infile = args.infile
    constraints = read_smt2(infile.name)
    print(constraints)


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
    args = parse_args_ingeneer()
    read_program(args)
