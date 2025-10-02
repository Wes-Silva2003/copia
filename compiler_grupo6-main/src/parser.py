# parser.py - Analisador sintático (Parser) para Cirius
from cirius_ast import *

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ("EOF", None)

    def consume(self, expected_type=None):
        if self.pos >= len(self.tokens):
            raise ParserError("Fim inesperado dos tokens")
        token = self.tokens[self.pos]
        if expected_type and token[0] != expected_type:
            raise ParserError(f"Esperado {expected_type}, mas encontrado {token[0]}")
        self.pos += 1
        return token

    def match(self, *types):
        if self.peek()[0] in types:
            return self.consume()
        return None

    # --------------------------
    # Regras principais
    # --------------------------
    def parse(self):
        functions = []
        while self.pos < len(self.tokens):
            functions.append(self.parse_function())
        return Program(functions)

    def parse_function(self):
        self.consume("FUNC")
        name = self.consume("IDENT")[1]

        self.consume("LPAREN")
        params = []
        if self.peek()[0] != "RPAREN":
            params.append(self.consume("IDENT")[1])
            while self.match("COMMA"):
                params.append(self.consume("IDENT")[1])
        self.consume("RPAREN")

        self.consume("LBRACE")
        body = self.parse_block()
        self.consume("RBRACE")
        return FunctionDecl(name, params, body)

    def parse_block(self):
        statements = []
        while self.peek()[0] not in ("RBRACE", "EOF"):
            if self.peek()[0] == "SEMICOLON":
                self.consume()
                continue
            statements.append(self.parse_statement())
        return Block(statements)

    def parse_statement(self):
        token = self.peek()[0]
        if token == "IF":
            return self.parse_if()
        elif token == "WHILE":
            return self.parse_while()
        elif token == "FOR":
            return self.parse_for()
        elif token == "RETURN":
            return self.parse_return()
        elif token == "PRINT":
            return self.parse_print()
        elif token == "INPUT":
            return self.parse_input()
        elif token == "IDENT":
            return self.parse_assignment_or_call()
        else:
            raise ParserError(f"Instrução inesperada: {token}")

    # --- Estruturas de controle ---
    def parse_if(self):
        self.consume("IF")
        if self.peek()[0] == "LPAREN":
            self.consume("LPAREN")
            cond = self.parse_expression()
            self.consume("RPAREN")
        else:
            cond = self.parse_expression()

        self.consume("LBRACE")
        then_branch = self.parse_block()
        self.consume("RBRACE")

        elifs = []
        while self.peek()[0] == "ELIF":
            self.consume("ELIF")
            if self.peek()[0] == "LPAREN":
                self.consume("LPAREN")
                c = self.parse_expression()
                self.consume("RPAREN")
            else:
                c = self.parse_expression()
            self.consume("LBRACE")
            blk = self.parse_block()
            self.consume("RBRACE")
            elifs.append((c, blk))

        else_branch = None
        if self.peek()[0] == "ELSE":
            self.consume("ELSE")
            self.consume("LBRACE")
            else_branch = self.parse_block()
            self.consume("RBRACE")

        return IfStatement(cond, then_branch, elifs, else_branch)

    def parse_while(self):
        self.consume("WHILE")
        if self.peek()[0] == "LPAREN":
            self.consume("LPAREN")
            cond = self.parse_expression()
            self.consume("RPAREN")
        else:
            cond = self.parse_expression()
        self.consume("LBRACE")
        body = self.parse_block()
        self.consume("RBRACE")
        return WhileStatement(cond, body)

    def parse_for(self):
        self.consume("FOR")
        var = self.consume("IDENT")[1]
        self.consume("IN")
        start = self.parse_expression()
        self.consume("DOTS")
        end = self.parse_expression()
        self.consume("LBRACE")
        body = self.parse_block()
        self.consume("RBRACE")
        return ForStatement(var, start, end, body)

    def parse_return(self):
        self.consume("RETURN")
        expr = self.parse_expression()
        return ReturnStatement(expr)

    def parse_print(self):
        self.consume("PRINT")
        self.consume("LPAREN")
        expr = self.parse_expression()
        self.consume("RPAREN")
        return PrintStatement(expr)

    def parse_input(self):
        self.consume("INPUT")
        self.consume("LPAREN")
        self.consume("RPAREN")
        return InputStatement()

    def parse_assignment_or_call(self):
        name = self.consume("IDENT")[1]
        if self.peek()[0] == "ASSIGN":
            self.consume("ASSIGN")
            expr = self.parse_expression()
            return Assignment(Var(name), expr)
        elif self.peek()[0] == "LPAREN":
            self.consume("LPAREN")
            args = []
            if self.peek()[0] != "RPAREN":
                args.append(self.parse_expression())
                while self.match("COMMA"):
                    args.append(self.parse_expression())
            self.consume("RPAREN")
            return FunctionCall(name, args)
        else:
            raise ParserError("Esperado '=' ou '(' após identificador")

    # --- Expressões ---
    def parse_expression(self):
        return self.parse_logic_or()

    def parse_logic_or(self):
        expr = self.parse_logic_and()
        while self.peek()[0] == "OR":
            op = self.consume()[0]
            right = self.parse_logic_and()
            expr = BinaryOp(expr, op, right)
        return expr

    def parse_logic_and(self):
        expr = self.parse_equality()
        while self.peek()[0] == "AND":
            op = self.consume()[0]
            right = self.parse_equality()
            expr = BinaryOp(expr, op, right)
        return expr

    def parse_equality(self):
        expr = self.parse_comparison()
        while self.peek()[0] in ("EQ", "NE"):
            op = self.consume()[0]
            right = self.parse_comparison()
            expr = BinaryOp(expr, op, right)
        return expr

    def parse_comparison(self):
        expr = self.parse_term()
        while self.peek()[0] in ("GT", "LT", "GE", "LE"):
            op = self.consume()[0]
            right = self.parse_term()
            expr = BinaryOp(expr, op, right)
        return expr

    def parse_term(self):
        expr = self.parse_factor()
        while self.peek()[0] in ("PLUS", "MINUS"):
            op = self.consume()[0]
            right = self.parse_factor()
            expr = BinaryOp(expr, op, right)
        return expr

    def parse_factor(self):
        expr = self.parse_unary()
        while self.peek()[0] in ("MUL", "DIV", "MOD"):
            op = self.consume()[0]
            right = self.parse_unary()
            expr = BinaryOp(expr, op, right)
        return expr

    def parse_unary(self):
        if self.peek()[0] in ("NOT", "MINUS"):
            op = self.consume()[0]
            right = self.parse_unary()
            return UnaryOp(op, right)
        return self.parse_primary()

    def parse_primary(self):
        token = self.peek()
        if token[0] == "NUMBER":
            return Number(self.consume()[1])
        elif token[0] == "STRING":
            return String(self.consume()[1].strip('"'))
        elif token[0] == "TRUE":
            self.consume()
            return Boolean(True)
        elif token[0] == "FALSE":
            self.consume()
            return Boolean(False)
        elif token[0] == "IDENT":
            name = self.consume()[1]
            if self.peek()[0] == "LPAREN":
                self.consume("LPAREN")
                args = []
                if self.peek()[0] != "RPAREN":
                    args.append(self.parse_expression())
                    while self.match("COMMA"):
                        args.append(self.parse_expression())
                self.consume("RPAREN")
                return FunctionCall(name, args)
            return Var(name)
        elif token[0] == "INPUT":
            self.consume("INPUT")
            self.consume("LPAREN")
            self.consume("RPAREN")
            return InputStatement()
        elif token[0] == "LPAREN":
            self.consume("LPAREN")
            expr = self.parse_expression()
            self.consume("RPAREN")
            return expr
        else:
            raise ParserError(f"Expressão inesperada: {token}")
