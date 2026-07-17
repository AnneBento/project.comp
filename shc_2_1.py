#!/usr/bin/python
# -*- coding: UTF-8 -*-




import sys
import os
import pickle
import random
import glob
import subprocess


PROJECT = "project.comp"
PROVAS = "provas.tex"
LOG = "project.log"   
TEMP = "temp.tex"
REPORT = "report.txt"
STAT_REPORT = "stat.tex"
FSTUDENTS = "students.txt"
FGEAR = "fgear.dat"
FHEAD = "head.txt"
FTAIL = "tail.txt"
SUBMITS = "submits.dat"
RESPS = "resps.dat"


PREAMB =  """
\\documentclass[10pt,a4paper,twocolumn]{report}




\\usepackage[utf8]{inputenc}
\\usepackage[portuguese,brazilian]{babel}
\\usepackage{listings}
\\usepackage{amsmath}
\\usepackage{amsfonts}
\\usepackage{amssymb}
\\usepackage{graphicx}
\\usepackage{enumerate}
\\usepackage{anysize}
\\usepackage{bookman}
\\usepackage{fancyhdr}
\\setlength{\\headheight}{12.18494pt}




\\marginsize{0.5cm}{0.5cm}{0cm}{0cm}
\\pagestyle{fancy}




\\author{...}
\\begin{document}
"""




HEAD = """
\\begin{flushleft}
Universidade ...\\\\
Campus ...\\\\
...\\\\
Professor ...\\\\
\\end{flushleft}




"""




oneQuest = lambda k: f"""%%-- QUESTÃO {k} --
 
\\quest 




\\item{{1,c}} 
\\item{{2,e}} 
\\item{{3,e}} 
\\item{{4,e}} 
\\item{{5,e}} 
"""




TAIL = """
\\end{document}
"""
ROT_PREAMB = 'Preâmbulo'
ROT_HEAD = 'Cabeçalho'
ROT_QUEST = lambda k : f'Quest-{k:02d}'
ROT_TAIL = 'Término'




# oneQuest = lambda q: ROT_QUEST(q) + '\n' + CONTQUEST(q)
#basicContent = lambda n: dict([(ROT_PREAMB, PREAMB),\
 #                              (ROT_HEAD, HEAD)] + quests(n) + [(ROT_TAIL,\
  #                             TAIL)])


QUEST = "\\quest"
ITEM = "\\item{"




submitionsReport = lambda serial_resps, serial_id_tabela, serial_id_certas_erradas_nota: f"""
\\documentclass[10pt,a4paper]{{report}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[english,portuges,brazilian]{{babel}}
\\usepackage{{supertabular}}
\\begin{{document}}
   \\begin{{flushleft}} GABARITOS \\end{{flushleft}}
   \\begin{{supertabular}}{{|l|l|}}
   \\hline
   serial & gabarito \\\\
   \\hline    
   {serial_resps}
   \\hline
   \\end{{supertabular}}




   \\newpage
   \\begin{{flushleft}} TABELAS-RESPOSTAS \\end{{flushleft}}
   \\begin{{supertabular}}{{|l|l|l|}}
   \\hline
   serial & ID & Tabela-Resposta \\\\
   \\hline    
   {serial_id_tabela}
   \\hline
   \\end{{supertabular}}




   \\newpage
   \\begin{{flushleft}} RESULTADOS \\end{{flushleft}}
   \\begin{{supertabular}}{{|l|l|l|l|l|}}
   \\hline
   serial & ID & certas & erradas & nota \\\\
   \\hline    
   {serial_id_certas_erradas_nota}
   \\hline
   \\end{{supertabular}}




\\end{{document}}
"""


fold = "QUESTS"


content = {}
submits = {}


def load(fdat):
    if not os.path.exists(fdat):
        return None
    with open(fdat, 'rb') as f:
        return pickle.load(f)


def dump(dat, fdat):
    with open(fdat, 'wb') as f:
        pickle.dump(dat, f)




def generateGear(np, nq):
    gear = {}
    letters = "ABCDE"
    sequencia = list(range(1, nq+1))
    x = [1, 2, 3, 4, 5] 


    for serial in range(1, np+1):
        random.shuffle(sequencia)
        mapas = {}
        for quest in sequencia:
            random.shuffle(x)
            mapas[quest] = [(letters[k], x[k]) for k in range(5)]
        gear[serial] = [sequencia[:], mapas]
    return gear

