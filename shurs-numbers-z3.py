#!/usr/bin/env python3

import argparse
import time

from z3 import Solver, IntSort, Array, ForAll, Int, And, Or, Implies, IntVal, sat, Exists


class ShurProblem:
    def __init__(self, total_colors: int, total_numbers: int):
        self.total_colors = total_colors
        self.total_numbers = total_numbers
        self.solver = Solver()
        self.coloring = Array("A", IntSort(), IntSort())

        i = Int("i")
        index_range = And(i >= 0, i < total_numbers)
        color_range = And(self.coloring[i] >= IntVal(1), self.coloring[i] <= IntVal(total_colors))
        self.solver.add(ForAll(i, Implies(index_range, color_range)))

        self.a = Int("a")
        self.b = Int("b")
        self.c = Int("c")

        a_domain = (self.a >= 1) & (self.a <= total_numbers)
        b_domain = (self.b >= 1) & (self.b <= total_numbers)
        c_domain = (self.c >= 1) & (self.c <= total_numbers)

        self.abc_domains = And(a_domain, b_domain, c_domain)
        self.shur_rule = self.a + self.b == self.c


def check_solution(total_colors: int, total_numbers: int, coloring: list[int]) -> bool:
    problem = ShurProblem(total_colors, total_numbers)

    for i, color in enumerate(coloring):
        problem.solver.add(problem.coloring[IntVal(i)] == IntVal(color))

    problem.solver.add(
        And(
            problem.abc_domains,
            problem.shur_rule,
            problem.coloring[problem.a - 1] == problem.coloring[problem.b - 1],
            problem.coloring[problem.b - 1] == problem.coloring[problem.c - 1],
        ),
    )

    result = problem.solver.check()

    if result == sat:
        model = problem.solver.model()
        a_value = int(model.evaluate(problem.a).as_long())
        b_value = int(model.evaluate(problem.b).as_long())
        c_value = int(model.evaluate(problem.c).as_long())
        print(f"Counterexample found: a={a_value}, b={b_value}, c={c_value}")
        return False

    return True


def assign_colors(total_colors: int, total_numbers: int) -> list[int]:
    problem = ShurProblem(total_colors, total_numbers)

    problem.solver.add(
        ForAll(
            [problem.a, problem.b, problem.c],
            Implies(
                And(problem.abc_domains, problem.shur_rule),
                Or(
                    problem.coloring[problem.a - 1] != problem.coloring[problem.b - 1],
                    problem.coloring[problem.b - 1] != problem.coloring[problem.c - 1],
                ),
            ),
        )
    )

    result = problem.solver.check()

    if result == sat:
        model = problem.solver.model()
        return [model.evaluate(problem.coloring[i]).as_long() for i in range(total_numbers)]
    else:
        return []


def main():
    parser = argparse.ArgumentParser(description="Shur's Numbers Solver")

    parser.add_argument("-C", type=int, help="Total number of colors")
    parser.add_argument("-N", type=int, help="Number of elements in the set")
    parser.add_argument("--iterate", action="store_true", help="Iterate to find Shur's numbers")

    args = parser.parse_args()

    if args.iterate:
        total_colors = 1
        total_numbers = 1
        while True:
            start_time = time.perf_counter()
            assigned_colors = assign_colors(total_colors, total_numbers)
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time

            print(f"{total_colors} colors with N={total_numbers} took {elapsed_time:.4f} seconds")
            if not assigned_colors:
                print(f"S({total_colors}) = {total_numbers}")
                total_colors += 1
            total_numbers += 1
    else:
        print(f"Numbers: {args.N}")
        print(f"Colors:  {args.C}")
        assigned_colors = assign_colors(args.C, args.N)
        print("Assigned Colors:", assigned_colors)
        # is_valid = check_solution(2, 10, [1, 2, 2, 1, 2, 1, 1, 2, 2, 1])


if __name__ == "__main__":
    main()
