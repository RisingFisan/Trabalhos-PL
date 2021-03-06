import re
import sys
from datetime import datetime, timedelta
import similar

def main():
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
    progress = 10
    for i,inscrito in enumerate(lista_inscritos):
        if i * 100 // len(lista_inscritos) > progress:
            print(f"Lendo ficheiro... {progress}% concluído")
            progress += 10
        insc_dict = dict()
        for linha in inscrito.splitlines():
            linha_stripped = linha.strip()
            if linha_stripped:
                m = re.search(r'"(\w+)"\s*:\s*"(.*)"\s*,?',linha_stripped)
                insc_dict[m.group(1)] = m.group(2)

        not_duplicate = all(any(similar.similarity(inscrito[key].lower(), insc_dict[key].lower()) > 2 for key in inscrito) for inscrito in inscritos)

        if not_duplicate: inscritos.append(insc_dict)

    print("Ficheiro carregado com sucesso!")

    while True:
        opt = input("""\n1) Nomes dos concorrentes individuais de Valongo.
2) Nome, email e prova dos concorrentes chamados \"Paulo\" ou \"Ricardo\" que usam o GMail.
3) Informação dos atletas da equipa \"TURBULENTOS\"
4) Lista ordenada de escalões e atletas por escalão.
5) Gerar página HTML com informação sobre provas e equipas.\n
0) Sair.\n
Escolha a opção pretendida: """).strip()
        if opt == '0': break

        elif opt == '1': # alinea a
            print("\nNomes dos concorrentes individuais de Valongo:")
            for inscrito in inscritos:
                if similar.similarity(inscrito["equipa"].lower(),"individual") < 2 and (n := re.search(r'(?i:valongo)',inscrito["morada"])):
                    print("-", inscrito["nome"].upper())

        elif opt == '2': # alinea b
            print("\nNome, email e prova dos concorrentes chamados \"Paulo\" ou \"Ricardo\" que usam o GMail:")
            for inscrito in inscritos:
                if m := re.search(r'@gmail\.com$', inscrito["email"]):
                    if o := re.search(r'(?i:Paulo|Ricardo)', inscrito["nome"]):
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

        elif opt == '4': # alinea d
            esc_dict = dict()
            for inscrito in inscritos:
                if re.match(r'(\w+)', inscrito["escalao"]):
                    x = esc_dict.get(inscrito["escalao"],0)
                    esc_dict[inscrito["escalao"]] = x+1
            for escalao in sorted(esc_dict):
                print("Escalão:", escalao, "; Número de atletas:", esc_dict[escalao])

        elif opt == '5': # alinea e
            today = datetime.today()
            equipas = dict()
            provas = dict()
            for i, inscrito in enumerate(inscritos):
                prova = inscrito["prova"]
                equipa = inscrito["equipa"].upper()
                for eqp in equipas:
                    if similar.similarity(eqp.upper(),equipa) < 2:
                        equipa = eqp.upper()
                        break
                if not (m := re.match(r',|N/D|S/ CLUBE', equipa)):
                    equipas.setdefault(equipa, list()).append(inscrito)
                    provas.setdefault(prova, dict()).setdefault(equipa, list()).append(inscrito)
                else:
                    provas.setdefault(prova, dict()).setdefault("INDIVIDUAL", list()).append(inscrito)

    # ------------------------------------------------------------------
    #                  FICHEIRO PROVAS
    # ------------------------------------------------------------------

            with open("equipas.html","w", encoding="utf-8") as f:
                f.write(f"""<!DOCTYPE html>\n
<html>
    <head>
        <title>Equipas</title>
        <style>{style_provas}</style>
    </head>
    <body>
    <h1>PROVAS</h1>
    <div class="provas">
""")

                for prova in provas:
                    f.write(f"""    <div class="prova">
        <h2>{prova}</h2>
""")
                    for equipa in sorted(provas[prova].keys(), key=lambda x : len(provas[prova][x]), reverse=True):
                        f.write(f"""        <a href="./equipas/{''.join(x for x in equipa if x.isalnum())}.html">
            <span class="equipa">
                <h2>{equipa if equipa != "INDIVIDUAL" else "Sem equipa"}</h2>
                <div class="num_a"><p>{len(provas[prova][equipa])} atleta{'s' if len(provas[prova][equipa]) > 1 else ''}</p></div>
            </span>
        </a>
""")

                    f.write("    </div>\n")
                f.write("""    </div>
    </body>
</html>
""")

    # ------------------------------------------------------------------
    #                  FICHEIROS EQUIPAS
    # ------------------------------------------------------------------

            for equipa in equipas:
                with open(f"equipas/{''.join(x for x in equipa if x.isalnum())}.html","w",encoding="utf-8") as ff:
                    ff.write(f"""<!DOCTYPE html>
    <html>
        <head>
            <title>{equipa}</title>
            <style>{style_equipas}</style>
        </head>
        <body>
            <h1>{"Equipa: " + equipa if equipa != "INDIVIDUAL" else "Atletas sem equipa"}</h1>
            <h2>Constituição: {len(equipas[equipa])} atleta{'s' if len(equipas[equipa]) != 1 else ''}</h2>
            <div class="atletas">
""")

                    for atleta in equipas[equipa]:
                        try:
                            if "ou" not in atleta["dataNasc"]:
                                birth = datetime.strptime(atleta["dataNasc"],"%d/%m/%y")
                                if birth > datetime.today(): birth = birth.replace(year = birth.year - 100)
                        except ValueError:
                            birth = None
                        ff.write(f"""            <div class="atleta">
                    <h3>{atleta["nome"]}</h3>
                    <ul>
                        <li>Idade: {str(today.year - birth.year - ((today.month,today.day) < (birth.month,birth.day))) + " anos" if birth else "-"}</li>
                        <li>Escalão: {atleta["escalao"] or "-"}</li>
                        <li>Prova: {atleta["prova"]}</li>
                    </ul>
                    </div>
""")
                    ff.write("""        </div>
        </body>
    </html>
""")


            print("\nFicheiro HTML gerado com sucesso!")

        else:
            continue
        input("\nPrima ENTER para continuar.")


style_provas = """
html {
    background: #5bcefa;
    color: #166888;
    font-family:fantasy;
    min-height: 100%;
}

h1,h2 {
    text-align: center;
    width: 100%;
}

.num_a {
    position: absolute;
    bottom: 0;
    left: 0px;
    right: 0px;
    text-align: center;
}

.provas {
    display: flex;
    flex-direction: column; 
}

.prova {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    background: #f5a9b8;
    color: #97273e;
    border-radius: 20px;
    margin: 50px;
}

.equipa {
    position: relative;
    flex-grow: 1;
    display: block;
    /*background-color:#ffa4d2;
    color: #ff339a;*/
    background: white;
    color: rgb(82, 82, 82);
    padding: 10px;
    width: 250px;
    border-radius: 8px;
    min-height: 200px;
}

a {
    margin: 15px;
    text-decoration: none;
}
"""

style_equipas = """
html {
    background:  	#a3a3a3;
    color: black;
    font-family:fantasy;
    min-height: 100%;
}

h1,h2,h3 {
    text-align: center;
}

.atletas {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
}

.atleta {
    /*background-color: #ffccf5;
    color: #7e3a70;*/
    background: #800080;
    color: white;
    padding: 10px;
    margin: 15px;
    width: 20%;
    border-radius: 15px;
}
"""

if __name__ == "__main__":
    main()