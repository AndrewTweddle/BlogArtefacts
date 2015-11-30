from sympy import *
# TODO: it's generally better to import specific functions

init_printing()

# Configure symbols:
n = Symbol("n", integer=True)
i = Symbol("i", integer=True)
a_0, a_1, a_2, a_3 = symbols("a_0, a_1, a_2, a_3", rational=True)

# Function f is the true sum of squares function. 
# Function g is our guess as to its closed form solution.
def f(x):
    if x == 0:
        return 0
    squares = [k * k for k in range(x + 1)]
    return sum(squares)

# Assume the closed form solution is a degree 3 polynomial:

# h is the term inside the summation
h_temp = Poly(n ** 2, n)
g_temp = Poly(a_0 + a_1 * n + a_2 * n ** 2 + a_3 * n ** 3, n)
g, h = g_temp.unify(h_temp)  # a hack to give the coefficients of f and h the same domain
# Note that the domain is Z not Q or R, otherwise we get an error message about a_2 not being rational
# TODO: resolve this

# Find coefficients a_i for g such that:
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
f_closed = factor(g.subs(soln))
print(f_closed)
