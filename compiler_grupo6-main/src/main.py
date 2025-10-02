# main.py - Orquestrador do compilador/interpretador Cirius

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List

# Imports do compilador
from lexer import Lexer
from parser_1 import Parser
from cirius_ast import Node, Program
from semantic import SemanticAnalyzer
from ir import IRGenerator
from optimize import Optimizer
from codegen import CodeGenerator
from interpreter import Interpreter # <-- NOVO IMPORT

# -------------------------
# Utilitários (sem alterações)
# -------------------------
def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def write_file(path: str, contents: str):
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "w", encoding="utf-8") as f:
        f.write(contents)

# ... (todas as outras funções utilitárias como safe_json_dump e normalize_ir permanecem iguais)
def safe_json_dump(obj, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=lambda o: o.to_dict() if isinstance(o, Node) else o.__dict__)

def normalize_ir(ir_list: List[Any]) -> List[Dict[str, Any]]:
    normalized = []
    for instr in ir_list:
        if instr is None: continue
        if isinstance(instr, dict):
            normalized.append(instr)
        else:
            d = {"op": getattr(instr, "op", None)}
            for attr in ["dest", "arg1", "arg2"]:
                if hasattr(instr, attr):
                    val = getattr(instr, attr)
                    if val is not None: d[attr] = val
            normalized.append(d)
    return normalized

# -------------------------
# Funções de Pipeline
# -------------------------
def compile_pipeline(source: str, output_path: str, verbose=False):
    """Executa o pipeline de compilação para gerar código C."""
    if verbose: print(f"\n[Compilando] {source[:30].strip()}... -> {output_path}")

    # 1. Lexer
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    if verbose: print(f"[Lexer] {len(tokens)} tokens gerados.")

    # 2. Parser
    parser = Parser(tokens)
    ast = parser.parse()
    if verbose: print("[Parser] AST gerada com sucesso.")

    # 3. Análise Semântica
    sema = SemanticAnalyzer()
    try:
        sema.analyze(ast)
        if verbose: print("[Semântica] Nenhum erro semântico encontrado.")
    except Exception as e:
        print(f"[ERRO Semântico] {e}")
        return

    # 4. Geração de IR
    irgen = IRGenerator()
    ir_code = normalize_ir(irgen.generate(ast))
    if verbose: print(f"[IR] Geradas {len(ir_code)} instruções.")

    # 5. Otimização
    opt = Optimizer()
    ir_opt = opt.optimize(ir_code)

    # 6. Geração de Código
    cg = CodeGenerator()
    c_code = cg.generate(ir_opt)
    write_file(output_path, c_code)
    if verbose: print(f"[CodeGen] Código C gerado em {output_path} (tamanho {len(c_code)})")
    print(f"[OK] Compilado para {output_path}")

def run_pipeline(source: str, verbose=False):
    """Executa o pipeline do interpretador."""
    if verbose: print(f"\n[Executando] {source[:30].strip()}...")

    # 1. Lexer
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    if verbose: print(f"[Lexer] {len(tokens)} tokens gerados.")
    
    # 2. Parser
    parser = Parser(tokens)
    ast = parser.parse()
    if verbose: print("[Parser] AST gerada com sucesso.")

    # 3. Análise Semântica
    sema = SemanticAnalyzer()
    try:
        sema.analyze(ast)
        if verbose: print("[Semântica] Nenhum erro semântico encontrado.")
    except Exception as e:
        print(f"[ERRO Semântico] {e}")
        return
        
    # 4. Interpretação
    if verbose: print("[Interpretador] Iniciando execução...")
    interpreter = Interpreter()
    interpreter.interpret(ast)
    if verbose: print("[Interpretador] Execução concluída.")


# -------------------------
# CLI
# -------------------------
def main():
    parser = argparse.ArgumentParser(description="Compilador/Interpretador Cirius")
    parser.add_argument("--verbose", action="store_true", help="Mostra detalhes do processo.")
    
    subparsers = parser.add_subparsers(dest="command", required=True, help="Comando a ser executado")

    # Comando 'compile'
    parser_compile = subparsers.add_parser("compile", help="Compila um arquivo .cir para .c")
    parser_compile.add_argument("input_path", help="Arquivo .cir de entrada")
    parser_compile.add_argument("-o", "--output", help="Arquivo .c de saída (opcional)")

    # Comando 'run'
    parser_run = subparsers.add_parser("run", help="Executa (interpreta) um arquivo .cir")
    parser_run.add_argument("input_path", help="Arquivo .cir para executar")

    args = parser.parse_args()
    
    source_code = Path(args.input_path).read_text(encoding="utf-8")

    if args.command == "compile":
        output_path = args.output or str(Path(args.input_path).with_suffix(".c"))
        compile_pipeline(source_code, output_path, args.verbose)
    elif args.command == "run":
        run_pipeline(source_code, args.verbose)

if __name__ == "__main__":
    main()