import ply.yacc as yacc

from myLexer import Lexer

INT = 0
FLOAT = 1
STRING = 2
ARRAY = 3
class Parser:

    tokens = Lexer.tokens

    def p_Program(self, p):
        "Program : Attribs Commands"
        p[0] = p[1] + "start\n" + p[2] + "stop\n"

    def p_Program_noAttribs(self, p):
        "Program : Commands"
        p[0] = "start\n" + p[1] + "stop\n"

    def p_Program_noCommands(self, p):
        "Program : Attribs"
        print("Error: no instructions found.")
        raise SyntaxError

    def p_Program_error(self, p):
        "Program : error"
        print("Aborting...")
        exit(1)

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

    def p_Attrib_Array(self, p):
        "Attrib : INTKW ID '[' INT ']' ';'"
        if p[2] not in self.fp:
            self.fp[p[2]] = (self.stack_size,ARRAY,p[4])
            self.stack_size += p[4]
        else:
            print(f"Error in line {p.lineno(2)}: variable {p[2]} was previously declared.")
            raise SyntaxError
        p[0] = f"pushn {p[4]}\n"

    def p_Attrib_Array_2d(self, p):
        "Attrib : INTKW ID '[' INT ']' '[' INT ']' ';'"
        if p[2] not in self.fp:
            self.fp[p[2]] = (self.stack_size,ARRAY,(p[4],p[7]))
            self.stack_size += p[4] * p[7]
        else:
            print(f"Error in line {p.lineno(2)}: variable {p[2]} was previously declared.")
            raise SyntaxError
        p[0] = f"pushn {p[4]*p[7]}\n"

    def p_Array_2d(self, p):
        "Array2d : '[' Arrays ']'"
        p[0] = p[2]

    def p_Arrays(self, p):
        "Arrays : Arrays ',' Array "
        if len(p[3]) != len(p[1][0]):
            print(f"Error in line {p.lineno(2)}: two dimensional array must have rows of equal length.")
            raise SyntaxError
        p[0] = p[1]
        p[0].append(p[3])

    def p_Arrays_single(self, p):
        "Arrays : Array"
        p[0] = [p[1]]

    def p_Array(self, p):
        "Array : '[' Elems ']' "
        p[0] = p[2]

    def p_Elems(self, p):
        "Elems : Elems ',' INT"
        p[0] = p[1]
        p[0].append(p[3])

    def p_Elems_single(self, p):
        "Elems : INT"
        p[0] = [p[1]]

    def p_Attrib_Array_elems(self, p):
        "Attrib : INTKW ID '[' INT ']' '=' Array ';'"
        "Attrib : INTKW ID '[' Empty ']' '=' Array ';'"
        if not p[4]: p[4] = len(p[7])
        if p[2] not in self.fp:
            self.fp[p[2]] = (self.stack_size,ARRAY,p[4])
            self.stack_size += p[4]
        else:
            print(f"Error in line {p.lineno(2)}: variable {p[2]} was previously declared.")
            raise SyntaxError

        if len(p[7]) != p[4]:
            print(f"Error in line {p.lineno(2)}: number of array elements different from the defined value.")
            raise SyntaxError
        p[0] = ""
        for elem in p[7]:
            p[0] += f"pushi {elem}\n"

    def p_Attrib_Array_2d_elems(self, p):
        """Attrib : INTKW ID '[' INT ']' '[' INT ']' '=' Array2d ';'
                  | INTKW ID '[' INT ']' '[' Empty ']' '=' Array2d ';'
                  | INTKW ID '[' Empty ']' '[' INT ']' '=' Array2d ';'
                  | INTKW ID '[' Empty ']' '[' Empty ']' '=' Array2d ';'"""

        if not p[4]: p[4] = len(p[10])
        if not p[7]: p[7] = len(p[10][0])

        if len(p[10]) != p[4]:
            print(f"Error in line {p.lineno(2)}: mismatch between expected number of rows and actual number of rows found.")
            raise SyntaxError
        if len(p[10][0]) != p[7]:
            print(f"Error in line {p.lineno(2)}: mismatch between expected number of columns and actual number of columns found.")
            raise SyntaxError

        if p[2] not in self.fp:
            self.fp[p[2]] = (self.stack_size,ARRAY,(p[4],p[7]))
            self.stack_size += p[4] * p[7]
        else:
            print(f"Error in line {p.lineno(2)}: variable {p[2]} was previously declared.")
            raise SyntaxError

        p[0] = ""
        for row in p[10]:
            for elem in row:
                p[0] += f"pushi {elem}\n"

    def p_Attrib(self, p):
        "Attrib : INTKW AttribsInt ';'"
        p[0] = p[2]

    def p_AttribsInt(self, p):
        "AttribsInt : AttribsInt ',' AttribInt"
        p[0] = p[1] + p[3]

    def p_AttribsInt_single(self, p):
        "AttribsInt : AttribInt"
        p[0] = p[1]

    def p_AttribInt(self, p):
        """AttribInt : ID '=' Expression
                     | ID"""
        if p[1] not in self.fp:
            self.fp[p[1]] = (self.stack_size,INT)
            self.stack_size += 1
        else:
            print(f"Error in line {p.lineno(1)}: variable {p[1]} was previously declared.")
            raise SyntaxError
        p[0] = p[3] if len(p) > 2 else 'pushi 0\n'

    def p_Attrib_f(self, p):
        "Attrib : FLOATKW AttribsFloat ';'"
        p[0] = p[2]

    def p_AttribsFloat(self, p):
        "AttribsFloat : AttribsFloat ',' AttribFloat"
        p[0] = p[1] + p[3]

    def p_AttribsFloat_single(self, p):
        "AttribsFloat : AttribFloat"
        p[0] = p[1]

    def p_AttribFloat(self, p):
        """AttribFloat : ID '=' ExpressionF
                       | ID"""
        if p[1] not in self.fp:
            self.fp[p[1]] = (self.stack_size,FLOAT)
            self.stack_size += 1
        else:
            print(f"Error in line {p.lineno(1)}: variable {p[1]} was previously declared.")
            raise SyntaxError
        p[0] = p[3] if len(p) > 2 else 'pushf 0.0\n'

    def p_Attrib_s(self, p):
        "Attrib : STRKW AttribsString ';'"
        p[0] = p[2]

    def p_AttribsString(self, p):
        "AttribsString : AttribsString ',' AttribString"
        p[0] = p[1] + p[3]

    def p_AttribsString_single(self, p):
        "AttribsString : AttribString"
        p[0] = p[1]

    def p_AttribString(self, p):
        "AttribString : ID '=' String ';'"
        if p[1] not in self.fp:
            self.fp[p[1]] = (self.stack_size,STRING)
            self.stack_size += 1
        else:
            print(f"Error in line {p.lineno(1)}: variable {p[1]} was previously declared.")
            raise SyntaxError
        p[0] = p[3]

    def p_Attrib_Error(self, p):
        """Attrib : INTKW error ';'
                  | FLOATKW error ';'
                  | STRKW error ';'"""
        p[0] = ""

    def p_Command_Redefine(self, p):
        "Command : Redefine ';'"
        p[0] = p[1]

    def p_Redefine(self, p):
        "Redefine : VAR '=' Expression"
        p[0] = f"{p[3]}storeg {self.fp[p[1]][0]}\n"

    def p_Redefine_ppmm(self, p):
        """Redefine : VAR PP
                    | VAR MM"""
        i = self.fp[p[1]][0]
        p[0] = f"pushg {i}\npushi 1\n{'add' if p[2] == '++' else 'sub'}\nstoreg {i}\n"

    def p_Redefine_ArrayElem(self, p):
        "Redefine : VARA '[' Expression ']' '=' Expression"
        p[0] = f"pushgp\npushi {self.fp[p[1]][0]}\npadd\n{p[3]}{p[6]}storen\n"

    def p_Redefine_ArrayElem_f(self, p):
        "Redefine : VARA '[' Expression ']' '=' ExpressionF"
        p[0] = f"pushgp\npushi {self.fp[p[1]][0]}\npadd\n{p[3]}{p[6]}ftoi\nstoren\n"

    def p_Redefine_Array2dElem(self, p):
        "Redefine : VARA '[' Expression ']' '[' Expression ']' '=' Expression"
        p[0] = f"pushgp\npushi {self.fp[p[1]][0]}\npadd\n{p[3]}pushi {self.fp[p[1]][2][1]}\nmul\n{p[6]}add\n{p[9]}storen\n"

    def p_Redefine_Array2dElem_f(self, p):
        "Redefine : VARA '[' Expression ']' '[' Expression ']' '=' ExpressionF"
        p[0] = f"pushgp\npushi {self.fp[p[1]][0]}\npadd\n{p[3]}pushi {self.fp[p[1]][2][1]}\nmul\n{p[6]}add\n{p[9]}ftoi\nstoren\n"

    def p_Redefine_pp_f(self, p):
        """Redefine : VARF PP
                    | VARF MM"""
        i = self.fp[p[1]][0]
        p[0] = f"pushg {i}\npushf 1.0\n{'fadd' if p[2] == '++' else 'fsub'}\nstoreg {i}\n"

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
        p[0] = p[3] + f"jz l{self.labels_if}\n" + p[5] + f"l{self.labels_if}:\n" + f"le{self.labels_if_else}:\n"
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

    def p_Expression_pow(self, p):
        "Expression : Expression POW Expression"
        p[0] = f"""pushi 1
{p[3]}pow{self.labels_pow}:
pushsp
load -1
pushi 0
sup
jz endpow{self.labels_pow}
pushsp
dup 1
load -2
{p[1]}mul
store -2
pushsp
dup 1
load -1
pushi 1
sub
store -1
jump pow{self.labels_pow}
endpow{self.labels_pow}:
pop 1
"""
        self.labels_pow += 1

    def p_ExpressionF_pow(self, p):
        "ExpressionF : ExpressionF POW Expression"
        p[0] = f"""pushf 1.0
{p[3]}pow{self.labels_pow}:
pushsp
load -1
pushi 0
sup
jz endpow{self.labels_pow}
pushsp
dup 1
load -2
{p[1]}fmul
store -2
pushsp
dup 1
load -1
pushi 1
sub
store -1
jump pow{self.labels_pow}
endpow{self.labels_pow}:
pop 1
"""
        self.labels_pow += 1

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

    def p_Value_ArrayElem(self, p):
        "Value : VARA '[' Expression ']'"
        p[0] = f"pushgp\npushi {self.fp[p[1]][0]}\npadd\n{p[3]}loadn\n"

    def p_Value_Array2dElem(self, p):
        "Value : VARA '[' Expression ']' '[' Expression ']'"
        p[0] = f"pushgp\npushi {self.fp[p[1]][0]}\npadd\n{p[3]}pushi {self.fp[p[1]][2][1]}\nmul\n{p[6]}add\nloadn\n"

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
        p[0] = "pushs " + '"' + p[1].strip('"') + '"' + "\n"

    def p_String_var(self, p):
        "String : VARS"
        p[0] = f"pushg {self.fp[p[1]][0]}\n"

    def p_String_input(self, p):
        "String : INPUT '(' String ')'"
        p[0] = f"{p[3]}writes\nread\n"

    def p_String_input_empty(self, p):
        "String : INPUT '(' ')'"
        p[0] = f"read\n"

    def p_Empty(self, p):
        "Empty : "
        pass

    def p_error(self, p):
        print(f"Syntax error - unexpected token '{p.value}' on line {p.lineno}.")


    def build(self, **kwargs):
        self.fp = dict()
        self.stack_size = 0
        self.lexer = Lexer(self.fp)
        self.lexer.build()
        self.parser = yacc.yacc(module=self, **kwargs)
        self.labels_if = 0
        self.labels_if_else = 0
        self.labels_cycle = 0
        self.labels_cycle_exit = 0
        self.labels_pow = 0