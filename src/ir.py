"""
ir.py - Gerador de código intermediário (TAC) para a linguagem Cirius
Compatível com a AST atual (FunctionDecl, IfStatement, WhileStatement, etc.)
"""

from cirius_ast import *

class IRInstruction:
    def __init__(self, op, dest=None, arg1=None, arg2=None):
        self.op = op
        self.dest = dest
        self.arg1 = arg1
        self.arg2 = arg2

    def __repr__(self):
        parts = [self.op]
        if self.dest is not None:
            parts.append(str(self.dest))
        if self.arg1 is not None:
            parts.append(str(self.arg1))
        if self.arg2 is not None:
            parts.append(str(self.arg2))
        return " ".join(parts)


class IRGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0

    def new_temp(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self, prefix="L"):
        self.label_counter += 1
        return f"{prefix}{self.label_counter}"

    # -------------------------
    # Função principal
    # -------------------------
    def generate(self, program: Program):
        for func in program.functions:
            self.gen_function(func)
        return self.instructions

    # -------------------------
    # Funções
    # -------------------------
    def gen_function(self, func: FunctionDecl):
        self.instructions.append(IRInstruction("FUNC_BEGIN", dest=func.name))
        self.gen_block(func.body)
        self.instructions.append(IRInstruction("FUNC_END", dest=func.name))

    # -------------------------
    # Blocos
    # -------------------------
    def gen_block(self, block: Block):
        for stmt in block.statements:
            self.gen_statement(stmt)

    # -------------------------
    # Statements
    # -------------------------
    def gen_statement(self, stmt):
        if isinstance(stmt, Assignment):
            value = self.gen_expression(stmt.expr)
            self.instructions.append(IRInstruction("ASSIGN", dest=stmt.target.name, arg1=value))
        elif isinstance(stmt, FunctionCall):
            args = [self.gen_expression(arg) for arg in stmt.args]
            for arg in args:
                self.instructions.append(IRInstruction("ARG", arg1=arg))
            self.instructions.append(IRInstruction("CALL", dest=stmt.name, arg1=len(args)))
        elif isinstance(stmt, PrintStatement):
            val = self.gen_expression(stmt.value)
            self.instructions.append(IRInstruction("PRINT", arg1=val))
        elif isinstance(stmt, InputStatement):
            temp = self.new_temp()
            self.instructions.append(IRInstruction("INPUT", dest=temp))
            return temp
        elif isinstance(stmt, ReturnStatement):
            val = self.gen_expression(stmt.value) if stmt.value else None
            self.instructions.append(IRInstruction("RETURN", arg1=val))
        elif isinstance(stmt, IfStatement):
            self.gen_if(stmt)
        elif isinstance(stmt, WhileStatement):
            self.gen_while(stmt)
        elif isinstance(stmt, ForStatement):
            self.gen_for(stmt)
        else:
            raise Exception(f"IR generation not implemented for {type(stmt).__name__}")

    # -------------------------
    # If / Elif / Else
    # -------------------------
    def gen_if(self, stmt: IfStatement):
        label_end = self.new_label("END_IF")
        label_else_list = [self.new_label("ELIF") for _ in stmt.elifs]
        label_else_main = self.new_label("ELSE") if stmt.otherwise else label_end

        # IF principal
        cond_temp = self.gen_expression(stmt.cond)
        first_label = label_else_list[0] if stmt.elifs else label_else_main
        self.instructions.append(IRInstruction("IF_FALSE_GOTO", cond_temp, first_label))
        self.gen_block(stmt.then)
        self.instructions.append(IRInstruction("GOTO", label_end))

        # ELIFs
        for i, (elif_cond, elif_block) in enumerate(stmt.elifs):
            label_next = label_else_list[i + 1] if i + 1 < len(stmt.elifs) else label_else_main
            self.instructions.append(IRInstruction("LABEL", dest=label_else_list[i]))
            cond_temp = self.gen_expression(elif_cond)
            self.instructions.append(IRInstruction("IF_FALSE_GOTO", cond_temp, label_next))
            self.gen_block(elif_block)
            self.instructions.append(IRInstruction("GOTO", label_end))

        # ELSE
        if stmt.otherwise:
            self.instructions.append(IRInstruction("LABEL", dest=label_else_main))
            self.gen_block(stmt.otherwise)

        # END IF
        self.instructions.append(IRInstruction("LABEL", dest=label_end))

    # -------------------------
    # While
    # -------------------------
    def gen_while(self, stmt: WhileStatement):
        label_start = self.new_label("WHILE")
        label_end = self.new_label("END_WHILE")

        self.instructions.append(IRInstruction("LABEL", dest=label_start))
        cond_temp = self.gen_expression(stmt.cond)
        self.instructions.append(IRInstruction("IF_FALSE_GOTO", cond_temp, label_end))
        self.gen_block(stmt.body)
        self.instructions.append(IRInstruction("GOTO", label_start))
        self.instructions.append(IRInstruction("LABEL", dest=label_end))

    # -------------------------
    # For (range)
    # -------------------------
    def gen_for(self, stmt: ForStatement):
        # stmt.var, stmt.start, stmt.end, stmt.body
        label_start = self.new_label("FOR")
        label_end = self.new_label("END_FOR")

        start_val = self.gen_expression(stmt.start)
        self.instructions.append(IRInstruction("ASSIGN", dest=stmt.var, arg1=start_val))

        self.instructions.append(IRInstruction("LABEL", dest=label_start))
        end_val = self.gen_expression(stmt.end)
        cond_temp = self.new_temp()
        self.instructions.append(IRInstruction("LT_EQ", dest=cond_temp, arg1=stmt.var, arg2=end_val))
        self.instructions.append(IRInstruction("IF_FALSE_GOTO", cond_temp, label_end))
        self.gen_block(stmt.body)
        self.instructions.append(IRInstruction("ADD", dest=stmt.var, arg1=stmt.var, arg2=1))
        self.instructions.append(IRInstruction("GOTO", label_start))
        self.instructions.append(IRInstruction("LABEL", dest=label_end))

    # -------------------------
    # Expressões
    # -------------------------
    def gen_expression(self, expr):
        if isinstance(expr, Number):
            return expr.value
        elif isinstance(expr, String):
            return expr.value
        elif isinstance(expr, Boolean):
            return expr.value
        elif isinstance(expr, Var):
            return expr.name
        elif isinstance(expr, UnaryOp):
            right = self.gen_expression(expr.operand)
            temp = self.new_temp()
            self.instructions.append(IRInstruction(expr.op, dest=temp, arg1=right))
            return temp
        elif isinstance(expr, BinaryOp):
            left = self.gen_expression(expr.left)
            right = self.gen_expression(expr.right)
            temp = self.new_temp()
            self.instructions.append(IRInstruction(expr.op, dest=temp, arg1=left, arg2=right))
            return temp
        elif isinstance(expr, FunctionCall):
            args = [self.gen_expression(arg) for arg in expr.args]
            for arg in args:
                self.instructions.append(IRInstruction("ARG", arg1=arg))
            temp = self.new_temp()
            self.instructions.append(IRInstruction("CALL", dest=temp, arg1=expr.name, arg2=len(args)))
            return temp
        elif isinstance(expr, InputStatement):
            temp = self.new_temp()
            self.instructions.append(IRInstruction("INPUT", dest=temp))
            return temp
        else:
            raise Exception(f"IR generation not implemented for {type(expr).__name__}")
