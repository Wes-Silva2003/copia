"""
Cirius Compiler - Analisador Léxico (Lexer)

Este módulo converte o código-fonte da linguagem Cirius em uma sequência de
tokens. Todos os tokens da linguagem são suportados, incluindo operadores
aritméticos, relacionais, lógicos, palavras-chave, literais, comentários e
identificadores.
"""

import re
from collections import namedtuple

# Estrutura de token
Token = namedtuple("Token", ["type", "value", "line", "column"])

# Lista de palavras-chave
KEYWORDS = {
    "func", "if", "elif", "else", "while", "for", "in",
    "print", "input", "return", "true", "false",
    "and", "or", "not", "break", "continue"
}

# Definição dos tokens com regex
TOKEN_SPECIFICATION = [
    # Comentários
    ("COMMENT", r"//.*|#.*|/\*[\s\S]*?\*/"),

    # Literais
    ("FLOAT", r"\d+\.\d+"),
    ("NUMBER", r"\d+"),
    ("STRING", r'"[^"\n]*"'),

    # Palavras-chave
    ("FUNC", r"\bfunc\b"),
    ("IF", r"\bif\b"),
    ("ELIF", r"\belif\b"),
    ("ELSE", r"\belse\b"),
    ("WHILE", r"\bwhile\b"),
    ("FOR", r"\bfor\b"),
    ("IN", r"\bin\b"),
    ("PRINT", r"\bprint\b"),
    ("INPUT", r"\binput\b"),
    ("RETURN", r"\breturn\b"),
    ("TRUE", r"\btrue\b"),
    ("FALSE", r"\bfalse\b"),
    ("AND", r"\band\b"),
    ("OR", r"\bor\b"),
    ("NOT", r"\bnot\b"),
    ("BREAK", r"\bbreak\b"),
    ("CONTINUE", r"\bcontinue\b"),

    # Operadores compostos (precisam vir antes dos simples)
    ("INC", r"\+\+"),
    ("DEC", r"--"),
    ("PLUS_ASSIGN", r"\+="),
    ("MINUS_ASSIGN", r"-="),
    ("MUL_ASSIGN", r"\*="),
    ("DIV_ASSIGN", r"/="),

    # Operadores relacionais
    ("EQ", r"=="),
    ("NE", r"!="),
    ("GE", r">="),
    ("LE", r"<="),
    ("GT", r">"),
    ("LT", r"<"),

    # Operadores aritméticos simples
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("MUL", r"\*"),
    ("DIV", r"/"),
    ("MOD", r"%"),
    ("ASSIGN", r"="),

    # Operadores bit a bit
    ("AND_BIT", r"&"),
    ("OR_BIT", r"\|"),
    ("XOR_BIT", r"\^"),
    ("NOT_BIT", r"~"),
    ("LSHIFT", r"<<"),
    ("RSHIFT", r">>"),

    # Símbolos
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("DOTS", r"\.\."),
    ("SEMICOLON", r";"),
    ("COMMA", r","),

    # Identificadores
    ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_]*"),

    # Espaços em branco (ignorar)
    ("SKIP", r"[ \t\n]+"),

    # Qualquer caractere não reconhecido
    ("MISMATCH", r"."),
]

# Compila o regex mestre
TOK_REGEX = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPECIFICATION)
TOK_REGEX_COMPILED = re.compile(TOK_REGEX)


class Lexer:
    """Implementação do analisador léxico para a linguagem Cirius."""

    def __init__(self, code: str):
        self.code = code

    def tokenize(self):
        """Converte o código-fonte em uma lista de tokens."""
        line_num = 1
        line_start = 0
        tokens = []

        for mo in TOK_REGEX_COMPILED.finditer(self.code):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - line_start + 1

            # Ignora espaços e comentários
            if kind == "SKIP" or kind == "COMMENT":
                line_num += value.count("\n")
                if "\n" in value:
                    line_start = mo.end()
                continue

            # Converte número para int ou float
            if kind == "NUMBER":
                value = int(value)
            elif kind == "FLOAT":
                value = float(value)

            # Identificadores que são palavras-chave viram token especial
            elif kind == "IDENT" and value in KEYWORDS:
                kind = value.upper()

            # Token inesperado
            elif kind == "MISMATCH":
                raise RuntimeError(f"[Erro Léxico] Caractere inesperado '{value}' na linha {line_num}")

            tokens.append(Token(kind, value, line_num, column))

        return tokens


# -------------------------------
# Execução direta para testes
# -------------------------------
if __name__ == "__main__":
    code = '''
    func main() {
        x = input();
        y = x % 2;
        if x > 0 and y == 1 {
            print("Número positivo e ímpar");
        } elif x == 0 {
            print("Zero");
        } else {
            print("Outro caso");
        }
    }
    '''
    lexer = Lexer(code)
    for token in lexer.tokenize():
        print(token)