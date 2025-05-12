%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void yyerror(const char *s);
extern int yylex();

typedef struct Node {
    char* type;
    char* value;
    struct Node** children;
    int child_count;
} Node;

Node* create_node(const char* type, const char* value, Node** children, int child_count) {
    Node* node = (Node*)malloc(sizeof(Node));
    node->type = strdup(type);
    node->value = value ? strdup(value) : NULL;
    node->children = children;
    node->child_count = child_count;
    return node;
}

void free_node(Node* node) {
    if (!node) return;
    for (int i = 0; i < node->child_count; i++) {
        free_node(node->children[i]);
    }
    free(node->type);
    if (node->value) free(node->value);
    free(node->children);
    free(node);
}
%}

%union {
    int num;
    char* str;
    struct Node* node;
}

%token SEED BRANCH GROW WHILE THEN ELSE PRINT IN FROM TO
%token GT LT EQ LBRACKET RBRACKET COMMA LBRACE RBRACE NEWLINE
%token <num> NUMBER
%token <str> STRING IDENTIFIER

%type <node> program statement declaration conditional loop print block
%type <node> condition expression value list list_elements list_element

%start program

%%

program:
    /* vazio */         { $$ = create_node("program", NULL, NULL, 0); }
    | program statement { $$ = create_node("program", NULL, (Node*[]){$1, $2}, 2); }
    ;

statement:
    declaration NEWLINE     { $$ = $1; }
    | conditional NEWLINE   { $$ = $1; }
    | loop NEWLINE          { $$ = $1; }
    | print NEWLINE         { $$ = $1; }
    ;

declaration:
    SEED IDENTIFIER EQ value    { $$ = create_node("declaration", NULL, (Node*[]){create_node("identifier", $2, NULL, 0), $4}, 2); }
    ;

conditional:
    BRANCH condition THEN block             { $$ = create_node("conditional", NULL, (Node*[]){$2, $4}, 2); }
    | BRANCH condition THEN block ELSE block { $$ = create_node("conditional", NULL, (Node*[]){$2, $4, $6}, 3); }
    ;

loop:
    GROW IDENTIFIER FROM NUMBER TO NUMBER block {
        char buf1[32], buf2[32];
        snprintf(buf1, sizeof(buf1), "%d", $4);
        snprintf(buf2, sizeof(buf2), "%d", $6);
        $$ = create_node("loop", "from_to", (Node*[]){
            create_node("identifier", $2, NULL, 0),
            create_node("number", buf1, NULL, 0),
            create_node("number", buf2, NULL, 0),
            $7
        }, 4);
    }
    | GROW WHILE condition block            { $$ = create_node("loop", "while", (Node*[]){$3, $4}, 2); }
    | GROW IDENTIFIER IN IDENTIFIER block   { $$ = create_node("loop", "in", (Node*[]){create_node("identifier", $2, NULL, 0), create_node("identifier", $4, NULL, 0), $5}, 3); }
    ;

print:
    PRINT STRING        { $$ = create_node("print", NULL, (Node*[]){create_node("string", $2, NULL, 0)}, 1); }
    | PRINT IDENTIFIER  { $$ = create_node("print", NULL, (Node*[]){create_node("identifier", $2, NULL, 0)}, 1); }
    ;

block:
    LBRACE NEWLINE RBRACE NEWLINE                   { $$ = create_node("block", NULL, NULL, 0); }
    | LBRACE NEWLINE statement RBRACE NEWLINE       { $$ = create_node("block", NULL, (Node*[]){$3}, 1); }
    | LBRACE NEWLINE block statement RBRACE NEWLINE { $$ = create_node("block", NULL, (Node*[]){$3, $4}, 2); }
    ;

condition:
    expression GT expression    { $$ = create_node("condition", ">", (Node*[]){$1, $3}, 2); }
    | expression LT expression  { $$ = create_node("condition", "<", (Node*[]){$1, $3}, 2); }
    | expression EQ expression  { $$ = create_node("condition", "=", (Node*[]){$1, $3}, 2); }
    ;

expression:
    NUMBER      { char buf[32]; snprintf(buf, sizeof(buf), "%d", $1); $$ = create_node("number", buf, NULL, 0); }
    | IDENTIFIER    { $$ = create_node("identifier", $1, NULL, 0); }
    | STRING        { $$ = create_node("string", $1, NULL, 0); }
    ;

value:
    expression  { $$ = $1; }
    | list      { $$ = $1; }
    ;

list:
    LBRACKET list_elements RBRACKET     { $$ = create_node("list", NULL, $2->children, $2->child_count); }
    | LBRACKET RBRACKET                 { $$ = create_node("list", NULL, NULL, 0); }
    ;

list_elements:
    list_element                        { $$ = create_node("list_elements", NULL, (Node*[]){$1}, 1); }
    | list_elements COMMA list_element  { $$ = create_node("list_elements", NULL, (Node*[]){$1, $3}, 2); }
    ;

list_element:
    NUMBER      { char buf[32]; snprintf(buf, sizeof(buf), "%d", $1); $$ = create_node("number", buf, NULL, 0); }
    | IDENTIFIER    { $$ = create_node("identifier", $1, NULL, 0); }
    | STRING        { $$ = create_node("string", $1, NULL, 0); }
    | list          { $$ = $1; }
    ;

%%

void yyerror(const char *s) {
    fprintf(stderr, "Erro sintático: %s\n", s);
}

int main() {
    yyparse();
    return 0;
}