%{
#include "parser.tab.h"
#include <string.h>

#define YYSTYPE union YYSTYPE
%}

%option noyywrap

%%

"seed"          { return SEED; }
"branch"        { return BRANCH; }
"grow"          { return GROW; }
"while"         { return WHILE; }
"then"          { return THEN; }
"else"          { return ELSE; }
"print"         { return PRINT; }
"in"            { return IN; }
"from"          { return FROM; }
"to"            { return TO; }
">"             { return GT; }
"<"             { return LT; }
"="             { return EQ; }
"["             { return LBRACKET; }
"]"             { return RBRACKET; }
","             { return COMMA; }
"{"             { return LBRACE; }
"}"             { return RBRACE; }
[0-9]+          { yylval.num = atoi(yytext); return NUMBER; }
\"[a-zA-Z0-9 ]*\" { yylval.str = strdup(yytext); return STRING; }
[a-zA-Z][a-zA-Z0-9]* { yylval.str = strdup(yytext); return IDENTIFIER; }
"\n"            { return NEWLINE; }
[ \t]+          { /* Ignora espaços e tabs */ }
.               { printf("Erro léxico: caractere desconhecido '%s'\n", yytext); }

%%