def loadStudents():
    if not os.path.exists(FSTUDENTS):
        return {}
    dstudents = {}

    lines = open(FSTUDENTS, "r").read().splitlines()
    serial = 1
    for line in lines:
        splited = line.split()
        mat, nome = splited[0], ' '.join( splited[1:] )
        dstudents[serial] = mat, nome.upper()
        serial += 1 
    np = len(dstudents)


    return dstudents        


# def saveAll():
#     dic = {'NP':           np,
#            'NQ':           nq,
#            'MAX_NOTA':     max_nota,
#            'STUDENTS':     students,
#            'CONTENT':      content,
#            'GEAR':         gear,
#            'RESPS':        resps,
#            'SUBMITS':      submits}
#     b = pickle.dumps(dic)
#     with open(PROJECT, 'wb') as f:
#         f.write(b)


# TALVEZ SEJA REMOVÍVEL
def iterRot():
    yield ROT_PREAMB
    yield ROT_HEAD
    for k in range(nq):
        rot = ROT_QUEST(k+1)
        if rot in content:
            yield rot
    yield ROT_TAIL


# TALVEZ SEJA REMOVÍVEL
def iterRotQuest():
    for k in range(nq):
        rot = ROT_QUEST(k+1)
        if rot in content:
            yield rot, k+1


# TALVEZ SEJA REMOVÍVEL
def rotIsQuest(rot):
    for r, q in iterRotQuest():
        if r == rot:
            return True
    return False


# Teve o nome trasnformado (antes compileTexInside)
def compileTex(texContent, texFile):  
    
    f = open(texFile, 'w+')    
    f.write( texContent )
    f.close()
    
    args = ["pdflatex",\
            "-shell-escape",\
            #"-file-line-error",\
            #"-interaction nonstopmode",\
            texFile\
            #"-halt-on-error",\
            #"-output-directory",\
            #self.folder
            ]
    
    #subprocess.call( [a.decode('utf-8') for a in args])
    subprocess.call( args )
    log = ''
    if os.path.exists(LOG):
        x = open(LOG, "r").read()
        log = ''.join( [s+'\n' for s in x.splitlines() if s.lower().find('error')>=0] )
        if len(log) == 0:
            log = '--- sem erros ---'
    #for fnome in glob.glob(fbase + '.*'):
    #    ext = os.path.splitext(fnome)[1]
    #    if ext.upper() in ['.LOG', '.AUX', '.TEX']:
    #        os.remove(fnome)
    return log


def popItemQuest(s, pos_inicial=0):
    pos_final = -1
    args = []
    enunciado = ""
    i = s.find(ITEM, pos_inicial)
    if i>=0:
        j = s.find("}", i+1)
        if j>0: 
            args = s[ i+len(ITEM):j ].split(",")
            pos_final = s.find(ITEM, j+1) 
            if pos_final<0: pos_final = len(s)
            enunciado = s[j+1:pos_final]
    return enunciado, args, pos_final 


def splitQuest(s):    
    enunciado = ""
    i = j = s.find(QUEST)
    if i>0:
        i += len(QUEST)
        j = s.find(ITEM, i)
        enunciado = s[i:j]
    certas = []
    items = {}
    for i in range(5):
        e, args, j = popItemQuest(s, j)
        if len(args) == 2:
            key, ch = int( args[0] ), args[1][0].lower()
            if ch=="c": certas.append(key)
            items[key] = e
    return enunciado, items, certas


# Teve o nome alterado (antes transformQuestToTex)
def bodyQuest(s, mapa):
    enunciado, items, certas = splitQuest(s)
    res, body = [], ""
    for letra, key in mapa:
        if key in items.keys():
            body += f"\\item {items[key]}\n"
            if key in certas:
                res.append(letra)         
    return f""" 
    \\item {enunciado}
    \\begin{{enumerate}}
    {body}
    \\end{{enumerate}}""", res


# Nome alterado (antes qTest)
def getContentQuest(num_quest):
    s = ''    
    s += PREAMB      
    s += f'\\lhead{{TESTE DA QUESTÃO {num_quest:02d}}} \n \\begin{{enumerate}}\n'
    fileQuest = fold + os.sep + f"quest{num_quest:02d}.txt"
    txt = open(fileQuest, "r").read()
    qs, r = bodyQuest(txt, [ ("ABCDE"[k], k+1) for k in range(5) ] ) 
    s += qs[:]     
    s += '\\end{enumerate} \n\nRESP(s): '
    for ch in r: s += ch
    s += TAIL
    return s


