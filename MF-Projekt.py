def K(a, b): return a and b
def A(a, b): return a or b
def I(a, b): return (not a) or b
def R(a, b): return a == b

OPS = {
    "k": (2, K),
    "a": (1, A),
    "i": (0, I),
    "r": (0, R),
}