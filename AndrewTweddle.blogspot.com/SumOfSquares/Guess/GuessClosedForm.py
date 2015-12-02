import sys
from sympy import *
from sympy.parsing.sympy_parser import parse_expr

if len(sys.argv) != 2:
  scriptName = sys.argv[0]
  print 'USAGE: {0} "<expression>"'.format(scriptName)
  print '<expression> is a polynomial over a variable i.'
  print 'It is the term in a summation for values of i between 1 and n'
  raise SystemExit(1)

expr_to_parse = sys.argv[1]
print "f(n) = SUM [{0}] for i between 1 and n".format(expr_to_parse)

init_printing()

# Configure symbols:
i = Symbol("i", integer=True)
parsed = parse_expr(expr_to_parse, {"i": i})
h_parsed = Poly(parsed, i)
d = h_parsed.degree(i)

# Function f is the true summation function.
def f(x):
    if x == 0:
        return 0
    squares = [h_parsed(k) for k in range(1, x + 1)]
    return sum(squares)

# Function g is our guess as to its closed form solution.
# Assume the closed form solution is a degree (d+1) polynomial:
a = [Symbol("a_{0}".format(k), rational=True) for k in range(d + 2)]
n = Symbol("n", integer=True)

g_temp = Poly(sum([a[j] * (n ** j) for j in range(d+2)]), n)
h_temp = h_parsed.subs(i, n)
g, h = g_temp.unify(h_temp)  # a hack to give the coefficients of g and h the same domain
# Note that the domain is Z not Q (or R), otherwise we get an error message about a_{d+1} not being rational
# TODO: resolve this issue

# Find coefficients a_j for g such that:
# 1) g(0) = f(0) = 0
eq_0 = Eq(g(0), 0)

# 2) Choose a_j coefficents, so that: g(i) - g(i-1) = h(i) for any positive integer i
#    Because then f(n) = sum(i=1 to n)[h(i)]            by definition
#                      = sum(i=1 to n)[g(i) - g(i-1)]
#                      = g(n) - g(0)                    since all other terms cancel out
#                      = g(n)                           since g(0) = 0
p1 = simplify(g.subs(n, i) - g.subs(n, i - 1) - h.subs(n, i))
p2 = Poly(p1, i)  # a hack to group terms by powers of i only
# TODO: Polynomial domain is integers. How to specify rational or real domains for the general case?

# Enforce that g(i) - g(i-1) and h(i) are identical polynomials in i.
# Equivalently each coefficient in g(i) - g(i-1) - h(i) is always zero:
eqs = [Eq(c) for c in p2.coeffs()] + [eq_0]
soln = solve(eqs)

if (soln):
  f_closed = g.subs(soln)
  f_closed_factorized = factor(f_closed)
  print "     = {0}".format(f_closed)
  print "     = {0}".format(f_closed_factorized)
else:
  print "NO CLOSED FORM FOUND!"
