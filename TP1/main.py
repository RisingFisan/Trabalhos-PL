import re
import sys
from functools import reduce

fp = None
inscritos = list()

while not fp:
    opt = input("1) Usar ficheiro predefinido (inscritos-form.json).\n\
2) Especificar ficheiro a usar.\n\n\
Escolha a opção pretendida: ").strip()
    if opt == '1':
        fp = "inscritos-form.json"
    elif opt == '2':
        fp = input("Introduza o caminho para o ficheiro que pretende utilizar: ").strip()

with open(fp, encoding="utf-8") as f:
    m = re.search(r'{\s*"inscritos":\[\s*((?:.|\n)*)\]\s*}',f.read())
    if not m:
        sys.exit("Erro - Ficheiro inválido")
    string_inscritos = m.group(1)

lista_inscritos = re.split(r'}\s*,\s*{',string_inscritos.strip(" \t\n{}"))
for inscrito in lista_inscritos:
    insc_dict = dict()
    for linha in inscrito.splitlines():
        linha_stripped = linha.strip()
        if linha_stripped:
            m = re.search(r'"(\w+)"\s*:\s*"(.*)"\s*,?',linha_stripped)
            insc_dict[m.group(1)] = m.group(2)
    inscritos.append(insc_dict)

print("\nFicheiro carregado com sucesso!")

while True:
    opt = input("""\n1) Nomes dos concorrentes individuais de Valongo.
2) Nome, email e prova dos concorrentes chamados \"Paulo\" ou \"Ricardo\" que usam o GMail.
3) Informação dos atletas da equipa \"TURBULENTOS\"
4) Lista ordenada de escalões e atletas por escalão.
5) Gerar página HTML com informação.\n
0) Sair.\n
Escolha a opção pretendida: """).strip()
    if opt == '0': break

    elif opt == '1': # alinea a
        print("\nNomes dos concorrentes individuais de Valongo:")
        for inscrito in inscritos:
            if (m := re.match(r'(?i:individual)',inscrito["equipa"])) and (n := re.search(r'(?i:valongo)',inscrito["morada"])):
                print("-", inscrito["nome"].upper())

    elif opt == '2': #alinea b
        print("\nNome, email e prova dos concorrentes chamados \"Paulo\" ou \"Ricardo\" que usam o GMail:")
        for inscrito in inscritos:
            if m := re.search(r'@gmail\.com$', inscrito["email"]):
                if o := re.match(r'(?i:Paulo|Ricardo)', inscrito["nome"]):
                    print(f'- {inscrito["nome"]}; {inscrito["email"]}; {inscrito["prova"]}')

    elif opt == '3': # alinea c
        turbulentos = list()
        for inscrito in inscritos:
            if m := re.fullmatch(r'(?i:turbulentos)',inscrito["equipa"]):
                turbulentos.append(inscrito)
        i = 0
        while True:
            print(f'\nNome: {turbulentos[i]["nome"]};\nData de nascimento: {turbulentos[i]["dataNasc"]};\nMorada: {turbulentos[i]["morada"]};\nEmail: {turbulentos[i]["email"]};\nProva: {turbulentos[i]["prova"]};\nEscalão: {turbulentos[i]["escalao"]}')
            print(f"\nPágina {i+1} de {len(turbulentos)}\n\n[a] ver anterior; [s] ver seguinte; [e] sair")
            opt = input()
            if opt == 'a' and i > 0: i -= 1
            elif opt == 's' and i < len(turbulentos) - 1: i += 1
            elif opt == 'e': break

    elif opt == '4': #alinea d --- lista dos escalões ordem alfabética, para cada um indicar #atletas inscritos nesse escalão.   
        esc_dict = dict()
        for inscrito in inscritos:
            if re.match(r'(\w+)', inscrito["escalao"]):
                x = esc_dict.get(inscrito["escalao"],0)
                esc_dict[inscrito["escalao"]] = x+1
        for key, value in esc_dict.items():
	        print("Escalão:", key, "; Número de atletas:", value)

    elif opt == '5': # alinea e
        equipas = dict()
        for inscrito in inscritos:
            equipa = inscrito["equipa"]
            if equipa not in [",","n/d","s/ clube"]:
                equipas.setdefault(equipa.upper(), list()).append(inscrito)
            else:
                equipas.setdefault("INDIVIDUAL", list()).append(inscrito)
        with open("equipas.html","w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>\n
<html>
    <head>
        <title>Equipas</title>
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
    <h1>EQUIPAS</h1>
    <div class="equipas">
""")




            for equipa in sorted(equipas.keys(), key=lambda x : len(equipas[x]), reverse=True):
                with open(f"equipas/{''.join(x for x in equipa if x.isalnum())}.html","w",encoding="utf-8") as ff:
                    ff.write(f"""<!DOCTYPE html>
<html>
    <head>
        <title>{equipa}</title>
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
        <h1>Equipa: {equipa}</h1>
        <h2>{len(equipas[equipa])} atletas</h2>
        <div class="atletas">
""")




                    for atleta in equipas[equipa]:
                        ff.write(f"""            <div class="atleta">
                <h3>{atleta["nome"]}</h3>
                <ul>
                    <li>Escalão: {atleta["escalao"] or "-"}</li>
                    <li>Prova: {atleta["prova"]}</li>
                </ul>
                </div>
""")
                    ff.write("""        </div>
    </body>
</html>
""")
                    
                f.write(f"""        <a href="./equipas/{''.join(x for x in equipa if x.isalnum())}.html">
            <span class="equipa">
                <h2>{equipa}</h2>
                <h3>{len(equipas[equipa])} atleta{'s' if len(equipas[equipa]) > 1 else ''}</h3>
            </span>
        </a>
""")
            f.write("""    </div>
    </body>
</html>
""")

        print("\nFicheiro HTML gerado com sucesso!")

    else:
        continue
    input("\nPrima ENTER para continuar.")
