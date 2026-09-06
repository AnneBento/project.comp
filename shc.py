import os
import pickle #converte objetos em bytes e reconstrói depois 
import subprocess #vai ser utilizado na cmd_testar
import random
import sys

# dicionário com os caminhos do projeto
PATHS = {
    'QUESTS_DIR':'./quests',
    'PROJECT': './project.comp',
    'STUDENTS':'./students.txt',
    'PROVAS': './provas.txt',
    'REPORT': './report.txt'
}

# lê o arquivo .comp, onde todos os dados do exame estão salvos e converte esse arquivo em binário
# de volta para um dicionário python usando o pickle load. 
# Se o arquivo não existir ele retorna um dicionário vazio e assim o programa começa do zero 
def load_project(path):
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
    return{}

# salva o projeto, recebendo path direção, e data, conteúdo.
def save_project(path, data):
    with open(path, 'wb') as f:
        pickle.dump(data, f)



#---------------------------------------------------------------------------------------------------- LEITURA E PREPARAÇÃO DE ARQUIVOS!
# essa função lê um arquivo de questão escrito em formato do tipo lateX
def parse_question_file(quest_dir, filename):
    #se não existir pasta quests ou arquivos dentro da pasta, retorna none
    path = os.path.join(quest_dir, filename)
    if not os.path.exists(path):
        return None

    enunciado = ""
    alternativas = []

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

        for line in lines:
            line_str = line.strip()

            # ignora comentários do teX e linhas em branco
            if line_str.startswith('%%') or not line_str:
                continue;

            if line_str.startswith("\\quest"):
                enunciado = line_str.replace("\\quest", "").strip()

            if line_str.startswith("\\item"):
                start_bracket = line_str.find("{")
                end_bracket = line_str.find("}")

                if start_bracket != -1 and end_bracket != -1:
                    meta = line_str[start_bracket+1:end_bracket].split(",")
                    item_id = meta[0].strip();
                    status = meta[1].strip();
                    texto = line_str[end_bracket+1:].strip()
                    alternativas.append((item_id, status, texto))

    return {"enunciado": enunciado,
            "alternativas": alternativas}



# Extrai matricula e nome de cada aluno
def get_alunos(name):
    
    if not os.path.exists(name):
        print(f"[-] Erro: Arquivo '{name}' não encontrado")
        return []
    
    students = []

    with open (name, 'r', encoding = 'utf-8') as f:
        for line in f:
            line_str = line.strip();
            #se não tem linhas em branco
            if not line_str:
                continue    

            #separa por tab
            if '\t' in line_str:
                partes = line_str.split('\t', 1);
            else:
                partes = line_str.split(None, 1);

            if len(partes) >= 2:
                matricula = partes[0].strip()

                #para não quebrar o latex
                nome = partes[1].strip().replace("_", "\\_")
                students.append([matricula, nome])
            else:
                students.append([partes[0].strip(), "Estudante sem nome"])

        return students



# varre a pasta de questões e mapeia qual é o ID da alternativa correta de cada questão.
# ela vai conferir se essa questão realmente existe.
def get_correct_answers(quests_dir):
    gabarito_real = {}

    if not os.path.exists(quests_dir):
        return gabarito_real

    for file in os.listdir(quests_dir): 

        file_lower = file.lower()
        if file_lower.startswith("quest") and file_lower.endswith(".txt"):

            q_num = file_lower.replace("quest", "").replace(".txt", "")

            # ler o arquivo com o perse_question :)
            q_data = parse_question_file(quests_dir, file)
            if q_data: 
                for item_id, status, _ in q_data["alternativas"]:
                    if status == 'c':
                        gabarito_real[q_num] = item_id

    return gabarito_real



#--------------------------------------------------------------------------------------------------- EXECUÇÃO DOS COMANDOS DO USUÁRIO.

