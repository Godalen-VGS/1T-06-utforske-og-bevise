"""Automatisk retting av 1T-06-utforske-og-bevise.

Hver sjekk i SJEKKER er én deltest, og poengene fordeles likt på dem.
De samme sjekkene ligger i "Test løsningen din"-cellen nederst i notebooken.
"""
import pytest

from notebook_loader import last_notebook

def naer(a, b, rel=1e-3):
    """Sant hvis tallet a er innenfor rel (relativt) av b."""
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if b == 0:
        return abs(a) < 1e-9
    return abs(a - b) <= rel * abs(b)


def S(tekst):
    """Gjør tekst om til et sympy-uttrykk, f.eks. S("x**2 - 1")."""
    import sympy
    return sympy.sympify(tekst, locals={n: sympy.Symbol(n) for n in ("N", "O", "Q", "S")})


def lik(a, b):
    """Sant hvis a og b er matematisk like.

    Lister og mengder sammenlignes uten hensyn til rekkefølge, tupler (koordinater) i rekkefølge.
    """
    import sympy
    if a is None:
        return False
    if isinstance(b, tuple):
        if not isinstance(a, (tuple, list, sympy.Tuple)) or len(a) != len(b):
            return False
        return all(lik(x, y) for x, y in zip(a, b))
    if isinstance(b, (list, set)):
        if isinstance(a, sympy.FiniteSet):
            a = list(a)
        if not isinstance(a, (list, tuple, set)) or len(a) != len(b):
            return False
        rest = list(a)
        for y in b:
            for i, x in enumerate(rest):
                if lik(x, y):
                    del rest[i]
                    break
            else:
                return False
        return True
    if isinstance(b, dict):
        if not isinstance(a, dict) or len(a) != len(b):
            return False
        a = {str(k): v for k, v in a.items()}
        return all(str(k) in a and lik(a[str(k)], v) for k, v in b.items())
    try:
        a, b = sympy.sympify(a), sympy.sympify(b)
    except (sympy.SympifyError, TypeError):
        return False
    vanlige = lambda u: u.subs({s: sympy.Symbol(s.name) for s in u.free_symbols})
    a, b = vanlige(a), vanlige(b)
    if isinstance(a, sympy.Set) or isinstance(b, sympy.Set):
        return a == b
    if getattr(b, "is_Relational", False):
        return a == b
    try:
        return sympy.simplify(a - b) == 0
    except TypeError:
        return a == b

oppgave = last_notebook("oppgave")

SJEKKER = [
    ('1_sum', 'sum_oddetall(5) skal gi 1 + 3 + 5 + 7 + 9 = 25', 'sum_oddetall(5) == 25 and sum_oddetall(1) == 1'),
    ('1_sjekk', 'sjekk_oddetall(1000) skal gi True', 'sjekk_oddetall(1000) is True or sjekk_oddetall(1000) == True'),
    ('2_prim', 'er_primtall skal gi riktig svar for 0, 1, 2, 17, 21 og 97', '[er_primtall(t) for t in [0, 1, 2, 17, 21, 97]] == [False, False, True, True, False, True]'),
    ('2_moteksempel', 'moteksempel skal være den minste n der n² + n + 41 ikke er et primtall', 'moteksempel == 40'),
    ('3', 'forskjell skal være (n + 1)² - n² forenklet', "lik(forskjell, S('2*n + 1'))"),
    ('4', 'delelig_med_6(1000) skal gi True', 'delelig_med_6(1000) == True'),
    ('5_tripler', 'pytagoreiske(20) skal gi alle seks tripler med c ≤ 20', 'lik(pytagoreiske(20), [(3, 4, 5), (6, 8, 10), (5, 12, 13), (9, 12, 15), (8, 15, 17), (12, 16, 20)])'),
    ('5_euklid', 'euklid skal være a² + b² - c² forenklet, altså 0', 'euklid is not None and lik(euklid, 0)'),
]


@pytest.mark.parametrize(
    "beskrivelse,uttrykk", [s[1:] for s in SJEKKER], ids=[s[0] for s in SJEKKER]
)
def test_sjekk(beskrivelse, uttrykk):
    navnerom = {**vars(oppgave), "naer": naer, "lik": lik, "S": S}
    assert eval(uttrykk, navnerom), beskrivelse
