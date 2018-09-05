my_input, grammar, cur_position = None, None, 0

def pos_cur(): return cur_position

def pos_set(i):
    global cur_position
    cur_position = i

def pos_eof(): return pos_cur() == len(my_input)

def next_token():
    i = pos_cur()
    if i+1 > len(my_input): return None
    pos_set(i+1)
    return my_input[i]

def match(t): return next_token() == t

def is_terminal(val): return val not in grammar
def is_nonterminal(val): return val in grammar
EOF = '\0'

def first(tok):
    # If X is a terminal then First(X) is just X!
    if is_terminal(tok): return set([tok])
    res = set()
    for rule in grammar[tok]:
        if not rule:
            # If there is a Production X -> ε then add ε to first(X)
            res |= set([''])
        else:
            # If there is a Production X -> Y1Y2..Yk then add first(Y1Y2..Yk) to first(X)
            tokens = rule #  $ is being missed here.
            add_empty = True
            for t in tokens:
                # First(Y1Y2..Yk) is either
                # First(Y1) (if First(Y1) doesn't contain ε)
                if t == tok: # recursion
                    continue
                r = first(t)
                if '' not in r:
                    res |= r
                    add_empty = False
                    break
                else:
                    # OR First (Y1Y2..Yk) is everything in First(Y1) <except for ε > as well as everything in First(Y2..Yk)
                    r.remove('')
                    res |= r

                # If First(Y1) First(Y2)..First(Yk) all contain ε then add ε to First(Y1Y2..Yk) as well.
            if add_empty:
                res |= set([''])
    return res

def follow(start='$START', fdict={}):
    # First put $ (the end of input marker) in Follow(S) (S is the start symbol)
    fdict = fdict or {k:set() for k in grammar.keys()}

    updates = []

    fdict[start] |= {EOF}
    for key in sorted(grammar.keys()):
        for rule in grammar[key]:
            tokens = rule
            A = key
            for i, B in enumerate(tokens):
                if not B: continue
                if is_nonterminal(B):
                    if (i + 1) != len(tokens):
                        # If there is a production A → aBb, then everything in FIRST(b) except for ε is placed in FOLLOW(B).
                        # If there is a production A → aBb, where FIRST(b) contains ε, then everything in FOLLOW(A) is in FOLLOW(B)
                        b = tokens[i+1]
                        fb = first(b)
                        if '' in fb:
                            updates.append((B,A))
                            fdict[B] |= fdict[A]
                            fb.remove('')
                        fdict[B] |= fb
                    else: # if B is the end.
                        # If there is a production A → aB, then everything in FOLLOW(A) is in FOLLOW(B)
                        fdict[B] |= fdict[A]
                        updates.append((B,A))

    cont = True
    while cont:
        cont = False
        for k,v in updates:
            val= (fdict[v] - fdict[k])
            if val:
               cont = True
               fdict[k] |= val
    return fdict

def parse(i, g, start):
    global my_input
    global grammar
    grammar = g
    my_input = i
    stack = []
    stack.append(start) 
    token = next_token()
    while stack:
        top = stack[-1]
        if is_nonterminal(top):
            action = parse_table[top][token]
            if action > 0:
                stack.pop()
                for symbol on RHS[action]:
                    stack.append(symbol)
                else:
                    print('error')
                    raise Error()
            elif token == top:
                stack.pop()
                token = next_token()
            else:
                print('error')
                raise Error()

    assert pos_eof()

if __name__ == '__main__':
    my_grammar = {
            "expr": [
                ["term", "add_op", "expr"],
                ["term"]],
            "term": [
                ["fact", "mul_op", "term"],
                ["fact"]],
            "fact": [
                ["digits"],
                ["(", "expr", ")"]],
            "digits": [
                ["digit", "digits"],
                ["digit"]],
            "digit": [[str(i)] for i in list(range(10))],
            "add_op": [["+"], ["-"]],
            "mul_op": [["*"], ["/"]]}

    grammar = my_grammar
    import sys
    fdict = follow('expr')
    print(sorted(fdict[sys.argv[1]]))
    #import sys
    #parse(sys.argv[1], my_grammar)