# prepara o ambiente do projeto
# cria pasta quests/
# os arquivos head.txt e tail.txt e outros .txt
def cmd_criar(num_questoes):

    quests_dir = PATHS['QUESTS_DIR']

    if not os.path.exists(quests_dir):
        os.makedirs(quests_dir)
        print(f"Pasta {quests_dir} criada com sucesso.")


# cria arquivo head.txt
    head_path = os.path.join(quests_dir, "head.txt")
    if not os.path.exists(head_path):
        with open(head_path, 'w', encoding='utf-8') as f:
            f.write("\\begin{flushleft}\n")
            f.write("Universidade Federal do Ceará - Campus Quixadá\\\\\n")
            f.write("Professor - Ricardo Reis\\\\\n")
            f.write("Disciplina: 2026.2\\\\\n")
            f.write("\\end{flushleft}\n")
            print("Arquivo 'head.txt' criado.")


    # cria o arquivo tail.txt
    tail_path = os.path.join(quests_dir, "tail.txt")
    if not os.path.exists(tail_path):
        with open(tail_path, 'w', encoding='utf-8') as f:
            f.write("% Rodapé da prova\n")
            f.write("\\vfill \\centerline{Fim da Prova!}\n")
        print("Arquivo 'tail.txt' criado.")


    # arquivos de questões com o template padrão
    for i in range(1, int(num_questoes) + 1):
        q_filename = f"quest{i:02d}.txt"
        q_path = os.path.join(quests_dir, q_filename)

        if not os.path.exists(q_path):
            with open(q_path, 'w', encoding='utf-8') as f:
                f.write(f"%% -- QUESTÃO {i:02d} --\n\n")
                f.write(f"\\quest\n\n")
                f.write("\\item{1, c}\n")
                f.write("\\item{2, e}\n")
                f.write("\\item{3, e}\n")
                f.write("\\item{4, e}\n")
            print(f"Arquivo '{q_filename}' criado.")
        else:
            print(f"Arquivo '{q_filename}' já existe e não foi sobrescrito.")



# testar uma questão isolada em lateX, monta um documento teX temporário e compila como PDF lateX via subprocess
def cmd_testar(quest_target):
    quest_dir = PATHS['QUESTS_DIR']

    if not quest_target.endswith('.txt'):
        if not quest_target.startswith('quest'):
            filename = f"quest{int(quest_target):02d}.txt"
        else:
            num_str = quest_target.replace('quest', '')
            filename = f"quest{int(num_str):02d}.txt"
    else:
        filename = quest_target

    #parse da questão
    q_data = parse_question_file(quest_dir, filename)
    if not q_data:
        print(f"Não foi possível ler a questão {filename}")
        return


    #latex minimalista de teste
    tex_test = """\\documentclass[10pt,a4paper]{article}
    \\usepackage[utf8]{inputenc}
    \\usepackage[portuguese,brazilian]{babel}
    \\usepackage{amsmath}
    \\usepackage{amsfonts}
    \\usepackage{enumitem}
    \\begin{document}
    \\section*{Teste de Compilação - """ + filename + """}

    \\noindent \\textbf{Enunciado:} """ + q_data['enunciado'] + """

    \\vspace{0.3cm}
    \\noindent \\textbf{Alternativas:}
    \\begin{enumerate}[label=\\alph*)]
    """

    for item_id, status, texto in q_data['alternativas']:
        marcadore = " [CORRETA]" if status == 'c' else ""
        tex_test += f"    \\item (ID: {item_id}) {texto}\\textbf{{{marcadore}}}\n"

    tex_test += """\\end{enumerate}
    \\end{document}
    """ 

    #escrita temporária do teX para teste
    test_tex_path = "./teste_temp.tex"
    with open(test_tex_path, 'w', encoding='utf-8') as f:
        f.write(tex_test)
    print(f"Compilando teste para '{filename}'...")


    #trava de segurança para o meu uso em windows
    try:
        #agora utiliza o compilador para pdfLatex
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", test_tex_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            print("[+] Sucesso! Arquivo 'teste_temp.pdf' gerado sem erros de sintaxe TeX.")
        else:
            print("[-] Erro na sintaxe do TeX. Verifique o arquivo .log gerado.")
    except FileNotFoundError:
        print("[-] ERRO: O executável 'pdflatex' não foi encontrado no Windows.")
        print("    Certifique-se de ter o MiKTeX instalado e adicionado ao PATH do sistema.")



