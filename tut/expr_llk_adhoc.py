class g_parse:
    def __init__(self, g): self._g = g

    def remain(self): return self._len - self._i

    def next_token(self):
        try: return None if self._i + 1 > self._len else self._str[self._i]
        finally: self._i += 1

    def match(self, t): return self.next_token() == t

    def is_nt(self, key): return key in self._g

    def do_seq(self, seq_terms): return all(self.do_alt(t) for t in seq_terms)

    def _try(self, fn):
        o_pos = self._i
        if fn(): return True
        self._i = o_pos

    def do_alt(self, key):
        if not self.is_nt(key): return self.match(key)
        return any(self._try(lambda: self.do_seq(ts)) for ts in self._g[key])

    def parse(self, i):
        self._str, self._len, self._i = i, len(i), 0
        self.do_alt('expr')
        assert self.remain() == 0

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
    g_parse(my_grammar).parse(sys.argv[1])
