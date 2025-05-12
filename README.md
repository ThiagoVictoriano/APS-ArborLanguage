# ArborLang

Arbor é uma linguagem de programação inspirada em árvores, que gera uma Árvore Sintática Abstrata (AST) ao final da execução.

## Gramática (EBNF)

```ebnf
program = { statement } ;
statement = ( declaration | conditional | loop | print ) , newline ;
declaration = "seed" , identifier , "=" , value ;
conditional = "branch" , condition , "then" , block , [ "else" , block ] ;
loop = "grow" , identifier , "from" , number , "to" , number , block
| "grow" , "while" , condition , block
| "grow" , identifier , "in" , identifier , block ;
print = "print" , ( string | identifier ) ;
block = "{" , newline , { statement } , "}" , newline ;
condition = expression , ( ">" | "<" | "=" ) , expression ;
expression = number | identifier | string ;
value = expression | list ;
list = "[" , [ list_elements ] , "]" ;
list_elements = list_element , { "," , list_element } ;
list_element = number | identifier | string | list ;
identifier = letter , { letter | digit } ;
number = digit , { digit } ;
string = """ , { letter | digit | space } , """ ;
letter = "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j"
| "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t"
| "u" | "v" | "w" | "x" | "y" | "z"
| "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J"
| "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T"
| "U" | "V" | "W" | "X" | "Y" | "Z" ;
digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
space = " " ;
newline = "\n" ;
```
