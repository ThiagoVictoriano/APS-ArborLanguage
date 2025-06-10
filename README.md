# ArborLang

Arbor é uma linguagem de programação inspirada em árvores, que gera uma Árvore Sintática Abstrata (AST) ao final da execução.

## Apresentação

A apresentação completa da linguagem pode ser encontrada:
- [Link para apresentação no Gamma.app](seu_link_aqui)
- [Apresentação em PDF](./apresentacao.pdf)
- [Apresentação em PowerPoint](./apresentacao.pptx)

## Gramática (EBNF)

```ebnf
program ::= { statement }

statement ::= ( declaration | assignment | conditional | loop | print | NEWLINE )

declaration ::= "seed" IDENTIFIER [ "=" value ] ( NEWLINE | EOF | PRINT | GROW | BRANCH | IDENTIFIER )

assignment ::= IDENTIFIER "=" value ( NEWLINE | EOF )

conditional ::= "branch" condition "then" block [ "else" block ]

loop ::= "grow" ( loop_while | loop_in )

loop_while ::= "while" condition block

loop_in ::= IDENTIFIER "in" ( IDENTIFIER | list ) block

print ::= "print" ( list | value ) ( NEWLINE | EOF )

block ::= "{" NEWLINE { statement } "}" ( NEWLINE | EOF | ELSE )

condition ::= expression ( ">" | "<" | "==" | "<=" | ">=" | "!=" ) expression

expression ::= term { ( "+" | "-" ) term }

term ::= factor { ( "*" | "/" ) factor }

factor ::= NUMBER
        | STRING
        | IDENTIFIER
        | "(" expression ")"
        | list

value ::= expression

list ::= "[" [ list_element { "," list_element } ] "]"

list_element ::= expression

IDENTIFIER ::= [a-zA-Z_][a-zA-Z0-9_]*
NUMBER ::= [0-9]+
STRING ::= "\"" [^"]* "\""
NEWLINE ::= "\n"
EOF ::= end of file
```