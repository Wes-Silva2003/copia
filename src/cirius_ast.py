# cirius_ast.py - Estrutura de AST para a linguagem Cirius

class Node:
    """Classe base para todos os nós da AST"""
    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, d):
        obj = cls.__new__(cls)
        obj.__dict__.update(d)
        return obj

class Program(Node):
    def __init__(self, functions=None):
        self.functions = functions or []

class FunctionDecl(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class Block(Node):
    def __init__(self, statements=None):
        self.statements = statements or []

class Assignment(Node):
    def __init__(self, target, expr):
        self.target = target
        self.expr = expr

class Var(Node):
    def __init__(self, name):
        self.name = name

class Number(Node):
    def __init__(self, value):
        self.value = value

class String(Node):
    def __init__(self, value):
        self.value = value

class Boolean(Node):
    def __init__(self, value):
        self.value = value

class BinaryOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp(Node):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class IfStatement(Node):
    def __init__(self, cond, then, elifs=None, otherwise=None):
        self.cond = cond
        self.then = then
        self.elifs = elifs or []
        self.otherwise = otherwise

class WhileStatement(Node):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

class ForStatement(Node):
    def __init__(self, var, start, end, body):
        self.var = var
        self.start = start
        self.end = end
        self.body = body

class ReturnStatement(Node):
    def __init__(self, value):
        self.value = value

class PrintStatement(Node):
    def __init__(self, value):
        self.value = value

class InputStatement(Node):
    pass

class FunctionCall(Node):
    def __init__(self, name, args=None):
        self.name = name
        self.args = args or []
