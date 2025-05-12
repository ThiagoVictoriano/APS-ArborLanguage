# ArborLang

Arbor é uma linguagem de programação inspirada em árvores, que gera uma Árvore Sintática Abstrata (AST) ao final da execução.

## Gramática (EBNF)

```ebnf
program = { statement } ;
statement = ( declaration | conditional | loop | print ) , newline ;
declaration = "seed" , identifier , "=" , ( expression | list ) ;
conditional = "branch" , condition , "then" , block , [ "else" , block ] ;
loop = "grow" , identifier , "from" , number , "to" , number , block
     | "grow" , "while" , condition , block
     | "grow" , identifier , "in" , identifier , block ;
print = "print" , ( string | identifier ) ;
block = "{" , newline , { statement } , "}" , newline ;
condition = expression , ( ">" | "<" | "=" ) , expression ;
expression = number | identifier | string | list ;
list = "[" , [ list_elements ] , "]" ;
list_elements = list_element , { "," , list_element } ;
list_element = expression | list ;
identifier = letter , { letter | digit } ;
number = digit , { digit } ;
string = "\"" , { letter | digit | space } , "\"" ;
letter = "a" | "b" | ... | "z" | "A" | "B" | ... | "Z" ;
digit = "0" | "1" | ... | "9" ;
space = " " ;
newline = "\n" ;
```
