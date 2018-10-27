EOF='\0'
EPSILON=''
def rules(g): return [(k, e) for k, a in g.items() for e in a]
def terminals(g):
    return set(t for k, expr in rules(g) for t in expr if t not in g)
def fixpoint(f):
    def helper(*args):
        while True:
            sargs = repr(args)
            args_ = f(*args)
            if repr(args_) == sargs:
                return args
            args = args_
    return helper


@fixpoint
def nullable_(rules, e):
    for A, expression in rules:
        if all((token in e)  for token in expression): e |= {A}
    return (rules, e)

def nullable(grammar):
    return nullable_(rules(grammar), set())[1]

@fixpoint
def firstset_(rules, first, epsilon):
    for A, expression in rules:
        for token in expression:
            first[A] |= first[token]

            # update until the first token that is not nullable
            if token not in epsilon:
                break
    return (rules, first, epsilon)

def firstset(grammar, epsilon):
    # https://www.cs.umd.edu/class/spring2014/cmsc430/lectures/lec05.pdf p6
    # (1) If X is a terminal, then First(X) is just X
    first = {i:{i} for i in terminals(grammar)}

    # (2) if X ::= epsilon, then epsilon \in First(X)
    for k in grammar:
        first[k] = {EPSILON} if k in epsilon else set()
    return firstset_(rules(grammar), first, epsilon)[1]

@fixpoint
def followset_(grammar, epsilon, first, follow):
    for A, expression in rules(grammar):
        # https://www.cs.umd.edu/class/spring2014/cmsc430/lectures/lec05.pdf
        # https://www.cs.uaf.edu/~cs331/notes/FirstFollow.pdf
        # essentially, we start from the end of the expression. Then:
        # (3) if there is a production A -> aB, then every thing in
        # FOLLOW(A) is in FOLLOW(B)
        # note: f_B serves as both follow and first.
        f_B = follow[A]
        for t in reversed(expression):
            # update the follow for the current token. If this is the
            # first iteration, then here is the assignment
            if t in grammar:
                follow[t] |= f_B  # only bother with nt

            # computing the last follow symbols for each token t. This
            # will be used in the next iteration. If current token is
            # nullable, then previous follows can be a legal follow for
            # next. Else, only the first of current token is legal follow
            # essentially

            # (2) if there is a production A -> aBb then everything in FIRST(B)
            # except for epsilon is added to FOLLOW(B)
            f_B = f_B | first[t] if t in epsilon else (first[t] - {EPSILON})

    return (grammar, epsilon, first, follow)

def followset(grammar, start):
    # Initialize first and follow sets for non-terminals
    follow = {i: set() for i in grammar}
    follow[start] = {EOF}

    epsilon = nullable(grammar)
    first = firstset(grammar, epsilon)
    return followset_(grammar, epsilon, first, follow)
def rnullable(rule, epsilon):
    return all(token in epsilon for token in rule)
def rfirst(rule, first, epsilon):
    tokens = set()
    for token in rule:
        tokens |= first[token]
        if token not in epsilon: break
    return tokens
def predict(rulepair, first, follow, epsilon):
    A, rule = rulepair
    rf = rfirst(rule, first, epsilon)
    if rnullable(rule, epsilon):
        rf |= follow[A]
    return rf
def parse_table(grammar, start, my_rules):
    _, epsilon, first, follow = followset(grammar, start)

    ptable = [(rule, predict(rule, first, follow, epsilon))
              for rule in my_rules]

    parse_tbl = {k: {} for k in grammar}

    for (k, expr), pvals in ptable:
        parse_tbl[k].update({v: (k, expr) for v in pvals})
    return parse_tbl
def parse_helper(grammar, tbl, stack, inplst):
    inp, *inplst = inplst
    exprs = []
    while stack:
        val, *stack = stack
        if isinstance(val, tuple):
            exprs.append(val)
        elif val not in grammar:  # terminal
            assert val == inp
            exprs.append(val)
            inp, *inplst = inplst or [None]
        else:
            _, rhs = tbl[val][inp] if inp else (None, [])
            stack = rhs + [(val, len(rhs))] + stack
    return exprs
def parse(grammar, start, inp):
    my_rules = rules(grammar)
    parse_tbl = parse_table(grammar, start, my_rules)
    k, _ = my_rules[0]
    stack = [k]
    return parse_helper(grammar, parse_tbl, stack, list(inp))
def linear_to_tree(arr):
    stack = []
    while arr:
        elt = arr.pop(0)
        if not isinstance(elt, tuple):
            stack.append((elt, []))
        else:
            # get the last n
            sym, n = elt
            elts = stack[-n:] if n > 0 else []
            stack = stack[0:len(stack) - n]
            stack.append((sym, elts))
    assert len(stack) == 1
    return stack[0]
START_SYMBOL = '<start>'
grammar = {'<start>': [['<expr>']],
 '<expr>': [['<term>', '<expr_>']],
 '<expr_>': [['+', '<expr>'], ['-', '<expr>'], []],
 '<term>': [['<factor>', '<term_>']],
 '<term_>': [['*', '<term>'], ['/', '<term>'], []],
 '<factor>': [['+', '<factor>'],
  ['-', '<factor>'],
  ['(', '<expr>', ')'],
  ['<int>']],
 '<int>': [['<integer>', '<integer_>']],
 '<integer_>': [[], ['.', '<integer>']],
 '<integer>': [['<digit>', '<I>']],
 '<I>': [['<integer>'], []],
 '<digit>': [['0'],
  ['1'],
  ['2'],
  ['3'],
  ['4'],
  ['5'],
  ['6'],
  ['7'],
  ['8'],
  ['9']]}

tree = linear_to_tree(parse(grammar, START_SYMBOL, '(1+2)*3'))
print(tree)
