# ArborLang

Arbor é uma linguagem de programação inspirada em árvores, que gera uma Árvore Sintática Abstrata (AST) ao final da execução.

## Gramática (EBNF)

```ebnf
program = { statement } ;
statement = declaration | conditional | loop | print ;
declaration = "seed", identifier, "=", expression ;
conditional = "branch", condition, "then", block, [ "else", block ] ;
loop = "grow", identifier, "from", number, "to", number, block
     | "grow", "while", condition, block ;
print = "print", ( string | identifier ) ;
block = { statement } ;
condition = expression, ( ">" | "<" | "=" ), expression ;
expression = number | identifier | string ;
identifier = letter, { letter | digit } ;
number = digit, { digit } ;
string = '"', { letter | digit | space }, '"' ;
letter = "a" | "b" | "c" | ... | "z" ;
digit = "0" | "1" | "2" | ... | "9" ;
space = " " ;
```
