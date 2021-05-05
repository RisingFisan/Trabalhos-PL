from myParser import Parser

parser = Parser()

parser.build()

f = ""

while line := input():
    f += line + "\n"
    
result = parser.parser.parse(f)
print(result)
