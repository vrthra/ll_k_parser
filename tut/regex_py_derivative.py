def is_empty(l): return l == []
def is_eps(l):   return l == ''
def is_char(l):  return isinstance(l, str) and len(l) == 1    # 'a'
def is_star(l):  return isinstance(l, tuple) and len(l) == 1  # (x,)
def is_alt(l):   return isinstance(l, tuple) and len(l) > 1   # (a,b,c)
def is_cat(l):   return isinstance(l, list)                   # [a,b,c]

def nullable(l):
    if is_empty(l): return False
    if is_eps(l):   return True
    if is_char(l):  return False
    if is_star(l):  return True
    if is_alt(l):   return any(nullable(i) for i in l)
    if is_cat(l):   return all(nullable(i) for i in l)

def derive(c, l):
    if is_empty(l): return []
    if is_eps(l):   return []
    if is_char(l):  return '' if c == l else []
    if is_alt(l):   return tuple(derive(c, i) for i in l)
    if is_cat(l):
        if nullable(l[0]):
            return (derive(c, l[1:]), [derive(c, l[0])] + l[1:])
        else:
            return [derive(c, l[0])] + l[1:]
    if is_star(l): return [derive(c, l[0]), l]
    return False

def matches(w, l):
    return nullable(l) if w == '' else matches(w[1:], derive(w[0], l))

print(matches('aabzd', [('a',), ['b', ('x', 'y', 'z'), 'd', ('e',)]]))
print(matches('aabnd', [('a',), ['b', ('x', 'y', 'z'), 'd', ('e',)]]))