# lê alunos via get_alunos
# extrai e embaralha questões via parse_question_file
# constói o código teX completo com cabeçalho e rodapé 
# grava os mapeamentos das provas individuais no dicionário VERSIONS dentro do arquivo .comp
def cmd_provas(qtd_sem_aluno=1):

    d = load_project(PATHS['PROJECT'])


    students = get_alunos(PATHS['STUDENTS'])
    if not students:
        print(f"Aviso: Arquivo '{PATHS['STUDENTS']}' não encontrado ou vazio. Gerando {qtd_sem_aluno} prova(s) sem pré-preenchimento...")
        students = []
        for i in range(1, qtd_sem_aluno + 1):
            students.append(["", ""])

    #verificar a presença dos arquivos
    head_path = os.path.join(PATHS['QUESTS_DIR'], "head.txt")
    tail_path = os.path.join(PATHS["QUESTS_DIR"], "tail.txt")

    if not os.path.exists(head_path) or not os.path.exists(tail_path):
        print(f"Erro: Os arquivos 'head.txt' ou tail.txt ausentes na pasta 'quests/'. ")
        return

    with open(head_path, 'r', encoding='utf-8') as f:
        head_content = f.read()
    with open(tail_path, 'r', encoding='utf-8') as f:
        tail_content = f.read()



    #mapeia o arquivo de questões EXISTENTES
    q_files = sorted([f for f in os.listdir(PATHS['QUESTS_DIR']) if f.lower().startswith("quest") and f.lower().endswith(".txt")]) 
    if not q_files:
        print("Nenhuma questão encontrada na pasta 'quests/'.")
        return


    #preâmbulo do documento teX
    tex_output = """\\documentclass[10pt,a4paper,twocolumn]{report}
    \\usepackage[utf8]{inputenc}
    \\usepackage[portuguese,brazilian]{babel}
    \\usepackage{amsmath}
    \\usepackage{amsfonts}
    \\usepackage{amssymb}
    \\usepackage{enumitem}
    \\usepackage{anysize}
    \\marginsize{1cm}{1cm}{1.5cm}{1.5cm}
    \\begin{document}
    """

    letras = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    d['VERSIONS'] = {}
    d['ANULADAS'] = set()

    # Aqui acontece o processo da prova de cada aluno
    for idx, student in enumerate(students):
        matricula = student[0]
        nome = student[1]
        serial = f"{idx+1:02d}"

        # identificação institucional
        tex_output += f"\\noindent\\textbf{{SERIAL DA PROVA: {serial}}} \\hfill \\textbf{{Álgebra Linear}}\\\\\n"
        tex_output += "\\rule{\\linewidth}{0.2mm}\\\\\n" 
        tex_output += head_content + "\n"


        # dados aluno
        # Quantidade de questões ativas
        qtd_q = len(q_files)

        # Montagem dos dados e do cartão de respostas
        tex_output += "\n\\vspace{0.3cm}\n"
        if not nome and not matricula:
            tex_output += f"\\noindent Matrícula: \\underline{{\\hspace{{3cm}}}} \\\\ Nome: \\underline{{\\hspace{{6cm}}}} \\\\ Serial da Prova: \\textbf{{{serial}}}\\\\\n"
        else:
            tex_output += f"\\noindent Matrícula: {matricula}\\\\ Nome: {nome} \\\\ Serial da Prova: \\textbf{{{serial}}}\\\\\n"
        tex_output += "\\vspace{0.2cm}\n"
        
        # Tabela com alinhamento centralizado 
        tex_output += "\\begin{tabular}{|" + "|".join(["c"] * qtd_q) + "|}\\hline\n"
        tex_output += "  " + " & ".join([f"{i+1:02d}" for i in range(qtd_q)]) + " \\\\ \\hline \n"
        tex_output += "  " + " & ".join(["" for _ in range(qtd_q)]) + " \\rule{0pt}{0.4cm} \\\\ \\hline \n"
        tex_output += "\\end{tabular}\n\n"
        
        tex_output += "\\vspace{0.4cm}\n"
        tex_output += "\\rule{\\linewidth}{0.1mm}\\\\\n\\vspace{0.2cm}\n"

        tex_output += " \\begin{enumerate}[label=\\arabic*., ref=\\arabic*]\n"
        version_map = {}


        # embaralha a ordem das questões para o aluno
        shuffled_q_files = list(q_files)
        random.shuffle(shuffled_q_files)
        visual_order = []

        for q_file in shuffled_q_files:
            q_num = q_file.lower().replace("quest", "").replace(".txt", "")
            q_data = parse_question_file(PATHS['QUESTS_DIR'], q_file)

            if not q_data:
                continue

            visual_order.append(q_num)
            tex_output += f"    \\item {q_data['enunciado']}\n"
            tex_output += "    \\begin{enumerate}[label=\\alph*)]\n"


            #embaralhamento das alternativas da questao
            alts = list(q_data['alternativas'])
            random.shuffle(alts)

            student_q_map = {}
            for l_idx, alt in enumerate(alts):
                letra = letras[l_idx]
                item_id = alt[0]
                tex_output += f"        \\item {alt[2]}\n"
                student_q_map[letra] = item_id

            tex_output += "    \\end{enumerate} \n"
            version_map[q_num] = student_q_map

        tex_output += " \\end{enumerate}\n"


        #rodapé
        tail_clean = tail_content.replace("\\end{document}", "")
        tex_output += tail_clean + "\n"
        tex_output += "\\clearpage\n\n"


        #guarda a estrutura da prova do aluno no dicionário
        d['VERSIONS'][serial] = {
            'nome': nome if nome else "Estudante",
            'matricula': matricula if matricula else "N/A",
            'map': version_map,
            'order': visual_order
        }

    tex_output += "\\end{document}\n"


    #agora ele abrir e vai salvar o arquivo teX e atualizar o .comp
    with open(PATHS['PROVAS'], 'w', encoding='utf-8') as f:
        f.write(tex_output)

    save_project(PATHS['PROJECT'], d)
    print(f"Código TeX das provas gerados em: {PATHS['PROVAS']}")

    #compilação da prova
    try: 
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", PATHS['PROVAS']],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            print("PDF compilado com sucesso em: ./provas.pdf")
        else:
            print("Falha na compilação teX. Verifique o arquivo 'provas.log'.")
    except FileNotFoundError:
        print("'pdflatex' não instalado/encontrado. O arquivo '.tex' e o mapa '.comp' foram salvos com sucesso.")




