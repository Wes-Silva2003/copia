# semantic.py - Analisador semântico compatível com AST

from cirius_ast import *

# Exceção para erros semânticos
class SemanticError(Exception):
    pass

# Representa uma função embutida (ex: str, print)
class BuiltinFunction:
    def __init__(self, name, arity):
        self.name = name
        self.arity = arity

# Tabela de símbolos com escopo
class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def define(self, name, value):
        if name in self.symbols:
            raise SemanticError(f"Símbolo '{name}' já declarado.")
        self.symbols[name] = value

    def resolve(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.resolve(name)
        raise SemanticError(f"Símbolo '{name}' não declarado.")

# Analisador semântico principal
class SemanticAnalyzer:
    def __init__(self):
        self.global_scope = SymbolTable()
        self.current_scope = self.global_scope

        # Adiciona funções built-in conhecidas
        self._add_builtins()

    def _add_builtins(self):
        self.global_scope.define("str", BuiltinFunction("str", 1))
        self.global_scope.define("print", BuiltinFunction("print", 1))  # pode adaptar para vários args
        self.global_scope.define("input", BuiltinFunction("input", 0))

    def analyze(self, node):
        method = f"visit_{type(node).__name__}"
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise SemanticError(f"Semântico não implementado para {type(node).__name__}")

    def visit_Program(self, node: Program):
        for func in node.functions:
            self.analyze(func)

    def visit_FunctionDecl(self, node: FunctionDecl):
        self.global_scope.define(node.name, node)
        prev_scope = self.current_scope
        self.current_scope = SymbolTable(parent=self.global_scope)
        for param in node.params:
            self.current_scope.define(param, "param")
        self.analyze(node.body)
        self.current_scope = prev_scope

    def visit_Block(self, node: Block):
        prev_scope = self.current_scope
        self.current_scope = SymbolTable(parent=prev_scope)
        for stmt in node.statements:
            self.analyze(stmt)
        self.current_scope = prev_scope

    def visit_Assignment(self, node: Assignment):
        self.analyze(node.expr)
        if isinstance(node.target, Var):
            if node.target.name not in self.current_scope.symbols:
                self.current_scope.define(node.target.name, "var")
        else:
            self.analyze(node.target)

    def visit_Var(self, node: Var):
        self.current_scope.resolve(node.name)

    def visit_Number(self, node: Number): pass
    def visit_String(self, node: String): pass
    def visit_Boolean(self, node: Boolean): pass

    def visit_BinaryOp(self, node: BinaryOp):
        self.analyze(node.left)
        self.analyze(node.right)

    def visit_UnaryOp(self, node: UnaryOp):
        self.analyze(node.operand)

    def visit_IfStatement(self, node: IfStatement):
        self.analyze(node.cond)
        self.analyze(node.then)
        for cond, blk in node.elifs:
            self.analyze(cond)
            self.analyze(blk)
        if node.otherwise:
            self.analyze(node.otherwise)

    def visit_WhileStatement(self, node: WhileStatement):
        self.analyze(node.cond)
        self.analyze(node.body)

    def visit_ForStatement(self, node: ForStatement):
        prev_scope = self.current_scope
        self.current_scope = SymbolTable(parent=prev_scope)
        self.current_scope.define(node.var, "var")
        self.analyze(node.start)
        self.analyze(node.end)
        self.analyze(node.body)
        self.current_scope = prev_scope

    def visit_ReturnStatement(self, node: ReturnStatement):
        if node.value:
            self.analyze(node.value)

    def visit_PrintStatement(self, node: PrintStatement):
        self.analyze(node.value)

    def visit_InputStatement(self, node: InputStatement):
        pass

    def visit_FunctionCall(self, node: FunctionCall):
        func = self.global_scope.resolve(node.name)

        if isinstance(func, FunctionDecl):
            if len(node.args) != len(func.params):
                raise SemanticError(
                    f"Função '{node.name}' espera {len(func.params)} argumento(s), mas recebeu {len(node.args)}"
                )

        elif isinstance(func, BuiltinFunction):
            if func.arity != len(node.args):
                raise SemanticError(
                    f"Função embutida '{node.name}' espera {func.arity} argumento(s), mas recebeu {len(node.args)}"
                )

        else:
            raise SemanticError(f"'{node.name}' não é uma função.")

        for arg in node.args:
            self.analyze(arg)
