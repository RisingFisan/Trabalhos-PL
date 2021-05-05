import ply.lex as lex

class Lexer:

    reserved = {
        # 'int': 'DEFINT',
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
        'ID',
        'POW',
        'GE',
        'LE',
        'EQ',
        'NE',
        'TEXT'
    ] + list(reserved.values())

    literals = ['=','+','-','*','/','(',')','<','>',',',';','%','{','}']

    def t_INT(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    # def t_FLOAT(self, t):
    #     r'(\d*\.)?\d+(e(?:\+|-)\d+)?'
    #     t.value = float(t.value)
    #     return t

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
        return t

    t_TEXT = r"'(\\'|[^'])*'|\"(\\\"|[^\"])*\""

    t_ignore = ' \t'

    def t_newline(self, t):
        r'\n'
        t.lexer.lineno += 1

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)