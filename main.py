import sys
import re
from typing import Any, Tuple, List

# Pré-processador
class PrePro:
    @staticmethod
    def filter(code: str) -> str:
        filtered = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        filtered = re.sub(r'[\t]+', ' ', filtered).rstrip()
        return filtered

# Tabela de Símbolos
class SymbolTable:
    def __init__(self, parent: 'SymbolTable' = None):
        self.parent = parent
        self.table = {}

    def create(self, key: str, value: Any = None):
        if key in self.table:
            raise ValueError(f"Variável '{key}' já existe no escopo atual")
        self.table[key] = value

    def set(self, key: str, value: Any):
        current = self
        while current is not None:
            if key in current.table:
                current.table[key] = value
                return
            current = current.parent
        raise ValueError(f"Variável '{key}' não definida")

    def get(self, key: str) -> Any:
        current = self
        while current is not None:
            if key in current.table:
                return current.table[key]
            current = current.parent
        raise ValueError(f"Variável '{key}' não definida")

# Nós da AST
class Node:
    def __init__(self, value: Any, children: List['Node']):
        self.value = value
        self.children = children

    def evaluate(self, st: SymbolTable) -> Tuple[Any, str]:
        pass

    def to_string(self, indent: int = 0) -> str:
        indent_str = "  " * indent
        result = f"{indent_str}{self.__class__.__name__}({self.value})\n"
        for child in self.children:
            result += child.to_string(indent + 1)
        return result

class Declaration(Node):
    def __init__(self, children: List[Node]):
        if len(children) not in [1, 2]:
            raise ValueError("Declaração deve ter 1 ou 2 filhos")
        super().__init__("declaration", children)

    def to_string(self, indent: int = 0) -> str:
        indent_str = "  " * indent
        result = f"{indent_str}Declaration\n"
        for child in self.children:
            result += child.to_string(indent + 1)
        return result

    def evaluate(self, st: SymbolTable) -> Tuple[None, str]:
        identifier = self.children[0].value
        if len(self.children) == 2:
            value, _ = self.children[1].evaluate(st)
        else:
            value = None
        st.create(identifier, value)
        return (None, "none")

class Assignment(Node):
    def __init__(self, children: List[Node]):
        if len(children) != 2:
            raise ValueError("Atribuição deve ter exatamente 2 filhos")
        super().__init__("assignment", children)

    def to_string(self, indent: int = 0) -> str:
        indent_str = "  " * indent
        result = f"{indent_str}Assignment\n"
        for child in self.children:
            result += child.to_string(indent + 1)
        return result

    def evaluate(self, st: SymbolTable) -> Tuple[None, str]:
        identifier = self.children[0].value
        value, value_type = self.children[1].evaluate(st)
        st.get(identifier)
        st.set(identifier, value)
        return (None, "none")

class Conditional(Node):
    def __init__(self, children: List[Node]):
        if len(children) not in [2, 3]:
            raise ValueError("Condicional deve ter 2 ou 3 filhos")
        super().__init__("conditional", children)

    def to_string(self, indent: int = 0) -> str:
        indent_str = "  " * indent
        result = f"{indent_str}Conditional\n"
        result += f"{indent_str}  Condition:\n"
        result += self.children[0].to_string(indent + 2)
        result += f"{indent_str}  Then:\n"
        result += self.children[1].to_string(indent + 2)
        if len(self.children) == 3:
            result += f"{indent_str}  Else:\n"
            result += self.children[2].to_string(indent + 2)
        return result

    def evaluate(self, st: SymbolTable) -> Tuple[None, str]:
        condition_val, condition_type = self.children[0].evaluate(st)
        if condition_type != "bool":
            raise ValueError(f"Condição deve ser bool, obteve {condition_type}")
        if condition_val:
            return self.children[1].evaluate(st)
        elif len(self.children) == 3:
            return self.children[2].evaluate(st)
        return (None, "none")

