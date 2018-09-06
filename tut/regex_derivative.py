from enum import Enum, auto
class M(Enum):
    empty = auto()
    eps = auto()
    char = auto()
    cat = auto()
    alt = auto()
    star = auto()

def isit(l, e): return l[0] == e

def nullable(l):
    if isit(l, M.empty): return False
    if isit(l, M.eps): return True
    if isit(l, M.char): return False
    if isit(l, M.star): return True
    if isit(l, M.alt): return any(nullable(i) for i in l[1])
    if isit(l, M.cat): return all(nullable(i) for i in l[1])

def derive(c, l):
    if isit(l, M.empty): return (M.empty, None)
    if isit(l, M.eps): return (M.empty, None)
    if isit(l, M.char): return (M.eps, None) if c == l[1] else (M.empty, None)
    if isit(l, M.alt): return (M.alt, [derive(c, i) for i in l[1]])
    if isit(l, M.cat):
        if nullable(l[1][0]):
            return (M.alt, [derive(c, l[1][1]), (M.cat, [derive(c, i) for i in l[1]])])
        else:
            return (M.cat, [derive(c, i) for i in l[1]])
    if isit(l, M.star): return (M.cat, [derive(c, l[1]), l])
    assert False

def matches(w, l):
    if w == '':
        return nullable(l)
    else:
        return matches(w[1:], derive(w[0], l))

print(matches('aab', (M.cat, [(M.star, (M.char, 'a')), (M.char, 'b')])))
