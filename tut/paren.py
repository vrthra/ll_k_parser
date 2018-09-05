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

def do_seq(seq_terms):
   for t in seq_terms:
       if not do_alt(t): return False
   return True

def do_alt(key):
    if key not in grammar: return match(key)
    alt_terms = grammar[key]
    for ts in alt_terms:
        o_pos = pos_cur()
        if do_seq(ts): return True
        pos_set(o_pos)
    return False

def parse(i, g):
    global my_input
    global grammar
    grammar = g
    my_input = i
    do_alt('expr')
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

    import sys
    parse(sys.argv[1], my_grammar)
