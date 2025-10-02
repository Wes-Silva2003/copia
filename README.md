# Cirius: Uma Linguagem e seu Compilador 🚀

![Status do Projeto](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Linguagem](https://img.shields.io/badge/linguagem-Python-blue)

Projeto acadêmico desenvolvido para a disciplina de **Compiladores**. O objetivo foi projetar e implementar um compilador completo para uma nova linguagem de programação, a **Cirius**. O compilador é construído em Python e transpila o código Cirius para a linguagem C.

---

## 📖 Índice

- [Sobre o Nome](#-sobre-o-nome)
- [A Linguagem Cirius](#-a-linguagem-cirius)
- [Arquitetura do Compilador](#-arquitetura-do-compilador)
- [Funcionalidades Implementadas](#-funcionalidades-implementadas)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Como Executar o Compilador](#-como-executar-o-compilador)
  - [Pré-requisitos](#pré-requisitos)
  - [Instalação](#instalação)
  - [Uso](#uso)
- [Autores](#-autores)

---

## ✨ Sobre o Nome

**Cirius** é uma fusão de **C** e **Sirius**, a estrela mais brilhante do céu noturno. O nome reflete a filosofia do projeto: criar uma linguagem com a **clareza** e a **simplicidade** de uma estrela guia, homenageando a base sólida e poderosa da linguagem C, que serve como nosso código-alvo.

---

## 💻 A Linguagem Cirius

Cirius é uma linguagem de programação imperativa, de alto nível e com tipagem estática, projetada com fins didáticos. Sua sintaxe é inspirada em C e Python para ser intuitiva e poderosa.

#### Exemplo de Código em Cirius:
```c
// exemplo.cir

func main() {
    x = 10;
    y = 20;

    if (x < y and y > 15) {
        print("Y é maior");
    } else {
        print("X é maior ou igual");
    }

    // Laço for
    for i in 0..5 {
        print(i);
    }
}
```

---

## 🏗️ Arquitetura do Compilador

O compilador segue um pipeline clássico, dividido em front-end, middle-end e back-end, conforme descrito no documento de design.

1.  **Front-end**
    * **Analisador Léxico (`lexer.py`):** Converte o código-fonte em uma sequência de tokens usando expressões regulares.
    * **Analisador Sintático (`parser.py`):** Constrói uma Árvore Sintática Abstrata (AST) a partir dos tokens, validando a gramática da linguagem. A estrutura da AST é definida em `ast.py`.
    * **Analisador Semântico (`semantic.py`):** Percorre a AST para verificar regras de escopo, tipos e uso correto de variáveis e funções, utilizando uma Tabela de Símbolos para gerenciar os escopos.

2.  **Middle-end**
    * **Gerador de IR (`ir.py`):** Converte a AST validada em um Código Intermediário de Três Endereços (Three Address Code - TAC), que facilita as otimizações.
    * **Otimizador (`optimizer.py`):** Aplica otimizações no código intermediário, como propagação de constantes e eliminação de código morto, para melhorar a eficiência do código gerado.

3.  **Back-end**
    * **Gerador de Código (`codegen.py`):** Traduz (transpila) o código intermediário otimizado para a linguagem C, gerando um arquivo `.c` como saída.

O orquestrador `main.py` gerencia todo esse fluxo, oferecendo uma interface de linha de comando para compilar arquivos `.cir`.

---

## ⚙️ Funcionalidades Implementadas

-   **Análise Léxica e Sintática:** Suporte completo para a gramática da linguagem, incluindo palavras-chave, operadores e literais.
-   **Estruturas de Controle:** Condicionais (`if`/`else`), laços de repetição (`while`, `for`).
-   **Funções:** Definição e chamada de funções com parâmetros.
-   **Análise Semântica:** Validação de escopo, declaração de variáveis e aridade de funções.
-   **Geração de Código Intermediário:** Tradução da AST para um formato TAC.
-   **Otimizações:** Implementação de `Constant Propagation` e `Dead Code Elimination`.
-   **Geração de Código Alvo:** Transpilação do código intermediário para a linguagem C.

---

## 📁 Estrutura do Projeto

```
.
├── /src/                 # Código fonte do compilador
│   ├── lexer.py          # Analisador Léxico
│   ├── parser.py         # Analisador Sintático
│   ├── ast.py            # Definições da Árvore Sintática Abstrata
│   ├── semantic.py       # Analisador Semântico
│   ├── ir.py             # Gerador de Código Intermediário (IR)
│   ├── optimizer.py      # Módulo de otimização do IR
│   ├── codegen.py        # Gerador de Código em C
│   └── main.py           # Orquestrador do compilador (CLI)
├── /docs/                # Documentação do projeto
│   ├── design.md         # Documento de arquitetura
│   └── grammar.ebnf      # Gramática formal da linguagem
├── /tests/               # (Sugerido) Diretório para códigos de teste em Cirius
└── README.md             # Este arquivo
```

---

## 🛠️ Tecnologias Utilizadas

-   **Linguagem Principal:** [Python 3](https://www.python.org/)
-   **Bibliotecas:** Nenhuma dependência externa principal, o compilador foi construído com módulos padrão do Python.

---

## ▶️ Como Executar o Compilador

O script `main.py` é a porta de entrada para compilar arquivos `.cir`.

### Pré-requisitos

-   Python 3.8 ou superior
-   Um compilador C (como `gcc` ou `clang`) para compilar o código gerado (opcional).

### Instalação

1.  Clone o repositório:
    ```bash
    git clone [https://github.com/seu-usuario/ciriusMain.git](https://github.com/seu-usuario/ciriusMain.git)
    ```
2.  Navegue até o diretório do projeto:
    ```bash
    cd ciriusMain/
    ```

### Uso

Para compilar um arquivo `.cir`, execute o `main.py` a partir da raiz do projeto, passando o arquivo de entrada como argumento.

```bash
python -m src.main tests/exemplo.cir -o out/exemplo.c
```

**Argumentos da Linha de Comando:**

-   `<input>`: O arquivo `.cir` a ser compilado.
-   `-o, --output`: O caminho do arquivo `.c` de saída.
-   `--emit-ast`: Salva a AST em um arquivo JSON.
-   `--emit-ir`: Salva o Código Intermediário em um arquivo JSON.
-   `--compile`: Compila o arquivo `.c` gerado usando `gcc`.
-   `--run`: Executa o binário resultante após a compilação.
-   `--verbose`: Exibe informações detalhadas de cada fase do processo.

Exemplo completo (compilar, gerar o executável e rodar):
```bash
python -m src.main tests/exemplo.cir --compile --run --verbose
```

---

## 👥 Autores

| Nome      |
|-----------|
| Estela    | 
| Mateus    | 
| Welinton  | 
| Wesley    | 