def getTexGradeTabelaResposta(matricula, nome, serial, nquests):
    res = f'Matrícula: {matricula}\\\\ Nome: {nome} \\\\ Serial: {serial:02d}\\\\'
    res += '\n\\begin{tabular}{|l|l|l|l|l|}\\hline\n'
    d = 1
    while nquests % 5 != 0: nquests += 1
    for k in range(1, nquests + 1):
        res += f'{k:02d} '
        if k/5 == d: 
            res += '\\\\ \\hline \n & & & & \\\\ \\hline \n'
            d += 1
        else:  
            res += " &"
    res += '\\end{tabular}' 
    res += "\n \\cleardoublepage \n"
    return res


def getCurrentContentQuest(q):
    fnome = fold + os.sep + "quest{0:02d}.txt".format(q)
    with open(fnome, "r") as f:
        return f.read()


# Nome alterado (antes compileToPdf)
def getTextExams():
    resps = {}
    s = PREAMB
    xs = open(fold + os.sep + FHEAD, "r").read()
    ys = open(fold + os.sep + FTAIL, "r").read()


    for serial in gear.keys():
        sequencia, mapas = gear[serial]
        s += xs
        s += f'\\lhead{{{serial:02d}}} \n \\begin{{enumerate}}'
        resp = {}
        for q in sequencia:
            content = getCurrentContentQuest(q)
            rot = ROT_QUEST(q)
            qs, r = bodyQuest( content, mapas[q] ) 
            s += qs
            resp[q] = r
        s += '\\end{enumerate} \n'
        resps[serial] = resp
        mattricula, nomealuno = students.get(serial, ('-', '-') )
        s += getTexGradeTabelaResposta(mattricula, nomealuno, serial, nq)
    s += ys


    dump(resps, RESPS)
    return s


def clearSubmits():
    submits = {}


def evalQuest(serial, q):
    resps = load(RESPS)
    submits = load(SUBMITS)


    if not serial in resps or \
        not serial in submits: 
        return 'INVALIDA'
    resps = resps[serial]
    tabela = submits[serial][serial]
    if len(resps[q]) == 0:
        return 'ANULADA'
    if tabela[q] in resps[q]:
        return 'CERTA'
    else:
        return 'ERRADA'


def calcNota(serial):
    qc, qt = 0, 0
    sequencia = gear[serial][0]
    for q in sequencia:
        e = evalQuest(serial, q)
        if e == None: continue
        if e != 'ANULADA':
            qt += 1
        if e == 'CERTA':
            qc += 1
    return qc, qt        


def addSubmit(serial, submissionText):
    submit = {}


    if not serial in gear.keys():
        print(gear)
        raise Exception('Serial Inválido')
    tabela_resposta, k = {}, 0
    sequencia = gear[serial][0]
    for ch in submissionText.upper():
        if ch in "ABCDEX": 
            #j = sequencia.get(k, -1)
            if k >= nq:
                raise Exception('Número de questões excede {0}!'.format(nq))    
            tabela_resposta[ sequencia[k] ] = ch
            k += 1
    if k<nq:
        raise Exception('Número de questões é menor que {0}!'.format(nq))    
    submit[serial] = tabela_resposta
    
    return submit


