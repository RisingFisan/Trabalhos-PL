import ply.lex as lex

INT = 0
FLOAT = 1
STRING = 2
ARRAY = 3

class Lexer:

    def __init__(self, fp : dict):
        self.fp = fp

    reserved = {
        'int': 'INTKW',
        'float': 'FLOATKW',
        'str': 'STRKW',
        'print': "PRINT",
        'println': "PRINTLN",
        'or': 'OR',
        'and': 'AND',
        'not': 'NOT',
        'if': 'IF',
        'else': 'ELSE',
        'input': 'INPUT',
        'for': 'FOR',
        'while': 'WHILE'
    }

    tokens = [
        'INT',
        'FLOAT',
        'ID',
        'VAR',
        'VARF',
        'VARS',
        'VARA',
        'POW',
        'GE',
        'LE',
        'EQ',
        'NE',
        'TEXT',
        'PP',
        'MM'
    ] + list(reserved.values())

    literals = ['=','+','-','*','/','(',')','<','>',',',';','%','{','}','[',']']

    def t_FLOAT(self, t):
        r'(\d*)?\.\d+(e(?:\+|-)\d+)?'
        t.value = float(t.value)
        return t

    def t_INT(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    t_POW = r'\*\*|\^'
    t_GE = r'>='
    t_LE = r'<='
    t_EQ = r'=='
    t_NE = r'!='
    t_AND = r'&&'
    t_OR = r'\|\|'
    t_NOT = r'!'
    t_PP = r'\+\+'
    t_MM = r'\-\-'
        
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_\']*'
        t.type = Lexer.reserved.get(t.value,"ID")
        v = self.fp.get(t.value, None)
        if v is not None:
            vartype = v[1]
            if vartype == INT: t.type = "VAR"
            elif vartype == FLOAT: t.type = "VARF"
            elif vartype == STRING: t.type = "VARS"
            elif vartype == ARRAY: t.type = "VARA"
        return t

    t_TEXT = r"'(\\'|[^'])*'|\"(\\\"|[^\"])*\""

    t_ignore = ' \t'

    def t_newline(self, t):
        r'\n'
        t.lexer.lineno += 1

    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}'")
        t.lexer.skip(1)

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)