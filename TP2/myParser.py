import ply.yacc as yacc

from myLexer import Lexer

INT = 0
FLOAT = 1
STRING = 2
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
        "Attrib : INTKW ID '=' Expression ';'"
        i = len(self.fp)
        if p[2] not in self.fp:
            self.fp[p[2]] = (i,INT)
        else:
            print(f"Error in line {p.lineno(2)}: variable {p[2]} was previously declared.")
            raise SyntaxError
        p[0] = f"{p[4]}storeg {i}\n"

    def p_Attrib_f(self, p):
        "Attrib : FLOATKW ID '=' ExpressionF ';'"
        i = len(self.fp)
        if p[2] not in self.fp:
            self.fp[p[2]] = (i,FLOAT)
        else:
            print(f"Error in line {p.lineno(2)}: variable {p[2]} was previously declared.")
            raise SyntaxError
        p[0] = f"{p[4]}storeg {i}\n"

    def p_Attrib_s(self, p):
        "Attrib : STRKW ID '=' String ';'"
        i = len(self.fp)
        if p[2] not in self.fp:
            self.fp[p[2]] = (i,STRING)
        else:
            print(f"Error in line {p.lineno(2)}: variable {p[2]} was previously declared.")
            raise SyntaxError
        p[0] = f"{p[4]}storeg {i}\n"

    def p_Attrib_Empty(self, p):
        "Attrib : INTKW ID ';'"
        i = len(self.fp)
        if p[2] not in self.fp:
            self.fp[p[2]] = (i,INT)
        else:
            print(f"Error in line {p.lineno(2)}: variable {p[2]} was previously declared.")
            raise SyntaxError
        p[0] = f"pushi 0\nstoreg {i}\n"

    def p_Attrib_Empty_f(self, p):
        "Attrib : FLOATKW ID ';'"
        i = len(self.fp)
        if p[2] not in self.fp:
            self.fp[p[2]] = (i,FLOAT)
        else:
            print(f"Error in line {p.lineno(2)}: variable {p[2]} was previously declared.")
            raise SyntaxError
        p[0] = f"pushf 0.0\nstoreg {i}\n"

    def p_Attrib_Error(self, p):
        """Attrib : INTKW VAR '=' Expression ';'
                  | FLOATKW VAR '=' ExpressionF ';'
                  | STRKW VAR '=' String ';'
                  | INTKW VARF '=' Expression ';'
                  | FLOATKW VARF '=' ExpressionF ';'
                  | STRKW VARF '=' String ';'
                  | INTKW VARS '=' Expression ';'
                  | FLOATKW VARS '=' ExpressionF ';'
                  | STRKW VARS '=' String ';'"""
        print(f"Error in line {p.lineno(2)}: variable {p[2]} was previously declared.")
        raise SyntaxError

    def p_Command_Redefine(self, p):
        "Command : Redefine ';'"
        p[0] = p[1]

    def p_Redefine(self, p):
        "Redefine : VAR '=' Expression"
        p[0] = f"{p[3]}storeg {self.fp[p[1]][0]}\n"

    def p_Redefine_pp(self, p):
        "Redefine : VAR PP"
        i = self.fp[p[1]][0]
        p[0] = f"pushg {i}\npushi 1\nadd\nstoreg {i}\n"

    def p_Redefine_pp_f(self, p):
        "Redefine : VARF PP"
        i = self.fp[p[1]][0]
        p[0] = f"pushg {i}\npushf 1\nfadd\nstoreg {i}\n"

    def p_Redefine_f(self, p):
        "Redefine : VARF '=' ExpressionF"
        p[0] = f"{p[3]}storeg {self.fp[p[1]][0]}\n"

    def p_Redefine_s(self, p):
        "Redefine : VARS '=' String"
        p[0] = f"{p[3]}storeg {self.fp[p[1]][0]}\n"

    def p_Redefine_cast(self, p):
        "Redefine : VARF '=' Expression"
        p[0] = f"{p[3]}itof\nstoreg {self.fp[p[1]][0]}\n"

    def p_Redefine_cast_2(self, p):
        "Redefine : VAR '=' ExpressionF"
        print(f"Warning in line {p.lineno(2)}: implicit casting of floating point value to integer.")
        p[0] = f"{p[3]}ftoi\nstoreg {self.fp[p[1]][0]}\n"

    def p_Command_PRINT(self, p):
        """Command : PRINT '(' Expression ')' ';'
                   | PRINT '(' Logical ')' ';'"""
        p[0] = p[3] + "writei\n"

    def p_Command_PRINT_f(self, p):
        "Command : PRINT '(' ExpressionF ')' ';'"
        p[0] = p[3] + "writef\n"

    def p_Command_PRINT_s(self, p):
        "Command : PRINT '(' String ')' ';'"
        p[0] = p[3] + "writes\n"

    def p_Command_PRINTLN(self, p):
        """Command : PRINTLN '(' Expression ')' ';'
                   | PRINTLN '(' Logical ')' ';'"""
        p[0] = p[3] + "writei\n" + "pushs \"\\n\"\n" + "writes\n"

    def p_Command_PRINTLN_f(self, p):
        "Command : PRINTLN '(' ExpressionF ')' ';'"
        p[0] = p[3] + "writef\n" + "pushs \"\\n\"\n" + "writes\n"

    def p_Command_PRINTLN_s(self, p):
        "Command : PRINTLN '(' String ')' ';'"
        p[0] = p[3] + "writes\n" + "pushs \"\\n\"\n" + "writes\n"

    def p_Command_if(self, p):
        "Command : IF Boolean '{' Commands '}'"
        p[0] = p[2] + f"jz l{self.labels_if}\n" + p[4] + f"l{self.labels_if}:\n" 
        self.labels_if += 1
    
    def p_Command_if_else(self, p):
        "Command : IF Boolean '{' Commands '}' Else"
        p[0] = p[2] + f"jz l{self.labels_if}\n" + p[4] + f"jump le{self.labels_if_else}\n" + f"l{self.labels_if}:\n" + p[6]
        self.labels_if += 1
        self.labels_if_else += 1

    def p_Else(self, p):
        "Else : ELSE '{' Commands '}'"
        p[0] = p[3] + f"le{self.labels_if_else}:\n"

    def p_Else_if(self, p):
        "Else : ELSE IF Boolean '{' Commands '}'"
        p[0] = p[4] + f"jz l{self.labels_if}\n" + p[5] + f"l{self.labels_if}:\n" + f"le{self.labels_if_else}:\n"
        self.labels_if += 1

    def p_Else_if_else(self, p):
        "Else : ELSE IF Boolean '{' Commands '}' Else"
        p[0] = p[3] + f"jz l{self.labels_if}\n" + p[5] + f"jump le{self.labels_if_else}\n" + f"l{self.labels_if}:\n" + p[7]
        self.labels_if += 1

    def p_Command_for(self, p):
        """Command : FOR '(' Redefine ';' Boolean ';' Redefine ')' '{' Commands '}'
                   | FOR '(' Empty ';' Boolean ';' Redefine ')' '{' Commands '}'"""
        p[0] = (p[3] if p[3] else "") + f"lc{self.labels_cycle}:\n" + p[5] + f"jz lb{self.labels_cycle_exit}\n" + p[10] + p[7] + f"jump lc{self.labels_cycle}\n" + f"lb{self.labels_cycle_exit}:\n"
        self.labels_cycle += 1
        self.labels_cycle_exit += 1

    def p_Command_while(self, p):
        "Command : WHILE Boolean '{' Commands '}'"
        p[0] = f"lc{self.labels_cycle}:\n" + p[2] + f"jz lb{self.labels_cycle_exit}\n" + p[4] + f"jump lc{self.labels_cycle}\n" + f"lb{self.labels_cycle_exit}:\n"
        self.labels_cycle += 1
        self.labels_cycle_exit += 1

    precedence = (
        ('left','OR'),
        ('left','AND'),
        ('left','NOT'),
        ('left','<','>','GE','LE','EQ','NE'),
        ('left','+','-'),
        ('left','*','/','%'),
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

    def p_Expression_mod(self, p):
        "Expression : Expression '%' Expression"
        p[0] =  p[1] + p[3] + "mod\n"

    def p_ExpressionF_ops1(self, p):
        """ExpressionF : ExpressionF '+' ExpressionF
                       | ExpressionF '-' ExpressionF
                       | ExpressionF '*' ExpressionF
                       | ExpressionF '/' ExpressionF"""
        p[0] =  p[1] + p[3]
        if p[2] == '+': p[0] += "fadd\n"
        elif p[2] == '-': p[0] += "fsub\n"
        elif p[2] == '*': p[0] += "fmul\n"
        elif p[2] == '/': p[0] += "fdiv\n"

    def p_ExpressionF_ops2(self, p):
        """ExpressionF : Expression '+' ExpressionF
                       | Expression '-' ExpressionF
                       | Expression '*' ExpressionF
                       | Expression '/' ExpressionF"""
        p[0] =  p[1] + "itof\n" + p[3]
        if p[2] == '+': p[0] += "fadd\n"
        elif p[2] == '-': p[0] += "fsub\n"
        elif p[2] == '*': p[0] += "fmul\n"
        elif p[2] == '/': p[0] += "fdiv\n"

    def p_ExpressionF_ops3(self, p):
        """ExpressionF : ExpressionF '+' Expression
                       | ExpressionF '-' Expression
                       | ExpressionF '*' Expression
                       | ExpressionF '/' Expression"""
        p[0] =  p[1] + p[3] + "itof\n"
        if p[2] == '+': p[0] += "fadd\n"
        elif p[2] == '-': p[0] += "fsub\n"
        elif p[2] == '*': p[0] += "fmul\n"
        elif p[2] == '/': p[0] += "fdiv\n"

    # def p_Expression_pow(self, p):
    #     "Expression : Expression POW Expression"
    #     p[0] = p[1] ** p[3]

    def p_Expression_uplus(self, p):
        """Expression : '+' Expression
           ExpressionF : '+' ExpressionF"""
        p[0] = p[2]

    def p_Expression_uminus(self, p):
        "Expression : '-' Expression %prec UMINUS"
        p[0] = p[2] + "dup 1\ndup 1\nsub\nswap\nsub\n"

    def p_Expression_uminus_f(self, p):
        "ExpressionF : '-' ExpressionF %prec UMINUS"
        p[0] = p[2] + "dup 1\ndup 1\nfsub\nswap\nfsub\n"

    def p_Expression_paren(self, p):
        """Expression : '(' Expression ')'
           ExpressionF : '(' ExpressionF ')'"""
        p[0] = p[2]

    def p_Expression_Value(self, p):
        "Expression : Value"
        p[0] = p[1]

    def p_ExpressionF_ValueF(self, p):
        "ExpressionF : ValueF"
        p[0] = p[1]

    def p_ValueF_FLOAT(self, p):
        "ValueF : FLOAT"
        p[0] = f"pushf {p[1]}\n"

    def p_ValueF_IDF(self, p):
        "ValueF : VARF"
        p[0] = f"pushg {self.fp[p[1]][0]}\n"

    def p_ValueF_str(self, p):
        "ValueF : FLOATKW '(' String ')'"
        p[0] = f"{p[3]}atof\n"

    def p_ValueF_int(self, p):
        "ValueF : FLOATKW '(' Expression ')'"
        p[0] = f"{p[3]}itof\n"

    def p_Value_ID(self, p):
        "Value : VAR"
        p[0] = f"pushg {self.fp[p[1]][0]}\n"

    def p_Value_INT(self, p):
        "Value : INT"
        p[0] = f"pushi {p[1]}\n"

    def p_Value_str(self, p):
        "Value : INTKW '(' String ')'"
        p[0] = f"{p[3]}atoi\n"

    def p_Value_float(self, p):
        "Value : INTKW '(' ExpressionF ')'"
        p[0] = f"{p[3]}ftoi\n"

    def p_Logical_Comparisons(self, p):
        """Logical : Expression '>' Expression
                   | Expression '<' Expression
                   | Expression GE Expression
                   | Expression LE Expression
                   | Expression EQ Expression
                   | Expression NE Expression"""
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

    def p_Logical_Comparisons_f(self, p):
        """Logical : ExpressionF '>' ExpressionF
                   | ExpressionF '<' ExpressionF
                   | ExpressionF GE ExpressionF
                   | ExpressionF LE ExpressionF
                   | ExpressionF EQ ExpressionF
                   | ExpressionF NE ExpressionF"""
        if p[2] == '>':
            p[0] = p[1] + p[3] + "fsup\nftoi\n"
        elif p[2] == '<':
            p[0] = p[1] + p[3] + "finf\nftoi\n"
        elif p[2] == '>=':
            p[0] = p[1] + p[3] + "fsupeq\nftoi\n"
        elif p[2] == '<=':
            p[0] = p[1] + p[3] + "finfeq\nftoi\n"
        elif p[2] == '==':
            p[0] = p[1] + p[3] + "equal\n"
        elif p[2] == '!=':
            p[0] = p[1] + p[3] + "equal\nnot\n"

    def p_Logical_Comparisons_f2(self, p):
        """Logical : ExpressionF '>' Expression
                   | ExpressionF '<' Expression
                   | ExpressionF GE Expression
                   | ExpressionF LE Expression
                   | ExpressionF EQ Expression
                   | ExpressionF NE Expression"""
        p[0] = p[1] + p[3] + "itof\n"
        if p[2] == '>':
            p[0] += "fsup\nftoi\n"
        elif p[2] == '<':
            p[0] += "finf\nftoi\n"
        elif p[2] == '>=':
            p[0] += "fsupeq\nftoi\n"
        elif p[2] == '<=':
            p[0] += "finfeq\nftoi\n"
        elif p[2] == '==':
            p[0] += p[1] + p[3] + "equal\n"
        elif p[2] == '!=':
            p[0] += "equal\nnot\n"

    def p_Logical_Comparisons_f3(self, p):
        """Logical : Expression '>' ExpressionF
                   | Expression '<' ExpressionF
                   | Expression GE ExpressionF
                   | Expression LE ExpressionF
                   | Expression EQ ExpressionF
                   | Expression NE ExpressionF"""
        p[0] = p[1] + "itof\n" + p[3]
        if p[2] == '>':
            p[0] += "fsup\nftoi\n"
        elif p[2] == '<':
            p[0] += "finf\nftoi\n"
        elif p[2] == '>=':
            p[0] += "fsupeq\nftoi\n"
        elif p[2] == '<=':
            p[0] += "finfeq\nftoi\n"
        elif p[2] == '==':
            p[0] += p[1] + p[3] + "equal\n"
        elif p[2] == '!=':
            p[0] += "equal\nnot\n"


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

    def p_Boolean(self, p):
        """Boolean : Expression
                   | Logical"""
        p[0] = p[1]

    def p_String(self, p):
        "String : TEXT"
        p[0] = "pushs "+ p[1].replace("'",'"') + "\n"

    def p_String_var(self, p):
        "String : VARS"
        p[0] = f"pushg {self.fp[p[1]][0]}\n"

    def p_String_input(self, p):
        "String : INPUT '(' String ')'"
        p[0] = f"{p[3]}writes\nread\n"

    def p_Empty(self, p):
        "Empty : "
        pass

    # def p_error(self, p):
    #     print("Syntax error in input!")


    def build(self, **kwargs):
        self.fp = dict()
        self.lexer = Lexer(self.fp)
        self.lexer.build()
        self.parser = yacc.yacc(module=self, **kwargs)
        self.labels_if = 0
        self.labels_if_else = 0
        self.labels_cycle = 0
        self.labels_cycle_exit = 0