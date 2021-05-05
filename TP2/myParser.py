import ply.yacc as yacc

from myLexer import Lexer

class Parser:

    tokens = Lexer.tokens

    def p_Program(self, p):
        "Program : Attribs Commands"
        p[0] = (f"pushn {len(self.fp)}\n" if len(self.fp) > 0 else "") + "start\n" + p[1] + p[2] + "stop\n"

    def p_Program_noAttribs(self, p):
        "Program : Commands"
        p[0] = "start\n" + p[1] + "stop\n"

    def p_Program_noCommands(self, p):
        "Program : Attribs"
        print("Error: no instructions found.")
        raise SyntaxError

    def p_Attribs(self, p):
        "Attribs : Attribs Attrib"
        p[0] = p[1] + p[2]

    def p_Attribs_single(self, p):
        "Attribs : Attrib"
        p[0] = p[1]

    def p_Commands(self, p):
        "Commands : Commands Command"
        p[0] = p[1] + p[2]

    def p_Commands_single(self, p):
        "Commands : Command"
        p[0] = p[1]

    def p_Attrib(self, p):
        "Attrib : ID '=' Expression ';'"
        if p[1] not in self.fp:
            self.fp.append(p[1])
        else:
            print(f"Error in line {p.lineno(2)}: variable {p[1]} was previously declared.")
            raise SyntaxError
        p[0] = f"{p[3]}storeg {self.fp.index(p[1])}\n"

    def p_Attrib_stdin(self, p):
        "Attrib : ID '=' INPUT '(' TEXT ')' ';'"
        if p[1] not in self.fp:
            self.fp.append(p[1])
        else:
            print(f"Error in line {p.lineno(2)}: variable {p[1]} was previously declared.")
            raise SyntaxError
        p[0] = f"pushs {p[5]}\nwrites\nread\natoi\nstoreg {self.fp.index(p[1])}\n"

    def p_Attrib_Empty(self, p):
        "Attrib : ID ';'"
        if p[1] not in self.fp:
            self.fp.append(p[1])
        else:
            print(f"Error in line {p.lineno(2)}: variable {p[1]} was previously declared.")
            raise SyntaxError
        p[0] = f"pushi 0\nstoreg {self.fp.index(p[1])}\n"

    def p_Command_PRINT(self, p):
        """Command : PRINT '(' Expression ')' ';'
                   | PRINT '(' Logical ')' ';'"""
        p[0] = p[3] + "writei\n" + "pushs \"\\n\"\n" + "writes\n"

    def p_Command_if(self, p):
        "Command : IF Logical '{' Commands '}'"
        p[0] = p[2] + f"jz l{self.labels_if}\n" + p[4] + f"l{self.labels_if}:\n" 
        self.labels_if += 1
    
    def p_Command_if_else(self, p):
        "Command : IF Logical '{' Commands '}' Else"
        p[0] = p[2] + f"jz l{self.labels_if}\n" + p[4] + f"jump le{self.labels_if_else}\n" + f"l{self.labels_if}:\n" + p[6]
        self.labels_if += 1
        self.labels_if_else += 1

    def p_Else(self, p):
        "Else : ELSE '{' Commands '}'"
        p[0] = p[3] + f"le{self.labels_if_else}:\n"

    def p_Else_if(self, p):
        "Else : ELSE IF Logical '{' Commands '}'"
        p[0] = p[4] + f"jz l{self.labels_if}\n" + p[5] + f"l{self.labels_if}:\n" + f"le{self.labels_if_else}:\n"
        self.labels_if += 1

    def p_Else_if_else(self, p):
        "Else : ELSE IF Logical '{' Commands '}' Else"
        p[0] = p[3] + f"jz l{self.labels_if}\n" + p[5] + f"jump le{self.labels_if_else}\n" + f"l{self.labels_if}:\n" + p[7]
        self.labels_if += 1

    precedence = (
        ('left','OR'),
        ('left','AND'),
        ('left','NOT'),
        ('left','<','>','GE','LE','EQ','NE'),
        ('left','+','-'),
        ('left','*','/'),
        ('right','UMINUS'),
        ('left','POW')
    )

    def p_Expression_plus(self, p):
        "Expression : Expression '+' Expression"
        p[0] =  p[1] + p[3] + "add\n"

    def p_Expression_minus(self, p):
        "Expression : Expression '-' Expression"
        p[0] =  p[1] + p[3] + "sub\n"

    def p_Expression_multiply(self, p):
        "Expression : Expression '*' Expression"
        p[0] =  p[1] + p[3] + "mul\n"

    def p_Expression_divide(self, p):
        "Expression : Expression '/' Expression"
        p[0] =  p[1] + p[3] + "div\n"

    # def p_Expression_pow(self, p):
    #     "Expression : Expression POW Expression"
    #     p[0] = p[1] ** p[3]

    def p_Expression_uplus(self, p):
        "Expression : '+' Expression"
        p[0] = p[2]

    def p_Expression_uminus(self, p):
        "Expression : '-' Expression %prec UMINUS"
        p[0] = p[2] + "dup 1\ndup 1\nsub\nswap\nsub\n"

    def p_Expression_paren(self, p):
        "Expression : '(' Expression ')'"
        p[0] = p[2]

    def p_Expression_Value(self, p):
        "Expression : Value"
        p[0] = p[1]

    def p_Value_ID(self, p):
        "Value : ID"
        p[0] = f"pushg {self.fp.index(p[1])}\n"

    def p_Value_INT(self, p):
        "Value : INT"
        p[0] = f"pushi {p[1]}\n"

    def p_Logical_Comparisons(self, p):
        """Logical : Value '>' Value
                   | Value '<' Value
                   | Value GE Value
                   | Value LE Value
                   | Value EQ Value
                   | Value NE Value"""
        if p[2] == '>':
            p[0] = p[1] + p[3] + "sup\n"
        elif p[2] == '<':
            p[0] = p[1] + p[3] + "inf\n"
        elif p[2] == '>=':
            p[0] = p[1] + p[3] + "supeq\n"
        elif p[2] == '<=':
            p[0] = p[1] + p[3] + "infeq\n"
        elif p[2] == '==':
            p[0] = p[1] + p[3] + "equal\n"
        elif p[2] == '!=':
            p[0] = p[1] + p[3] + "equal\nnot\n"

    def p_Logical_Parens(self, p):
        "Logical : '(' Logical ')'"
        p[0] = p[2]

    def p_Logical_AND(self, p):
        "Logical : Logical AND Logical"
        p[0] = p[1] + p[3] + "mul\n"

    def p_Logical_OR(self, p):
        "Logical : Logical OR Logical"
        p[0] = p[1] + p[3] + "add\n"

    def p_Logical_NOT(self, p):
        "Logical : NOT Logical"
        p[0] = p[2] + "not\n"

    # def p_error(self, p):
    #     print("Syntax error in input!")


    def build(self, **kwargs):
        self.lexer = Lexer()
        self.lexer.build()
        self.parser = yacc.yacc(module=self, **kwargs)
        self.fp = list()
        self.labels_if = 0
        self.labels_if_else = 0