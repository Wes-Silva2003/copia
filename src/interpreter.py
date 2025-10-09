# interpreter.py - Interpretador para a AST da linguagem Cirius

from cirius_ast import *

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Variável '{name}' não definida.")

    def assign(self, name, value):
        self.vars[name] = value

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self._add_builtins()

    def _add_builtins(self):
        self.globals.assign("str", lambda x: str(x))
        self.globals.assign("input", lambda: input())  # texto
        self.globals.assign("int", lambda x: int(x))
        self.globals.assign("float", lambda x: float(x))
        self.globals.assign("bool", lambda x: bool(x))
        # Se quiser: self.globals.assign("len", lambda x: len(x))

    def interpret(self, node: Program):
        try:
            for func_decl in node.functions:
                self.globals.assign(func_decl.name, func_decl)

            main_func = self.globals.get("main")
            if not main_func or not isinstance(main_func, FunctionDecl):
                raise RuntimeError("Função 'main' não encontrada.")
            
            self.visit(main_func, self.globals)

        except (NameError, TypeError, RuntimeError) as e:
            print(f"[Erro de Execução] {e}")

    def visit(self, node, env: Environment):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node, env)

    def generic_visit(self, node, env: Environment):
        raise NotImplementedError(f"Nenhum método visit_{type(node).__name__} implementado.")

    def visit_Number(self, node: Number, env: Environment):
        return node.value

    def visit_String(self, node: String, env: Environment):
        return node.value

    def visit_Boolean(self, node: Boolean, env: Environment):
        return node.value

    def visit_Var(self, node: Var, env: Environment):
        return env.get(node.name)

    def visit_Block(self, node: Block, env: Environment):
        block_env = Environment(parent=env)
        for statement in node.statements:
            self.visit(statement, block_env)

    def visit_Assignment(self, node: Assignment, env: Environment):
        var_name = node.target.name
        value = self.visit(node.expr, env)
        env.assign(var_name, value)

    def visit_BinaryOp(self, node: BinaryOp, env: Environment):
        left_val = self.visit(node.left, env)
        right_val = self.visit(node.right, env)

        op_map = {
            "PLUS": lambda a, b: a + b, "MINUS": lambda a, b: a - b,
            "MUL": lambda a, b: a * b, "DIV": lambda a, b: a / b,
            "MOD": lambda a, b: a % b,
            "GT": lambda a, b: a > b, "LT": lambda a, b: a < b,
            "GE": lambda a, b: a >= b, "LE": lambda a, b: a <= b,
            "EQ": lambda a, b: a == b, "NE": lambda a, b: a != b,
            "AND": lambda a, b: a and b, "OR": lambda a, b: a or b,
        }
        if node.op in op_map:
            return op_map[node.op](left_val, right_val)
        raise RuntimeError(f"Operador binário desconhecido: {node.op}")

    def visit_UnaryOp(self, node: UnaryOp, env: Environment):
        operand_val = self.visit(node.operand, env)
        if node.op == "MINUS":
            return -operand_val
        if node.op == "NOT":
            return not operand_val
        raise RuntimeError(f"Operador unário desconhecido: {node.op}")

    def visit_IfStatement(self, node: IfStatement, env: Environment):
        cond_val = self.visit(node.cond, env)
        if cond_val:
            self.visit(node.then, env)
        else:
            for elif_cond, elif_block in node.elifs:
                if self.visit(elif_cond, env):
                    self.visit(elif_block, env)
                    return
            if node.otherwise:
                self.visit(node.otherwise, env)

    def visit_WhileStatement(self, node: WhileStatement, env: Environment):
        while self.visit(node.cond, env):
            self.visit(node.body, env)

    def visit_ForStatement(self, node: ForStatement, env: Environment):
        start_val = self.visit(node.start, env)
        end_val = self.visit(node.end, env)
        loop_env = Environment(parent=env)

        for i in range(start_val, end_val + 1):
            loop_env.assign(node.var, i)
            self.visit(node.body, loop_env)

    def visit_PrintStatement(self, node: PrintStatement, env: Environment):
        value = self.visit(node.value, env)
        print(value)

    def visit_InputStatement(self, node: InputStatement, env: Environment):
        try:
            return int(input())
        except ValueError:
            raise RuntimeError("Entrada inválida. Esperado um número inteiro.")

    def visit_FunctionDecl(self, node: FunctionDecl, env: Environment):
        func_env = Environment(parent=self.globals)
        self.visit(node.body, func_env)

    def visit_FunctionCall(self, node: FunctionCall, env: Environment):
        func = env.get(node.name)

        # 🧠 Função embutida (built-in)
        if callable(func):
            args = [self.visit(arg, env) for arg in node.args]
            try:
                return func(*args)
            except Exception as e:
                raise RuntimeError(f"Erro ao chamar função embutida '{node.name}': {e}")

        # 🧠 Função definida pelo usuário
        if isinstance(func, FunctionDecl):
            if len(node.args) != len(func.params):
                raise TypeError(f"Função '{node.name}' espera {len(func.params)} argumentos, mas recebeu {len(node.args)}.")

            arg_values = [self.visit(arg, env) for arg in node.args]
            call_env = Environment(parent=self.globals)
            for param_name, arg_val in zip(func.params, arg_values):
                call_env.assign(param_name, arg_val)
            self.visit(func.body, call_env)
            return

        raise TypeError(f"'{node.name}' não é uma função.")