class LoopWhile(Node):
    def __init__(self, children: List[Node]):
        if len(children) != 2:
            raise ValueError("LoopWhile deve ter exatamente 2 filhos")
        super().__init__("loop_while", children)

    def to_string(self, indent: int = 0) -> str:
        indent_str = "  " * indent
        result = f"{indent_str}WhileLoop\n"
        result += f"{indent_str}  Condition:\n"
        result += self.children[0].to_string(indent + 2)
        result += f"{indent_str}  Body:\n"
        result += self.children[1].to_string(indent + 2)
        return result

    def evaluate(self, st: SymbolTable) -> Tuple[None, str]:
        while True:
            condition_val, condition_type = self.children[0].evaluate(st)
            if condition_type != "bool":
                raise ValueError(f"Condição do while deve ser bool, obteve {condition_type}")
            if not condition_val:
                break
            loop_st = SymbolTable(parent=st)
            self.children[1].evaluate(loop_st)
        return (None, "none")

class LoopIn(Node):
    def __init__(self, identifier: str, list_identifier: str, block: Node):
        super().__init__("loop_in", [block])
        self.identifier = identifier
        self.list_identifier = list_identifier

    def to_string(self, indent: int = 0) -> str:
        indent_str = "  " * indent
        result = f"{indent_str}InLoop(var: {self.identifier}, list: {self.list_identifier})\n"
        result += f"{indent_str}  Body:\n"
        result += self.children[0].to_string(indent + 2)
        return result

    def evaluate(self, st: SymbolTable) -> Tuple[None, str]:
        list_val = st.get(self.list_identifier)
        if not isinstance(list_val, list):
            raise ValueError(f"Espera-se lista para loop 'in', obteve {type(list_val).__name__}")
        for item in list_val:
            loop_st = SymbolTable(parent=st)
            loop_st.create(self.identifier, item)
            self.children[0].evaluate(loop_st)
        return (None, "none")

class Print(Node):
    def __init__(self, children: List[Node]):
        if len(children) != 1:
            raise ValueError("Print deve ter exatamente 1 filho")
        super().__init__("print", children)

    def to_string(self, indent: int = 0) -> str:
        indent_str = "  " * indent
        result = f"{indent_str}Print\n"
        result += self.children[0].to_string(indent + 1)
        return result

    def evaluate(self, st: SymbolTable) -> Tuple[None, str]:
        value, value_type = self.children[0].evaluate(st)
        print(value)
        return (None, "none")

class Block(Node):
    def __init__(self, children: List[Node]):
        super().__init__("block", children)

    def to_string(self, indent: int = 0) -> str:
        indent_str = "  " * indent
        result = f"{indent_str}Block\n"
        for child in self.children:
            result += child.to_string(indent + 1)
        return result

    def evaluate(self, st: SymbolTable) -> Tuple[None, str]:
        for child in self.children:
            child.evaluate(st)
        return (None, "none")

