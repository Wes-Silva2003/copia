# codegen.py
"""
Cirius Compiler - Gerador de Código C
Gera código C a partir do IR (TAC) produzido pelo IRGenerator.
"""

from typing import List

class CodeGenerator:
    def __init__(self):
        self.output = []
        self.indent_level = 0

    # -------------------------------
    # Utilitários
    # -------------------------------
    def emit(self, code: str):
        self.output.append("    " * self.indent_level + code)

    def indent(self):
        self.indent_level += 1

    def dedent(self):
        self.indent_level = max(0, self.indent_level - 1)

    # -------------------------------
    # Geração Principal
    # -------------------------------
    def generate(self, ir: List[dict]) -> str:
        self.output = []
        self.emit("#include <stdio.h>")
        self.emit("")
        for instr in ir:
            self.gen_instruction(instr)
        return "\n".join(self.output)

    # -------------------------------
    # Instruções
    # -------------------------------
    def gen_instruction(self, instr: dict):
        op = instr.get("op")
        dest = instr.get("dest")
        arg1 = instr.get("arg1")
        arg2 = instr.get("arg2")

        if op == "FUNC_BEGIN":
            self.emit(f"void {dest}() {{")
            self.indent()
        elif op == "FUNC_END":
            self.dedent()
            self.emit("}")
            self.emit("")
        elif op == "ASSIGN":
            self.emit(f"int {dest} = {arg1};")
        elif op == "PRINT":
            self.emit(f'printf("%d\\n", {arg1});')
        elif op == "INPUT":
            self.emit(f"scanf(\"%d\", &{dest});")
        elif op == "GOTO":
            self.emit(f"goto {dest};")
        elif op == "IF_FALSE_GOTO":
            self.emit(f"if (!{arg1}) goto {dest};")
        elif op == "LABEL":
            self.emit(f"{dest}: ;")
        elif op in ("ADD", "SUB", "MUL", "DIV"):
            self.emit(f"int {dest} = {arg1} {self.op_to_symbol(op)} {arg2};")
        else:
            self.emit(f"// [ERRO] operação não suportada: {op}")

    def op_to_symbol(self, op: str) -> str:
        return {
            "ADD": "+",
            "SUB": "-",
            "MUL": "*",
            "DIV": "/"
        }.get(op, "?")