def getEval(serial):
    """
    (serial)|respostas|mat|nome|tabela-resposta|certas|erradas|nota
    """
    submits = load(SUBMITS)[serial]
    resps = load(RESPS)
    eval = {}                  
    eval['SERIAL'] = f'{serial:02d}'
    eval['GABARITO'] = ''
    sequencia, mapa = {}, {}
    if serial in resps:       
        resps = resps[serial]
        sequencia, mapa = gear[serial]
        for quest in range(nq):
            q = sequencia[quest]
            n = len(resps[q])
            if n==0:
                eval['GABARITO'] += 'X'
            elif n==1:
                eval['GABARITO'] += resps[q][0]
            else:
                eval['GABARITO'] += '('
                for ch in resps[q]: 
                    eval['GABARITO'] += ch
                eval['GABARITO'] += ')'
    eval['MATRICULA'], eval['NOME'] = students.get(serial, ('-', '<SEM NOME>'))            
    if serial in submits:
        qc, qt = calcNota(serial)
        eval['TABELA_RESPOSTA'] = ''
        sub = submits[serial]
        for quest in range(nq):
            q = -1
            if 0 <= quest < len(sequencia):
                q = sequencia[quest]
            eval['TABELA_RESPOSTA'] += sub.get(q, '?')
        if qt == 0: 
            eval['NOTA'] = '0'            
        else:
            eval['NOTA'] = f"{(qc * max_nota / qt):.1f}"       
        eval['CERTAS'] = f"{qc}"
        eval['ERRADAS'] = f"{qt - qc}"
    else:
        eval['TABELA_RESPOSTA'] = '-'
        eval['CERTAS'] = '-'
        eval['ERRADAS'] = '-'
        eval['NOTA'] = '-'
    return eval


# TALVEZ SEJA REMOVÍVEL
def getListEval():
    submits = load(SUBMITS)
    for serial in gear.keys():
        if serial in submits:
            yield getEval(serial)


# NOME ALTERADO (ANTES compileSubmitReport)
def makeSubmitReport():
    txtresults = "serial\tID\t(C)\t(E)\tnota\n" 
    sr, smt, smcen = '', '', ''
    lista = getListEval()
    
    for e in lista:
        sr += f"{e['SERIAL']} & {e['GABARITO']} \\\\"
        smt += f"{e['SERIAL']} & {e['MATRICULA']} & {e['TABELA_RESPOSTA']} \\\\ \n"
        print(e['NOTA'])
        smcen += f"{e['SERIAL']} & {e['MATRICULA']} & {e['CERTAS']} & {e['ERRADAS']} & {e['NOTA']} \\\\ \n"
        txtresults += f"{e['SERIAL']} \t {e['MATRICULA']} \t {e['CERTAS']} \t {e['ERRADAS']} \t {e['NOTA']} \n"
    
    tex = submitionsReport(sr, smt, smcen)
    
    with open(REPORT, 'w') as f:
        f.write(txtresults)
    
    return compileTex(tex, 'report.tex')


def compileStatReport():
    tex = content[ROT_PREAMB] + content[ROT_HEAD]
    tex += '\\textbf{RELATÓRIO ESTATÍSTICO} \\\\'
    tex += '\\begin{enumerate}\n'
    for q in range(1, nq+1):
        rot = ROT_QUEST(q)
        s = content[rot]
        enunciado, items, certas = splitQuest(s)
        tex += '\\item {0}\n'.format(enunciado)
        tex += '\\begin{itemize}\n'
        for key in certas:
            tex += '\\item {0}\n'.format(items[key])
        tex += '\\end{itemize}\n'
        acertos, total = 0, 0
        for serial in gear.keys():
            if serial in submits:
                e = evalQuest(serial, q)
                if e == None: continue
                if e != 'ANULADA':
                    total += 1
                if e == 'CERTA':
                    acertos += 1
        tex += 'Acertos: {0}/{1}\n'.format(acertos, total)
    tex += '\\end{enumerate}\n'
    tex += content[ROT_TAIL]
    return compileTex(tex, STAT_REPORT)