class BinOp(Node):
    def __init__(self, value: str, children: List[Node]):
        if len(children) != 2:
            raise ValueError("BinOp deve ter exatamente 2 filhos")
        super().__init__(value, children)

    def to_string(self, indent: int = 0) -> str:
        indent_str = "  " * indent
        result = f"{indent_str}BinOp({self.value})\n"
        for child in self.children:
            result += child.to_string(indent + 1)
        return result

    def evaluate(self, st: SymbolTable) -> Tuple[Any, str]:
        left_val, left_type = self.children[0].evaluate(st)
        right_val, right_type = self.children[1].evaluate(st)

        # Verificação de tipos para operações aritméticas
        if self.value in ["+", "-", "*", "/"]:
            # Caso especial para concatenação de strings
            if self.value == "+" and left_type == "str" and right_type == "str":
                return (left_val + right_val, "str")
            
            # Operações aritméticas requerem inteiros
            if not (left_type == "int" and right_type == "int"):
                if self.value == "+":
                    raise ValueError(f"Operador '+' requer dois inteiros ou duas strings, obteve {left_type} e {right_type}")
                else:
                    raise ValueError(f"Operador '{self.value}' requer operandos int, obteve {left_type} e {right_type}")
            
            if self.value == "+":
                return (left_val + right_val, "int")
            elif self.value == "-":
                return (left_val - right_val, "int")
            elif self.value == "*":
                return (left_val * right_val, "int")
            elif self.value == "/":
                if right_val == 0:
                    raise ValueError("Divisão por zero")
                return (left_val // right_val, "int")

        # Operadores de comparação
        elif self.value in [">", "<", "==", "<=", ">=", "!="]:
            if left_type != right_type:
                raise ValueError(f"Operador '{self.value}' requer operandos do mesmo tipo, obteve {left_type} e {right_type}")
            if self.value == ">":
                return (left_val > right_val, "bool")
            elif self.value == "<":
                return (left_val < right_val, "bool")
            elif self.value == "==":
                return (left_val == right_val, "bool")
            elif self.value == "<=":
                return (left_val <= right_val, "bool")
            elif self.value == ">=":
                return (left_val >= right_val, "bool")
            elif self.value == "!=":
                return (left_val != right_val, "bool")

        raise ValueError(f"Operador binário desconhecido: {self.value}")

class IntVal(Node):
    def __init__(self, value: int):
        super().__init__(value, [])

    def to_string(self, indent: int = 0) -> str:
        indent_str = "  " * indent
        return f"{indent_str}IntVal({self.value})\n"

    def evaluate(self, st: SymbolTable) -> Tuple[int, str]:
        return (self.value, "int")

class StrVal(Node):
    def __init__(self, value: str):
        super().__init__(value, [])

    def to_string(self, indent: int = 0) -> str:
        indent_str = "  " * indent
        return f"{indent_str}StrVal({self.value})\n"

    def evaluate(self, st: SymbolTable) -> Tuple[str, str]:
        return (self.value, "str")

class ListVal(Node):
    def __init__(self, elements: List[Node]):
        super().__init__(elements, [])

    def to_string(self, indent: int = 0) -> str:
        indent_str = "  " * indent
        result = f"{indent_str}ListVal\n"
        for elem in self.value:
            result += elem.to_string(indent + 1)
        return result

    def evaluate(self, st: SymbolTable) -> Tuple[List[Any], str]:
        values = []
        for elem in self.value:
            val, _ = elem.evaluate(st)
            values.append(val)
        return (values, "list")

class Identifier(Node):
    def __init__(self, value: str):
        super().__init__(value, [])

    def to_string(self, indent: int = 0) -> str:
        indent_str = "  " * indent
        return f"{indent_str}Identifier({self.value})\n"

    def evaluate(self, st: SymbolTable) -> Tuple[Any, str]:
        value = st.get(self.value)
        if isinstance(value, int):
            return (value, "int")
        elif isinstance(value, str):
            return (value, "str")
        elif isinstance(value, list):
            return (value, "list")
        elif value is None:
            return (value, "none")
        return (value, "unknown")

# Tokenizer
class Token:
    def __init__(self, type: str, value: Any):
        self.type = type
        self.value = value

class Tokenizer:
    def __init__(self, source: str, position: int = 0):
        self.source = source
        self.position = position
        self.next: Token | None = None
        self.selectNext()

    def selectNext(self) -> None:
        while self.position < len(self.source) and self.source[self.position].isspace() and self.source[self.position] != '\n':
            self.position += 1

        if self.position >= len(self.source):
            self.next = Token("EOF", None)
            return

        token = self.source[self.position]
        if token.isdigit():
            result = ""
            while self.position < len(self.source) and self.source[self.position].isdigit():
                result += self.source[self.position]
                self.position += 1
            self.next = Token("NUMBER", int(result))
        elif token == '+':
            self.next = Token("PLUS", 0)
            self.position += 1
        elif token == '-':
            self.next = Token("MINUS", 0)
            self.position += 1
        elif token == '*':
            self.next = Token("MULT", 0)
            self.position += 1
        elif token == '/':
            self.next = Token("DIV", 0)
            self.position += 1
        elif token == '(':
            self.next = Token("LPAREN", 0)
            self.position += 1
        elif token == ')':
            self.next = Token("RPAREN", 0)
            self.position += 1
        elif token == '{':
            self.next = Token("LBRACE", 0)
            self.position += 1
        elif token == '}':
            self.next = Token("RBRACE", 0)
            self.position += 1
        elif token == '[':
            self.next = Token("LBRACKET", 0)
            self.position += 1
        elif token == ']':
            self.next = Token("RBRACKET", 0)
            self.position += 1
        elif token == ',':
            self.next = Token("COMMA", 0)
            self.position += 1
        elif token == '>':
            if self.position + 1 < len(self.source) and self.source[self.position + 1] == '=':
                self.next = Token("GE", 0)
                self.position += 2
            else:
                self.next = Token("GT", 0)
                self.position += 1
        elif token == '<':
            if self.position + 1 < len(self.source) and self.source[self.position + 1] == '=':
                self.next = Token("LE", 0)
                self.position += 2
            else:
                self.next = Token("LT", 0)
                self.position += 1
        elif token == '=':
            if self.position + 1 < len(self.source) and self.source[self.position + 1] == '=':
                self.next = Token("EQ", 0)
                self.position += 2
            else:
                self.next = Token("ASSIGN", 0)
                self.position += 1
        elif token == '!':
            if self.position + 1 < len(self.source) and self.source[self.position + 1] == '=':
                self.next = Token("NE", 0)
                self.position += 2
            else:
                raise ValueError(f"Token inválido: {token}")
        elif token == '"':
            self.position += 1
            result = ""
            while self.position < len(self.source) and self.source[self.position] != '"':
                result += self.source[self.position]
                self.position += 1
            if self.position >= len(self.source):
                raise ValueError("String literal não terminada")
            self.next = Token("STRING", result)
            self.position += 1
        elif token == '\n':
            self.next = Token("NEWLINE", 0)
            self.position += 1
        elif token.isalpha() or token == '_':
            result = ""
            while self.position < len(self.source) and (self.source[self.position].isalnum() or self.source[self.position] == '_'):
                result += self.source[self.position]
                self.position += 1
            if result == "seed":
                self.next = Token("SEED", 0)
            elif result == "branch":
                self.next = Token("BRANCH", 0)
            elif result == "then":
                self.next = Token("THEN", 0)
            elif result == "else":
                self.next = Token("ELSE", 0)
            elif result == "grow":
                self.next = Token("GROW", 0)
            elif result == "while":
                self.next = Token("WHILE", 0)
            elif result == "in":
                self.next = Token("IN", 0)
            elif result == "print":
                self.next = Token("PRINT", 0)
            else:
                self.next = Token("IDENTIFIER", result)
        else:
            raise ValueError(f"Token inválido: {token}")

# Parser
class Parser:
    def __init__(self):
        self.tokenizer: Tokenizer | None = None

    def parseFactor(self) -> Node:
        if self.tokenizer.next.type == "NUMBER":
            result = IntVal(self.tokenizer.next.value)
            self.tokenizer.selectNext()
        elif self.tokenizer.next.type == "STRING":
            result = StrVal(self.tokenizer.next.value)
            self.tokenizer.selectNext()
        elif self.tokenizer.next.type == "IDENTIFIER":
            result = Identifier(self.tokenizer.next.value)
            self.tokenizer.selectNext()
        elif self.tokenizer.next.type == "LPAREN":
            self.tokenizer.selectNext()
            result = self.parseExpression()
            if self.tokenizer.next.type != "RPAREN":
                raise ValueError(f"Espera-se RPAREN, obteve {self.tokenizer.next.type}")
            self.tokenizer.selectNext()
        elif self.tokenizer.next.type == "LBRACKET":
            result = self.parseList()
        else:
            raise ValueError(f"Espera-se NUMBER, STRING, IDENTIFIER, LBRACKET ou LPAREN, obteve {self.tokenizer.next.type}")
        return result

    def parseTerm(self) -> Node:
        result = self.parseFactor()
        while self.tokenizer.next.type in ["MULT", "DIV"]:
            op = "*" if self.tokenizer.next.type == "MULT" else "/"
            self.tokenizer.selectNext()
            right = self.parseFactor()
            result = BinOp(op, [result, right])
        return result

    def parseExpression(self) -> Node:
        result = self.parseTerm()
        while self.tokenizer.next.type in ["PLUS", "MINUS"]:
            op = "+" if self.tokenizer.next.type == "PLUS" else "-"
            self.tokenizer.selectNext()
            right = self.parseTerm()
            result = BinOp(op, [result, right])
        return result

    def parseCondition(self) -> Node:
        left = self.parseExpression()
        if self.tokenizer.next.type in ["GT", "LT", "EQ", "LE", "GE", "NE"]:
            op = ">" if self.tokenizer.next.type == "GT" else \
                 "<" if self.tokenizer.next.type == "LT" else \
                 "==" if self.tokenizer.next.type == "EQ" else \
                 "<=" if self.tokenizer.next.type == "LE" else \
                 ">=" if self.tokenizer.next.type == "GE" else "!="
            self.tokenizer.selectNext()
            right = self.parseExpression()
            return BinOp(op, [left, right])
        raise ValueError(f"Espera-se GT, LT, EQ, LE, GE ou NE, obteve {self.tokenizer.next.type}")

    def parseList(self) -> Node:
        if self.tokenizer.next.type != "LBRACKET":
            raise ValueError(f"Espera-se LBRACKET, obteve {self.tokenizer.next.type}")
        self.tokenizer.selectNext()
        elements = []
        if self.tokenizer.next.type != "RBRACKET":
            elements.append(self.parseListElement())
            while self.tokenizer.next.type == "COMMA":
                self.tokenizer.selectNext()
                elements.append(self.parseListElement())
        if self.tokenizer.next.type != "RBRACKET":
            raise ValueError(f"Espera-se RBRACKET, obteve {self.tokenizer.next.type}")
        self.tokenizer.selectNext()
        return ListVal(elements)

    def parseListElement(self) -> Node:
        if self.tokenizer.next.type in ["NUMBER", "STRING", "IDENTIFIER"]:
            if self.tokenizer.next.type == "NUMBER":
                result = IntVal(self.tokenizer.next.value)
                self.tokenizer.selectNext()
            elif self.tokenizer.next.type == "STRING":
                result = StrVal(self.tokenizer.next.value)
                self.tokenizer.selectNext()
            else:
                result = Identifier(self.tokenizer.next.value)
                self.tokenizer.selectNext()
            return result
        raise ValueError(f"Espera-se NUMBER, STRING ou IDENTIFIER, obteve {self.tokenizer.next.type}")

    def parseValue(self) -> Node:
        if self.tokenizer.next.type in ["NUMBER", "STRING", "IDENTIFIER", "LPAREN", "LBRACKET"]:
            return self.parseExpression()
        raise ValueError(f"Espera-se NUMBER, STRING, IDENTIFIER, LBRACKET ou LPAREN, obteve {self.tokenizer.next.type}")

    def parseAssignment(self) -> Node:
        if self.tokenizer.next.type != "IDENTIFIER":
            raise ValueError(f"Espera-se IDENTIFIER, obteve {self.tokenizer.next.type}")
        identifier = self.tokenizer.next.value
        self.tokenizer.selectNext()
        if self.tokenizer.next.type != "ASSIGN":
            raise ValueError(f"Espera-se ASSIGN, obteve {self.tokenizer.next.type}")
        self.tokenizer.selectNext()
        value = self.parseValue()
        return Assignment([Identifier(identifier), value])

    def parseDeclaration(self) -> Node:
        if self.tokenizer.next.type != "SEED":
            raise ValueError(f"Espera-se SEED, obteve {self.tokenizer.next.type}")
        self.tokenizer.selectNext()
        if self.tokenizer.next.type != "IDENTIFIER":
            raise ValueError(f"Espera-se IDENTIFIER, obteve {self.tokenizer.next.type}")
        identifier = self.tokenizer.next.value
        self.tokenizer.selectNext()
        if self.tokenizer.next.type == "ASSIGN":
            self.tokenizer.selectNext()
            value = self.parseValue()
            return Declaration([Identifier(identifier), value])
        return Declaration([Identifier(identifier)])

    def parseConditional(self) -> Node:
        if self.tokenizer.next.type != "BRANCH":
            raise ValueError(f"Espera-se BRANCH, obteve {self.tokenizer.next.type}")
        self.tokenizer.selectNext()
        condition = self.parseCondition()
        if self.tokenizer.next.type != "THEN":
            raise ValueError(f"Espera-se THEN, obteve {self.tokenizer.next.type}")
        self.tokenizer.selectNext()
        then_block = self.parseBlock()
        children = [condition, then_block]
        if self.tokenizer.next.type == "ELSE":
            self.tokenizer.selectNext()
            else_block = self.parseBlock()
            children.append(else_block)
        return Conditional(children)

    def parseLoop(self) -> Node:
        if self.tokenizer.next.type != "GROW":
            raise ValueError(f"Espera-se GROW, obteve {self.tokenizer.next.type}")
        self.tokenizer.selectNext()
        if self.tokenizer.next.type == "IDENTIFIER":
            identifier = self.tokenizer.next.value
            self.tokenizer.selectNext()
            if self.tokenizer.next.type == "IN":
                self.tokenizer.selectNext()
                if self.tokenizer.next.type == "IDENTIFIER":
                    list_identifier = self.tokenizer.next.value
                    self.tokenizer.selectNext()
                    block = self.parseBlock()
                    return LoopIn(identifier, list_identifier, block)
                elif self.tokenizer.next.type == "LBRACKET":
                    list_node = self.parseList()
                    block = self.parseBlock()
                    # Criar uma variável temporária para a lista
                    temp_var = f"_temp_list_{id(list_node)}"
                    return Block([
                        Declaration([Identifier(temp_var), list_node]),
                        LoopIn(identifier, temp_var, block)
                    ])
                else:
                    raise ValueError(f"Espera-se IDENTIFIER ou LBRACKET, obteve {self.tokenizer.next.type}")
            else:
                raise ValueError(f"Espera-se IN, obteve {self.tokenizer.next.type}")
        elif self.tokenizer.next.type == "WHILE":
            self.tokenizer.selectNext()
            condition = self.parseCondition()
            block = self.parseBlock()
            return LoopWhile([condition, block])
        else:
            raise ValueError(f"Espera-se IDENTIFIER ou WHILE, obteve {self.tokenizer.next.type}")

    def parsePrint(self) -> Node:
        if self.tokenizer.next.type != "PRINT":
            raise ValueError(f"Espera-se PRINT, obteve {self.tokenizer.next.type}")
        self.tokenizer.selectNext()
        if self.tokenizer.next.type in ["STRING", "NUMBER", "IDENTIFIER", "LPAREN", "LBRACKET"]:
            if self.tokenizer.next.type == "LBRACKET":
                expr = self.parseList()
            else:
                expr = self.parseValue()
            return Print([expr])
        raise ValueError(f"Espera-se STRING, NUMBER, IDENTIFIER, LPAREN ou LBRACKET, obteve {self.tokenizer.next.type}")

    def parseStatement(self) -> Node:
        if self.tokenizer.next.type == "NEWLINE":
            self.tokenizer.selectNext()
            return Node("noop", [])
        elif self.tokenizer.next.type == "SEED":
            result = self.parseDeclaration()
            if self.tokenizer.next.type in ["NEWLINE", "EOF", "PRINT", "GROW", "BRANCH", "IDENTIFIER"]:
                if self.tokenizer.next.type == "NEWLINE":
                    self.tokenizer.selectNext()
            else:
                raise ValueError(f"Espera-se NEWLINE, EOF, PRINT, GROW, BRANCH ou IDENTIFIER, obteve {self.tokenizer.next.type}")
        elif self.tokenizer.next.type == "IDENTIFIER":
            result = self.parseAssignment()
            if self.tokenizer.next.type in ["NEWLINE", "EOF"]:
                if self.tokenizer.next.type == "NEWLINE":
                    self.tokenizer.selectNext()
            else:
                raise ValueError(f"Espera-se NEWLINE ou EOF, obteve {self.tokenizer.next.type}")
        elif self.tokenizer.next.type == "BRANCH":
            result = self.parseConditional()
        elif self.tokenizer.next.type == "GROW":
            result = self.parseLoop()
        elif self.tokenizer.next.type == "PRINT":
            result = self.parsePrint()
            if self.tokenizer.next.type in ["NEWLINE", "EOF"]:
                if self.tokenizer.next.type == "NEWLINE":
                    self.tokenizer.selectNext()
            else:
                raise ValueError(f"Espera-se NEWLINE ou EOF, obteve {self.tokenizer.next.type}")
        else:
            raise ValueError(f"Espera-se SEED, IDENTIFIER, BRANCH, GROW, PRINT ou NEWLINE, obteve {self.tokenizer.next.type}")
        return result

    def parseBlock(self) -> Node:
        if self.tokenizer.next.type != "LBRACE":
            raise ValueError(f"Espera-se LBRACE, obteve {self.tokenizer.next.type}")
        self.tokenizer.selectNext()
        if self.tokenizer.next.type != "NEWLINE":
            raise ValueError(f"Espera-se NEWLINE, obteve {self.tokenizer.next.type}")
        self.tokenizer.selectNext()
        children = []
        while self.tokenizer.next.type != "RBRACE":
            children.append(self.parseStatement())
        self.tokenizer.selectNext()
        if self.tokenizer.next.type not in ["NEWLINE", "EOF", "ELSE"]:
            raise ValueError(f"Espera-se NEWLINE, EOF ou ELSE, obteve {self.tokenizer.next.type}")
        if self.tokenizer.next.type == "NEWLINE":
            self.tokenizer.selectNext()
        return Block(children)

    def parseProgram(self) -> Node:
        children = []
        while self.tokenizer.next.type != "EOF":
            if self.tokenizer.next.type == "NEWLINE":
                self.tokenizer.selectNext()
                continue
            children.append(self.parseStatement())
        return Block(children)

    def run(self, code: str) -> Node:
        self.tokenizer = Tokenizer(code)
        result = self.parseProgram()
        if self.tokenizer.next.type != "EOF":
            raise ValueError(f"Espera-se EOF, obteve {self.tokenizer.next.type}")
        return result

# Execução
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.arbor>")
        sys.exit(1)

    filename = sys.argv[1]
    if not filename.endswith('.arbor'):
        print("Erro: O arquivo deve ter extensão .arbor")
        sys.exit(1)

    try:
        with open(filename, 'r') as file:
            code = file.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{filename}' não encontrado")
        sys.exit(1)
    except IOError:
        print(f"Erro: Não foi possível ler o arquivo '{filename}'")
        sys.exit(1)

    code_filtered = PrePro.filter(code)
    parser = Parser()
    tree = parser.run(code_filtered)
    
    # Imprime a árvore antes de avaliar
    print("\nÁrvore Sintática Abstrata:")
    print("=" * 50)
    print(tree.to_string())
    print("=" * 50)
    print("\nResultado da execução:")
    print("-" * 50)
    
    st = SymbolTable()
    tree.evaluate(st)