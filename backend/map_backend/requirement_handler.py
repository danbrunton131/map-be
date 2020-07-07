AND = 0
OR = 1

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        if self.op == AND:
            operator = "AND"
        else:
            operator = "OR"

        return "({}) {} ({})".format(str(self.left), operator, str(self.right))

class Parser:

    def __init__(self, req, precedence):
        self.req = req
        self.curr = 0
        self.sym = self.req[self.curr]
        # Details what binds tighters
        self.precedence = precedence

    def nxt(self):
        if self.curr < len(self.req):
            self.sym, self.curr = self.req[self.curr], self.curr + 1
        else:
            self.sym = None

    def factor(self):
        node = self.term()

        while self.sym == OR:
            token = self.sym
            self.nxt()
            if self.precedence == AND:
                node = BinOp(node, token, self.term())
            else:
                node = BinOp(node, token, self.expr())

        return node

    def term(self):
        node = self.expr()

        while self.sym == AND:
            token = self.sym
            self.nxt()
            if self.precedence == AND:
                node = BinOp(node, token, self.expr())
            else:
                node = BinOp(node, token, self.factor())

        return node

    def expr(self):
        res = self.sym
        self.nxt()
        return res

    def parse(self):
        self.nxt()

        if self.precedence == AND:
            return self.factor()
        else:
            return self.term()
