import re
import sys

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

print("\nFicheiro carregado com sucesso!\n")

while True:
    opt = input("""1) Nomes dos concorrentes individuais de Valongo.
2) Nome, nº e prova dos concorrentes chamados \"Paulo\" ou \"Ricardo\" que usam o GMail.
3) Informação dos atletas da equipa \"TURBULENTOS\"
4) Lista ordenada de escalões e atletas por escalão.
5) Gerar página HTML com informação.\n
0) Sair.\n
Escolha a opção pretendida: """).strip()
    if opt == '0': break

    elif opt == '1': # alinea a
        print("Nomes dos concorrentes individuais de Valongo:")
        for inscrito in inscritos:
            if inscrito["equipa"] == "Individual" and "Valongo" in inscrito["morada"]:
                print("-", inscrito["nome"].upper())

    elif opt == '2': #alinea b
        for inscrito in inscritos:
            if m := re.search(r'@gmail\.com$', inscrito["email"]):
                if o := re.search(r'(Paulo|Ricardo)', inscrito["nome"]):
                    print(f'Nome: {inscrito["nome"]};\nProva: {inscrito["prova"]}\n')

    elif opt == '3': # alinea c
        for inscrito in inscritos:
            if m := re.fullmatch(r'(?i:turbulentos)',inscrito["equipa"]):
                print(f'\nNome: {inscrito["nome"]};\nData de nascimento: {inscrito["dataNasc"]};\nMorada: {inscrito["morada"]};\nEmail: {inscrito["email"]};\nProva: {inscrito["prova"]};\nEscalão: {inscrito["escalao"]}')

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
            equipas.setdefault(inscrito["equipa"].upper(), list()).append(inscrito)
        with open("equipas.html","w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>\n
<html>
    <head>
        <title>Equipas</title>
    </head>
    <body>
""")

            for equipa in sorted(equipas.keys(), key=lambda x : len(equipas[x]), reverse=True):
                with open(f"equipas/{''.join(x for x in equipa if x.isalnum())}.html","w",encoding="utf-8") as ff:
                    ff.write(f"""<!DOCTYPE html>
<html>
    <head>
        <title>{equipa}</title>
    </head>
    <body>
        <h1>Equipa: {equipa}</h1>
        <h2>{len(equipas[equipa])} atletas</h2>
        <ul>
""")
                    for atleta in equipas[equipa]:
                        ff.write(f"""            <li>{atleta["nome"]}</li>
                <ul>
                    <li>Escalão: {atleta["escalao"]}</li>
                    <li>Prova: {atleta["prova"]}</li>
                </ul>
""")
                    ff.write("""        </ul>
    </body>
</html>
""")
                    
                f.write(f"""        <h1><a href="./equipas/{''.join(x for x in equipa if x.isalnum())}.html">{equipa}</a></h1>
        <h2>{len(equipas[equipa])} atletas</h2>
""")
            f.write("""    </body>
</html>
""")
        print("\nFicheiro HTML gerado com sucesso!")

    input("\nPrima ENTER para continuar.")
