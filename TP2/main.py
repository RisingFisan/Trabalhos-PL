#!/usr/bin/env python3

# Linguagem Genérica Baseada nas Típicas Imperativas

from myParser import Parser
import sys

parser = Parser()

parser.build()

if len(sys.argv) < 2:
    f = ""

    while line := input():
        f += line + "\n"
        
    result = parser.parser.parse(f)
    print(result)
elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
    print("""Compilador da Linguagem Genérica Baseada nas Típicas Imperativas

Uso do comando: python main.py [nome do ficheiro de input]

O nome do ficheiro de output será igual ao do ficheiro de input, com a extensão '.vm'.

Se não for fornecido um ficheiro de input, o programa irá correr em modo "interativo", no qual é possível introduzir um pedaço de código no terminal e será apresentada a sua versão "compilada", em código-máquina.""")
else:
    with open(sys.argv[1],"r") as f:
        result = parser.parser.parse(f.read())
    with open(sys.argv[1].strip(".\\").split('.')[0] + '.vm', "w", newline='\n') as r:
        r.write(result)