def removeBlankLines(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    non_blank_lines = [line for line in lines if line.strip()]

    with open(file_path, 'w') as file:
        file.writelines(non_blank_lines)

if __name__ == "__main__":
    a = sys.argv
    if len(a) != 2:
        print("Quantidade de argumentos inválida!")
        sys.exit()
    
    cmd = a[1]

    if cmd == "--create":
        if os.path.exists(PROJECT):
            print("Projeto já existe!")
            sys.exit()


        if not os.path.exists(FSTUDENTS):
            print("Lista de estudantes não presente!")
            sys.exit()


        nq = int(input("Número de questões: "))
        removeBlankLines(FSTUDENTS)
        students = loadStudents()
        np = len(students.keys())
        max_nota = float(input("Nota máxima: "))
        gear = generateGear(np, nq)


        d = {'NQ': nq, 'NP': np, 'STUDENTS': students, 'MAX_NOTA': max_nota, 'GEAR': gear}
        dump(d, PROJECT)


        if not os.path.exists(fold):
            os.mkdir(fold)


        hf = fold + os.sep + FHEAD
        with open(hf, "w") as f:
            f.write(HEAD)


        for k in range(nq):
            fnome = fold + os.sep + "quest{0:02d}.txt".format(k+1)
            with open(fnome, "w") as f:
                f.write(oneQuest(k+1))


        tf = fold + os.sep + FTAIL
        with open(tf, "w") as f:
            f.write(TAIL)


    if cmd == "--info":
        d = load(PROJECT)


        std = "Lista carregada"


        if not os.path.exists(FSTUDENTS):
            std = "Lista não carregada"


        g = d['GEAR']


        sg = "Gear gerado"


        if len(g) == 0:
            sg = "Gear não gerado"


        info = f"""Número de questões: {d['NQ']}\nNúmero de provas: {d['NP']}\nNota máxima: {d['MAX_NOTA']}\nAlunos: {std}\nGear: {sg}
        """


        print(info)


    if cmd == "--test":
        d = load(PROJECT)
        nq = d['NQ']
        
        q = int(input("Número da questão: "))
        
        if q < 1 or q > nq:
            print("Questão inválida!")
            sys.exit()
        
        cont = getContentQuest(q)
        compileTex(cont, TEMP)


    if cmd == "--exams":
        d = load(PROJECT)
        nq = d['NQ']
        np = d['NP']
        students = d['STUDENTS']
        gear = d['GEAR']
        max_nota = d['MAX_NOTA']


        s = getTextExams()
        compileTex(s, PROVAS)


    if cmd == "--submit":
        d = load(PROJECT) # testar exemplos sem lista de estudantes
        students = d['STUDENTS']
        gear = d['GEAR']
        nq = d['NQ']
        max_nota = d['MAX_NOTA']


        serial = int(input("Número de serial: ")) # serial é lido como inteiro


        if serial not in students.keys():
            print("Serial inválido!")
            sys.exit()
            
        submission = input("Respostas: ")
        
        print(f"\nSerial: {serial}\nNome: {students[serial][1]}\nMatricula: {students[serial][0]}" )


        print(f"Deseja submeter esses dados?", end=" ")


        while True:
            res = input("(s/n): ")


            if res.upper()[0] == "S":
                break
            elif res.upper()[0] == "N":
                sys.exit()
            else:
                print("Opção inválida!")
            
        submit = addSubmit(serial, submission)
        submits = {}


        if os.path.exists(SUBMITS):
            submits = load(SUBMITS)
        
        if serial in submits:
            while True:
                res = input("\nJá existe uma submissão para esse serial. Deseja sobrescrever? (s/n): ")
                if res.upper()[0] == "S":
                    break
                elif res.upper()[0] == "N":
                    sys.exit()
                else:
                    print("Opção inválida!")
        submits[serial] = submit
        dump(submits, SUBMITS)
        
        submitResult = getEval(serial)
        
        print("-" * 30)


        # Conteúdo
        for key, value in submitResult.items():
            print(f"{key:<20} {value}")
    
    if cmd == "--report":
        d = load(PROJECT) # testar exemplos sem lista de estudantes
        students = d['STUDENTS']
        gear = d['GEAR']
        nq = d['NQ']
        max_nota = d['MAX_NOTA']
        
        makeSubmitReport()

    if cmd == '--help' or cmd == '--h':
        print("Comandos disponíveis:")
        print("--create: Cria um novo projeto")
        print("--info: Exibe informações do projeto")
        print("--test: Gera os arquivos tex e pdf de uma questão")
        print("--exams: Gera as provas")
        print("--submit: Submete respostas de um aluno")
        print("--report: Gera o relatório das submissões")
        print("--help: Exibe os comandos disponíveis")




    # dic = {
    #     'CONTENT': basicContent(nq),
    #     'GEAR': gear,
    #     'RESPS': resps,
    #     'STUDENTS': students,
    #     'SUBMITS': submits,
    #     'NP': np,
    #     'NQ': nq,
    #     'MAX_NOTA': max_nota
    # }


    # else:
    #     dic = pickle.load(open(PROJECT, 'r'))
    #     content = dic['CONTENT']
    #     gear = dic['GEAR']
    #     resps = dic['RESPS']
    #     students = dic['STUDENTS']
    #     submits = dic['SUBMITS']
    #     np = dic['NP']
    #     nq = dic['NQ']
    #     max_nota = dic['MAX_NOTA']