#registrar no arquivo (.comp) o cartão de respostas que o professor digita para determinado aluno.
def cmd_submeter(serial, respostas_str):
    d = load_project(PATHS['PROJECT'])

    #garante que o dicionário esteja no projeto
    if 'SUBMITS' not in d:
        d['SUBMITS'] = {}

    versions = d.get('VERSIONS', {})

    #verifica se o serial existe nas provas geradas
    if serial not in versions:
        print(f"Erro: O serial '{serial}' não foi encontrado no projeto.")
        return 

    aluno_infor = versions[serial]
    nome = aluno_infor['nome'].replace("\\_", "_")
    matricula = aluno_infor['matricula']
    mapa_quest = aluno_infor['map']
    total_esperado = len(mapa_quest)

    respostas_limpas = respostas_str.lower().replace(" ", "").strip()

    #validação do númerode respostas enviadas
    if len(respostas_limpas) != total_esperado:
        print(f"Erro de validação! A prova esperava {total_esperado} respostas, mas foram enviadas {len(respostas_limpas)} ('{respostas_limpas}').")
        return

    print("\n")
    print("Confirmação de submissão")
    print(f"Serial:     {serial}")
    print(f"Aluno:      {nome}")
    print(f"Matrícula:  {matricula}")
    print(f"Respostas:  {respostas_limpas.upper()}")
    print("\n")

    confirmacao = input("Deseja confirmar o registro para este aluno? [S/n]: ").strip().lower()

    if confirmacao in ['', 's', 'sim']:
        d['SUBMITS'][serial] = list(respostas_limpas)
        save_project(PATHS['PROJECT'], d)
        print(f"\nRespostas do serial {serial} ({nome}) salvas com sucesso!\n")
    else: 
        print("\nOperação cancelada. Nenhuma alteração foi salva.\n")
    


