# optimizer.py (CORRIGIDO)
from typing import List, Dict, Any, Set

class Optimizer:
    def __init__(self):
        # Este otimizador é simples e não mantém estado entre as chamadas
        pass

    def dead_code_elimination(self, ir_code: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove instruções cujo destino não é usado posteriormente.
        Funciona melhor em uma única passagem para variáveis temporárias.
        """
        used_vars: Set[str] = set()
        # Passada reversa para encontrar variáveis usadas antes de serem definidas
        for instr in reversed(ir_code):
            if instr.get("arg1") and isinstance(instr["arg1"], str):
                used_vars.add(instr["arg1"])
            if instr.get("arg2") and isinstance(instr["arg2"], str):
                used_vars.add(instr["arg2"])
        
        optimized_code = []
        for instr in ir_code:
            dest = instr.get("dest")
            # Mantém a instrução se ela não tiver destino (ex: GOTO, LABEL, PRINT)
            # ou se o destino for usado em algum lugar.
            # Funções e labels principais também são mantidos.
            if dest is None or dest in used_vars or instr['op'] in ('FUNC_BEGIN', 'LABEL'):
                optimized_code.append(instr)
        
        return optimized_code

    # Outras otimizações (propagação de constantes, etc.) são complexas
    # e exigiriam uma análise de fluxo de controle mais robusta.
    # Por enquanto, focaremos na eliminação de código morto, que é mais segura.

    def optimize(self, ir_code: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Pipeline principal de otimizações.
        """
        print("\n[Optimizer] Iniciando otimizações...")
        
        # A otimização é executada múltiplas vezes para garantir que as melhorias se propaguem
        # Por exemplo, remover código morto pode abrir portas para mais otimizações.
        previous_len = len(ir_code) + 1
        while len(ir_code) < previous_len:
            previous_len = len(ir_code)
            # Adicione outras funções de otimização aqui no futuro
            ir_code = self.dead_code_elimination(ir_code)
        
        print(f"[Optimizer] Otimizações concluídas. Tamanho do IR reduzido para {len(ir_code)} instruções.")
        return ir_code