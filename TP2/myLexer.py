import ply.lex as lex

INT = 0
FLOAT = 1
STRING = 2

class Lexer:

    def __init__(self, fp : list):
        self.fp = fp

    reserved = {
        'int': 'INTKW',
        'float': 'FLOATKW',
        'print': "PRINT",
        'or': 'OR',
        'and': 'AND',
        'not': 'NOT',
        'if': 'IF',
        'else': 'ELSE',
        'input': 'INPUT'
    }

    tokens = [
        'INT',
        'FLOAT',
        'ID',
        'VAR',
        'VARF',
        'VARS',
        'POW',
        'GE',
        'LE',
        'EQ',
        'NE',
        'TEXT'
    ] + list(reserved.values())

    literals = ['=','+','-','*','/','(',')','<','>',',',';','%','{','}']

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
        
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_\']*'
        t.type = Lexer.reserved.get(t.value,"ID")
        for var,vartype in self.fp:
            if var == t.value:
                if vartype == INT: t.type = "VAR"
                elif vartype == FLOAT: t.type = "VARF"
                elif vartype == STRING: t.type = "VARS"
                break
        return t

    t_TEXT = r"'(\\'|[^'])*'|\"(\\\"|[^\"])*\""

    t_ignore = ' \t'

    def t_newline(self, t):
        r'\n'
        t.lexer.lineno += 1

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)