#painel visual para o usuário
#percentual de provas corrigidas 
def cmd_status():
    d = load_project(PATHS['PROJECT'])
    versions = d.get('VERSIONS', {})
    submits = d.get('SUBMITS', {})

    if not versions: 
        print("Nenhuma prova foi gerada ainda no projeto.")
        return

    #Calculos de metricas e barra de progresso
    total_provas = len(versions)
    total_entregues = len(submits)
    pendentes = total_provas - total_entregues
    porcentagem = (total_entregues / total_provas * 100) if total_provas > 0 else 0.0


    bar_len = 30
    filled = int(bar_len * total_entregues // total_provas) if total_provas > 0 else 0
    bar = '█' * filled + '░' * (bar_len - filled)


    print("\n" + "-" * 60)
    print(f"{'STATUS DE SUBMISSÃO E PAINEL DA TURMA':^60}")
    print("-" * 60)
    print(f" Progresso: [{bar}] {porcentagem:.1f}% ({total_entregues}/{total_provas})\n")
    print(f" {'SERIAL':<8} {'ESTUDANTE':<36} {'STATUS'}")
    print(" " + "-" * 56)

    proximo_sugerido = None

    for serial, info in sorted(versions.items()):
        nome_aluno = info['nome'].replace("\\_", "_")
        
        if serial in submits:
            status_str = "[OK] Submetido"
        else:
            status_str = "[ ] PENDENTE"
            if proximo_sugerido is None:
                proximo_sugerido = serial

        print(f" {serial:<8} {nome_aluno:<36} {status_str}")
          
    print(" " + "-" * 56)
    print(f" Concluídas: {total_entregues} | Pendentes: {pendentes} | Total: {total_provas}")

    if proximo_sugerido:
        print(f"\nPróxima prova pendente a submeter: Serial {proximo_sugerido}")
    else:
        print("\nTodas as provas foram submetidas com sucesso!")
    print("\n")



#anula uma questão específica
# anula ou reativa uma questão específica com confirmação de segurança
def cmd_ressubmissao(num_quest_visual):
    d = load_project(PATHS['PROJECT'])

    if 'VERSIONS' not in d or not d['VERSIONS']:
        print("Nenhuma prova foi gerada ainda.")
        return

    # garante que o conjunto de quest anuladas exista no projeto. 
    if 'ANULADAS' not in d:
        d['ANULADAS'] = set()

    # normaliza o formato do número de quest, tipo 1 -> 01
    try:
        q_num = f"{int(num_quest_visual):02d}"
    except:
        q_num = str(num_quest_visual).zfill(2)

    # verifica se a questão existe na pasta quest
    q_files = [f for f in os.listdir(PATHS['QUESTS_DIR']) if f.lower().startswith("quest") and f.lower().endswith(".txt")]
    q_existentes = [f.lower().replace("quest", "").replace(".txt", "") for f in q_files]

    if q_num not in q_existentes:
        print(f"A questão {q_num} não existe no projeto.") 
        return

    # Define qual ação será tomada para a mensagem de confirmação
    ja_anulada = q_num in d['ANULADAS']
    acao_str = "REATIVAR (desfazer anulação da)" if ja_anulada else "ANULAR"

    print("\n")
    print(" CONFIRMAÇÃO DE SEGURANÇA")
    print(f" Você está prestes a {acao_str} a Questão {q_num}.")
    if not ja_anulada:
        print(" [!] Isso desconsiderará esta questão no cálculo das notas finais.")
    else:
        print(" [!] Isso fará a questão voltar a ser contabilizada nas notas.")
    print("=" * 50 + "\n")

    confirmacao = input(f"Tem certeza que deseja {acao_str.split()[0].lower()} a Questão {q_num}? [S/n]: ").strip().lower()

    if confirmacao in ['', 's', 'sim']:
        if ja_anulada:
            d['ANULADAS'].remove(q_num)
            print(f"\n[+] Sucesso: Questão {q_num} REATIVADA! As notas serão recalculadas considerando esta questão.\n")
        else:
            d['ANULADAS'].add(q_num)
            print(f"\n[+] Sucesso: Questão {q_num} ANULADA! Ela será desconsiderada nos relatórios.\n")
        
        save_project(PATHS['PROJECT'], d)
    else:
        print("\nOperação cancelada. Nenhuma alteração foi feita.\n")



#correção e estatística 
#cruza o mapeamento da prova de cada aluno, com as respostas enviadas e o gabarito real
#calcula as notas finais e imprime a taxa de acertos/erros no arquivo .txt
def cmd_relatar():
    d = load_project(PATHS['PROJECT'])
    gabarito_atual = get_correct_answers(PATHS['QUESTS_DIR'])
    versions = d.get('VERSIONS', {})
    submits = d.get('SUBMITS', {})
    anuladas = d.get('ANULADAS', set())
    
    if not versions:
        print("[-] Erro: O projeto não tem provas geradas. Execute '--prova' primeiro.")
        return
    
    report_lines = []
    report_lines.append("="*75)
    report_lines.append("                  RELATÓRIO DE NOTAS E DESEMPENHO")
    report_lines.append("="*75)
    
    report_lines.append(f"\n{'SERIAL':<8} {'ESTUDANTE':<32} {'ACERTOS':<9} {'ERROS':<8} {'EM BRANCO':<11} {'NOTA':<6}")
    report_lines.append("-" * 75)
    
    stats_questoes = {q_num: {'certas': 0, 'erradas': 0, 'branco': 0} for q_num in gabarito_atual.keys()}
    
    for serial, v_info in sorted(versions.items()):
        nome = v_info['nome'].replace("\\_", "_")
        mapa_questoes = v_info['map']
        respostas_aluno = submits.get(serial, [])
        ordem_questoes = v_info.get('order', sorted(mapa_questoes.keys()))
    
        acertos = 0
        erros = 0
        em_branco = 0
    
        # O total de questões consideradas na nota agora ignora as anuladas
        questoes_validas = [q for q in ordem_questoes if q not in anuladas]
        total_validas = len(questoes_validas)
    
        if not respostas_aluno:
            report_lines.append(f"{serial:<8} {nome:<32} {'--':<9} {'--':<8} {'--':<11} {'PENDENTE'}")
            continue
    
        for idx, q_num in enumerate(ordem_questoes):
            # Se a questão foi anulada, ela não conta como acerto, erro ou em branco
            if q_num in anuladas:
                continue
    
            if idx < len(respostas_aluno):
                letra_marcada = respostas_aluno[idx]
    
                if letra_marcada in ['x', '-']:
                    em_branco += 1
                    if q_num in stats_questoes:
                        stats_questoes[q_num]['branco'] += 1
                else:
                    id_marcado = mapa_questoes[q_num].get(letra_marcada)
                    id_correto = gabarito_atual.get(q_num)
    
                    if id_marcado and id_marcado == id_correto:
                        acertos += 1
                        if q_num in stats_questoes:
                            stats_questoes[q_num]['certas'] += 1
                    else:
                        erros += 1
                        if q_num in stats_questoes:
                            stats_questoes[q_num]['erradas'] += 1
    
        # Cálculo proporcional de nota apenas com as questões válidas
        nota = (acertos / total_validas) * 10.0 if total_validas > 0 else 0.0
        report_lines.append(f"{serial:<8} {nome:<32} {acertos:<9} {erros:<8} {em_branco:<11} {nota:.2f}")
    
    report_lines.append("\n" + "="*75)
    report_lines.append("              ESTATÍSTICAS DA TURMA POR QUESTÃO")
    report_lines.append("="*75)
    report_lines.append(f"{'QUESTÃO':<12} {'ACERTOS (CERTAS)':<20} {'ERROS (ERRADAS)':<20} {'EM BRANCO':<15}")
    report_lines.append("-" * 75)
    
    for q_num in sorted(stats_questoes.keys(), key=lambda x: int(x) if x.isdigit() else x):
        q_label = f"Questão {q_num}"
        if q_num in anuladas:
            q_label += " (ANULADA)"
            report_lines.append(f"{q_label:<12} {'--':<20} {'--':<20} {'--':<15}")
        else:
            c = stats_questoes[q_num]['certas']
            e = stats_questoes[q_num]['erradas']
            b = stats_questoes[q_num]['branco']
            report_lines.append(f"{q_label:<12} {c:<20} {e:<20} {b:<15}")
    
    report_text = "\n".join(report_lines)
    
    with open(PATHS['REPORT'], 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(report_text)
    print(f"\n[+] Relatório consolidado salvo em: {PATHS['REPORT']}\n")


#buscar aluno
def cmd_buscar(termo_busca):
    d = load_project(PATHS['PROJECT'])
    versions = d.get('VERSIONS', {})
    submits = d.get('SUBMITS', {})
    anuladas = d.get('ANULADAS', set())
    gabarito_atual = get_correct_answers(PATHS['QUESTS_DIR'])

    if not versions:
        print("Erro: nenhuma prova gerada ainda.")
        return

    termo_limpo = termo_busca.lower().strip()
    resultados = []

    for serial, v_info in sorted(versions.items()):
        nome = v_info['nome'].replace("\\_", "_")
        matricula = str(v_info['matricula']).strip()

        if termo_limpo in nome.lower() or termo_limpo in matricula.lower():
            mapa_quest = v_info['map']
            respostas_aluno = submits.get(serial, [])
            ordem_quest = v_info.get('order', sorted(mapa_quest.keys()))

            acertos = 0
            erros = 0
            em_branco = 0

            questoes_validas = [q for q in ordem_quest if q not in anuladas]
            total_validas = len(questoes_validas)

            if not respostas_aluno:
                resultados.append((serial, nome, matricula, "PENDENTE", "--", "--", "--", "--"))
                continue

            for idx, q_num in enumerate(ordem_quest):
                if q_num in anuladas:
                    continue

                if idx < len(respostas_aluno):
                    letra_marcada = respostas_aluno[idx]

                    if letra_marcada in ['x', '-']:
                        em_branco += 1
                    else:
                        id_marcado = mapa_quest[q_num].get(letra_marcada)
                        id_correto = gabarito_atual.get(q_num)

                        if id_marcado and id_marcado == id_correto:
                            acertos += 1
                        else:
                            erros += 1

            nota = (acertos/total_validas) * 10.0 if total_validas > 0 else 0.0 
            resultados.append((serial, nome, matricula, f"{nota:.2f}", acertos, erros, em_branco, total_validas))


    if not resultados:
        print(f'Nenhum aluno encontrado com o termo: {termo_busca}')
        return

    print("\n")   
    print("Resultado da busca de estudante.")
    print("\n")
    for res in resultados:
        serial, nome, matricula, nota, acertos, erros, em_branco, total = res
        print(f"Serial:     {serial}")
        print(f"Nome:       {nome}")
        print(f"Matrícula:  {matricula}")
        if nota == "PENDENTE":
            print("Status:  PENDENTE DE SUBMISSÃO")
        else:
            print(f"Nota:   {nota}/10.0")
            print(f"Desempenhos:{acertos} acerto(s), {erros} erro(s), {em_branco} em branco (Total válido: {total})")
            print("\n")
        print("\n")



#menu
def cmd_ajuda():
    manual = """

    GERENCIADOR DE PROVAS - MANUAL 
 
    Uso: python shc.py --<comando> [argumentos]

    Comandos disponíveis:
        criar <n>               Cria a estrutura do exame com <n> questões modelo.
        testar <q>              Gera um LaTeX/PDF isolado para validar a sintaxe da questão <q>.
        prova [qtd]             Lê os alunos e questões, gera as provas embaralhadas (.tex/.pdf) e salva o mapeamento no project.comp. Se não houver students.txt, gera prova(s) genérica(s).
        submeter <serial> <res> Registra o cartão de respostas para o serial da prova (ex: 01 abcde).
        status                  Exibe o painel de submissões e o progresso da turma.
        resubmeter <q>          Anula ou reativa a questão <q> para o cálculo das notas.
        relatório               Calcula as notas finais, exibe o relatório da turma e salva o report.txt.
        ajuda, --help           Exibe este manual de instruções."""

    print(manual)



#interface 
if __name__ == "__main__":
    if len(sys.argv) < 2:
        cmd_ajuda()
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd in ["--criar"]:
        if len(sys.argv) < 3:
            print("Informe a quantidade de questões. Exemplo: python3 shc_3_0.py --criar 4")
        else:
            try:
                qtd = int(sys.argv[2])
                if qtd <= 0:
                    print("Erro: O número de questões deve ser maior que zero.")
                else:
                    cmd_criar(qtd)
            except ValueError:
                print("Erro: Digite um número inteiro para a quantidade de questões.")


    elif cmd in ["--testar"]:
        if len(sys.argv) < 3:
            print("Erro: Informe a questão que deseja testar. Exemplo: python 3 shc_3_0.p y --testar 1")
        else:
            cmd_testar(sys.argv[2])

    elif cmd in ["--prova"]:
        if len(sys.argv) >= 3 and sys.argv[2].isdigit():
            cmd_provas(int(sys.argv[2]))
        else:
            cmd_provas()

    elif cmd in ["--submeter"]:
        if len(sys.argv) < 4:
            print("Erro: Forneça o serial e as respostas. Exemplo: python3 shc_3_0.py --submeter 01 abcdx")
        else:
            respostas_brutas = "".join(sys.argv[3:])
            cmd_submeter(sys.argv[2], respostas_brutas)

    elif cmd in ["--status"]:
        cmd_status()
    elif cmd in ["--resubmeter"]:
        if len(sys.argv) < 3:
            print("Erro: informe a questão a ser anulada. Exemplo: python3 shc_3_0.py --resubmeter 1")
        else:
            cmd_ressubmissao(sys.argv[2])

    elif cmd in ["--relatório"]:
        cmd_relatar()

    elif cmd in["--buscar"]:
        if len(sys.argv) < 3:
            print("Erro: informe o termo de busca. Exemplo: python3 shc_3_0.py --buscar")
        else:
            termo = " ".join(sys.argv[2:])
            cmd_buscar(termo)

    elif cmd in ["--ajuda"]:
        cmd_ajuda()
        
    else:
        print(f"Comando '{cmd}' não é reconhecido")
        cmd_ajuda()
        sys.exit(1)