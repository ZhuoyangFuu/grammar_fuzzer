import hypothesis.strategies as st
from hypothesis import given


# constant = digit {digit} ;
# digit    = "0" | "1" | ... | "9" ;
def constant():
    # Generate strings of at least length 1 using only digits
    return st.text(alphabet=st.sampled_from("0123456789"), min_size=1)


# factor = constant | "(" expression ")" ;
def factor():
    # st.deferred is required here because 'expr' is defined later.
    # This prevents an infinite recursion error during setup.
    return st.one_of(
        constant(),
        st.builds(lambda e: f"({e})", st.deferred(expr))
    )


# term = factor { ("*" | "/") factor } ;
def term():
    def build_term(first_factor, tail):
        return first_factor + "".join(op + f for op, f in tail)

    return st.builds(
        build_term,
        factor(),
        # Limiting max_size to 3 prevents the strings from becoming infinitely huge
        st.lists(st.tuples(st.sampled_from(["*", "/"]), factor()), max_size=3)
    )


# expression = term { ("+" | "-") term } ;
def expr():
    def build_expr(first_term, tail):
        return first_term + "".join(op + t for op, t in tail)

    return st.builds(
        build_expr,
        term(),
        st.lists(st.tuples(st.sampled_from(["+", "-"]), term()), max_size=3)
    )


"""
DISCUSSION ON TEST INPUT GENERATION:
------------------------------------
Traditional testing approaches and predictable edge cases. The inputs are fixed and biased by human imagination.

Hypothesis, on the other hand, is a property-based testing framework. By formalizing the grammar, 
Hypothesis acts as an automated fuzzer. It generates hundreds of highly complex, nested, and 
structurally valid permutations that a human would rarely write by hand (e.g., "(((99321/3)*7)+0)").
Additionally, if a test were to fail, Hypothesis automatically "shrinks" the input, reducing a 
massive failing string down to the absolute minimal reproducible example.
"""


@given(expr())
def test_print(expr: str):
    print(expr)