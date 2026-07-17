#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import os
import pickle
import random
import subprocess

def get_project_paths(class_name):
    """Retorna os caminhos dos arquivos e pastas isolados 100% por turma."""
    base_dir = os.path.join(".", class_name)
    quests_dir = os.path.join(base_dir, "quests") # Agora a pasta quests fica DENTRO da turma!
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    if not os.path.exists(quests_dir):
        os.makedirs(quests_dir)

    return {
        'DIR': base_dir,
        'QUESTS_DIR': quests_dir,
        'PROJECT': os.path.join(base_dir, "project.comp"),
        'PROVAS': os.path.join(base_dir, "provas.tex"),
        'REPORT': os.path.join(base_dir, "report.txt"),
        'REPORT_TEX': os.path.join(base_dir, "report_notas.tex"),
        'STUDENTS': os.path.join(base_dir, "students.txt")
    }   

def load_project(path): 
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
    return {}

def save_project(path, data): 
    with open(path, 'wb') as f:
        pickle.dump(data, f) 

def parse_question_file(quests_dir, filename):
    """Lê uma questão de dentro da pasta quests específica da turma."""
    path = os.path.join(quests_dir, filename)
    if not os.path.exists(path):
        return None

    enunciado = ""
    alternativas = []
    
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line_str = line.strip()
        if line_str.startswith("%%") or not line_str:
            continue
        if line_str.startswith("\\quest"):
            enunciado = line_str.replace("\\quest", "").strip()
        elif line_str.startswith("\\item"):
            start_bracket = line_str.find("{")
            end_bracket = line_str.find("}")
            if start_bracket != -1 and end_bracket != -1:
                meta = line_str[start_bracket+1:end_bracket].split(",")
                item_id = meta[0].strip()
                status = meta[1].strip()
                texto = line_str[end_bracket+1:].strip()
                alternativas.append((item_id, status, texto))
            
    return {"enunciado": enunciado, "alternativas": alternativas}

def get_correct_answers(quests_dir):
    """Extrai o gabarito dinamicamente baseado nas questões da turma."""
    gabarito_real = {}
    if not os.path.exists(quests_dir):
        return gabarito_real
        
    for file in os.listdir(quests_dir):
        if file.startswith("quest") and file.endswith(".txt"):
            q_num = file.replace("quest", "").replace(".txt", "")
            q_data = parse_question_file(quests_dir, file)
            if q_data:
                for item_id, status, _ in q_data["alternativas"]:
                    if status == 'c':
                        gabarito_real[q_num] = item_id
    return gabarito_real

# ==========================================
# FUNÇÃO DE AJUDA
# ==========================================
def show_help():
    print("\n")
    print("      SISTEMA GERADOR DE PROVAS EMBARALHADAS (SHC)")
    print("\n")
    print("Uso via Linha de Comando (Direto para Turma Específica):")
    print("  python3 shc_2_2.py <NOME_DA_TURMA> --<comando> [argumentos]")
    print("\nUso via Assistente:")
    print("  python3 shc_2_2.py --create")
    print("  python3 shc_2_2.py --edit")
    print("\nComandos disponíveis:")
    print("  --create   Cria uma nova turma isolada pedindo o nome no terminal.")
    print("  --edit     Edita as questões/cabeçalho de uma turma selecionada.")
    print("  --exams    Gera as provas embaralhadas em LaTeX e PDF daquela turma.")
    print("  --submit   Registra as respostas de um estudante em uma turma.")
    print("  --report   Processa as notas e gera o relatório daquela turma.")
    print("\n")

# =====================================================================
# AUXILIARES DE ENTRADA DE DADOS
# =====================================================================

def configurar_questoes(quests_dir):
    print("\n--- CONFIGURAÇÃO DE QUESTÕES ---")
    while True:
        try:
            num_questoes = int(input("Quantas questões você deseja criar/adicionar? "))
            break  # Sai do laço se for um número válido
        except ValueError:
            print("[-] Erro: Por favor, digite um número inteiro válido para a quantidade de questões.")

    for i in range(1, num_questoes + 1):
        idx = 1
        while os.path.exists(os.path.join(quests_dir, f"quest{idx:02d}.txt")):
            idx += 1
            
        q_filename = f"quest{idx:02d}.txt"
        q_path = os.path.join(quests_dir, q_filename)
            
        print(f"\n>> Configurando a QUESTÃO {idx:02d}:")
        enunciado = input("Digite o enunciado da questão: ")
        
        # Correção aqui: validação para a quantidade de alternativas
        while True:
            try:
                num_itens = int(input("Quantas alternativas essa questão terá? "))
                if num_itens <= 0:
                    print("[-] Erro: A questão deve ter pelo menos 1 alternativa.")
                    continue
                break  # Sai do laço se for um número válido
            except ValueError:
                print("[-] Erro: Entrada inválida! Digite apenas números para a quantidade de alternativas.")
            
        alternativas_coletadas = []
        gabarito_definido = False
        
        for j in range(1, num_itens + 1):
            texto_alt = input(f"   Texto da alternativa {j}: ")
            
            while True:
                is_correct = input(f"   Esta é a alternativa CORRETA? (s/n): ").strip().lower()
                if is_correct in ['s', 'n']:
                    break
                print("[-] Responda apenas com 's' ou 'n'.")
            
            if is_correct == 's' and not gabarito_definido:
                status = 'c'
                gabarito_definido = True
            else:
                status = 'e'
                
            alternativas_coletadas.append((j, status, texto_alt))
            
        if not gabarito_definido:
            print("[!] Nenhuma marcada correta. Definindo a primeira como gabarito.")
            alternativas_coletadas[0] = (1, 'c', alternativas_coletadas[0][2])

        with open(q_path, 'w', encoding='utf-8') as f:
            f.write(f"%% -- QUESTÃO {idx} --\n\n")
            f.write(f"\\quest {enunciado}\n\n")
            for item_id, status, texto in alternativas_coletadas:
                f.write(f"\\item{{{item_id}, {status}}} {texto}\n")
                
        print(f"[+] Arquivo '{q_filename}' gerado com sucesso!")

        

def configurar_cabecalho(quests_dir, forcar=False):
    head_path = os.path.join(quests_dir, "head.txt")
    if not os.path.exists(head_path) or forcar:
        print("\n--- CONFIGURAÇÃO DO CABEÇALHO DA PROVA ---")
        universidade = input("Nome da Universidade: ")
        campus = input("Nome do Campus: ")
        professor = input("Nome do Professor: ")
        disciplina = input("Disciplina e Semestre: ")
        
        with open(head_path, 'w', encoding='utf-8') as f:
            f.write("\\begin{flushleft}\n")
            f.write(f"{universidade}\\\\\n")
            f.write(f"{campus}\\\\\n")
            f.write(f"{professor}\\\\\n")
            f.write(f"{disciplina}\\\\\n")
            f.write("\\end{flushleft}\n")
        print("[*] Arquivo 'head.txt' configurado.")

# =====================================================================
# NUCLEO DE COMANDOS: --create E --edit
# =====================================================================

def cmd_create(nome_turma_predefinido=None):
    if nome_turma_predefinido:
        nome_turma = nome_turma_predefinido
    else:
        print("\n--- INICIALIZANDO NOVA TURMA ---")
        nome_turma = input("Digite o nome da turma que deseja criar: ").strip().replace(" ", "_")
        if not nome_turma:
            print("[-] Nome inválido. Operação abortada.")
            return

    paths = get_project_paths(nome_turma)
    print(f"\n[+] Tudo será salvo isoladamente na pasta: '{paths['DIR']}'")

    tail_path = os.path.join(paths['QUESTS_DIR'], "tail.txt")
    if not os.path.exists(tail_path):
        with open(tail_path, 'w', encoding='utf-8') as f:
            f.write("\\end{document}\n")

    configurar_cabecalho(paths['QUESTS_DIR'], forcar=False)
    configurar_questoes(paths['QUESTS_DIR'])

    if not os.path.exists(paths['STUDENTS']):
        with open(paths['STUDENTS'], 'w', encoding='utf-8') as f:
            f.write("40028922 \tCRIS\n")

    d = {'VERSIONS': {}, 'SUBMITS': {}}
    save_project(paths['PROJECT'], d)
    print(f"\n[+] Sucesso! A turma '{nome_turma}' foi isolada com sucesso.")


def cmd_edit(nome_turma_predefinido=None):
    if nome_turma_predefinido:
        nome_turma = nome_turma_predefinido
    else:
        print("\n--- MODO EDIÇÃO ---")
        pastas_projeto = [d for d in os.listdir('.') if os.path.isdir(d) and os.path.exists(os.path.join(d, "project.comp"))]
        
        if not pastas_projeto:
            print("[-] Nenhuma turma localizada. Use o comando --create primeiro.")
            return
            
        print("[*] Selecione qual turma deseja EDITAR:")
        for idx, p in enumerate(pastas_projeto, 1):
            print(f"  [{idx}] {p}")
            
        try:
            escolha = int(input("\nDigite o número correspondente: "))
            nome_turma = pastas_projeto[escolha - 1]
        except (ValueError, IndexError):
            print("[-] Opção inválida.")
            return

    paths = get_project_paths(nome_turma)
    print(f"\n[+] Modificando a turma específica: '{nome_turma}'")

    print("\nO que deseja fazer?")
    print(" [1] Adicionar novas questões para esta turma")
    print(" [2] Atualizar o cabeçalho desta turma")
    print(" [3] Ver arquivo de estudantes")
    sub_opcao = input("Escolha (1-3): ").strip()
    
    if sub_opcao == '1':
        configurar_questoes(paths['QUESTS_DIR'])
    elif sub_opcao == '2':
        configurar_cabecalho(paths['QUESTS_DIR'], forcar=True)
    elif sub_opcao == '3':
        print(f"\n[*] Edite o arquivo físico: -> {os.path.abspath(paths['STUDENTS'])}")
        return

    d = load_project(paths['PROJECT'])
    save_project(paths['PROJECT'], d)
    print(f"\n[+] Alterações salvas na pasta da turma '{nome_turma}'.")

# ==========================================
# EXAMS, SUBMIT, REPORT (TOTALMENTE ISOLADOS)
# ==========================================

def cmd_exams(paths):
    d = load_project(paths['PROJECT'])
    if not os.path.exists(paths['STUDENTS']):
        print(f"[-] Erro: 'students.txt' ausente em {paths['STUDENTS']}")
        return
        
    students = []
    if os.path.exists(paths['STUDENTS']):
        with open(paths['STUDENTS'], 'r', encoding='utf-8') as f:
            for line in f:
                line_str = line.strip()
                if not line_str:
                    continue
                # Se houver tabulação, divide por ela; senão, tenta dividir por espaços
                if '\t' in line_str:
                    partes = line_str.split('\t', 1)
                else:
                    partes = line_str.split(None, 1) # Divide por qualquer quantidade de espaços em branco
                
                if len(partes) >= 2:
                    students.append([partes[0].strip(), partes[1].strip()])
                else:
                    # Se não achar separador, assume que é só o nome ou matrícula
                    students.append([partes[0].strip(), "Estudante Sem Nome"])

    try:
        with open(os.path.join(paths['QUESTS_DIR'], "head.txt"), 'r', encoding='utf-8') as f:
            head_content = f.read()
        with open(os.path.join(paths['QUESTS_DIR'], "tail.txt"), 'r', encoding='utf-8') as f:
            tail_content = f.read()
    except FileNotFoundError:
        print("[-] Erro crítico: Adicione cabeçalhos na pasta da turma antes.")
        return

    q_files = sorted([f for f in os.listdir(paths['QUESTS_DIR']) if f.startswith("quest") and f.endswith(".txt")])
    if not q_files:
        print("[-] Erro: Nenhuma questão encontrada nesta turma.")
        return

    tex_output = """\\documentclass[10pt,a4paper,twocolumn]{report}
\\usepackage[utf8]{inputenc}
\\usepackage[portuguese,brazilian]{babel}
\\usepackage{amsmath}
\\usepackage{amsfonts}
\\usepackage{amssymb}
\\usepackage{enumerate}
\\usepackage{anysize}
\\usepackage{fancyhdr}
\\setlength{\\headheight}{12.18494pt}
\\marginsize{0.5cm}{0.5cm}{0cm}{0cm}
\\pagestyle{fancy}
\\begin{document}
"""
    tex_output += head_content + "\n"
    letras = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    
    for idx, student in enumerate(students):
        matricula = student[0].strip()
        nome = student[1].strip()
        serial = f"{idx+1:02d}"
        
        tex_output += f"\\lhead{{{serial}}} \n \\begin{{enumerate}} \n"
        version_map = {}
        
        for q_file in q_files:
            q_num = q_file.replace("quest", "").replace(".txt", "")
            q_data = parse_question_file(paths['QUESTS_DIR'], q_file)
            
            tex_output += f"    \\item {q_data['enunciado']}\n    \\begin{{enumerate}}\n"
            
            alts = list(q_data['alternativas'])
            random.shuffle(alts)
            
            student_q_map = {}
            for l_idx, alt in enumerate(alts):
                letra = letras[l_idx]
                item_id = alt[0]
                tex_output += f"\\item {alt[2]}\n"
                student_q_map[letra] = item_id 
                
            tex_output += "    \\end{enumerate} \n"
            version_map[q_num] = student_q_map
            
        d['VERSIONS'][serial] = {
            'nome': nome,
            'matricula': matricula,
            'map': version_map
        }
        
        tex_output += f"Matrícula: {matricula}\\\\ Nome: {nome} \\\\ Serial: {serial}\\\\\n"
        tex_output += "\\begin{tabular}{|" + "|".join(["l"] * len(q_files)) + "|}\\hline\n"
        tex_output += "  &  ".join([f"{i+1:02d}" for i in range(len(q_files))]) + " \\\\ \\hline \n"
        tex_output += "  &  ".join([" " * len(q_files)]) + " \\\\ \\hline \n"
        tex_output += "\\end{tabular}\n \\cleardoublepage \n\n"

    tex_output += tail_content
    
    with open(paths['PROVAS'], 'w', encoding='utf-8') as f:
        f.write(tex_output)
        
    save_project(paths['PROJECT'], d)
    print(f"[+] Provas LaTeX geradas em: {paths['PROVAS']}")
    
    try:
        subprocess.run(["pdflatex", "-output-directory", paths['DIR'], paths['PROVAS']], stdout=subprocess.DEVNULL)
        print(f"[+] PDF gerado com sucesso em: {paths['DIR']}/provas.pdf")
    except Exception:
        print("[-] Realize a compilação do .tex manualmente.")

def cmd_submit(paths, serial, respostas_str):
    d = load_project(paths['PROJECT'])
    if serial not in d.get('VERSIONS', {}):
        print(f"[-] Erro: O Serial {serial} não existe nesta turma.")
        return
        
    d['SUBMITS'][serial] = list(respostas_str.lower().strip())
    save_project(paths['PROJECT'], d)
    print(f"[+] Respostas do Serial {serial} salvas nesta turma!")

def cmd_report(paths):
    d = load_project(paths['PROJECT'])
    gabarito_atual = get_correct_answers(paths['QUESTS_DIR'])
    
    report_txt = "RELATÓRIO DE NOTAS DA TURMA\n" + "="*40 + "\n"
    
    for serial, v_info in sorted(d.get('VERSIONS', {}).items()):
        nome = v_info['nome']
        mapa_questoes = v_info['map']
        respostas_aluno = d['SUBMITS'].get(serial, [])
        
        acertos = 0
        total_questoes = len(mapa_questoes)
        
        for idx, q_num in enumerate(sorted(mapa_questoes.keys())):
            if idx < len(respostas_aluno):
                letra_marcada = respostas_aluno[idx]
                id_marcado = mapa_questoes[q_num].get(letra_marcada)
                id_correto = gabarito_atual.get(q_num)
                
                if id_marcado and id_marcado == id_correto:
                    acertos += 1
                    
        nota = (acertos / total_questoes) * 10.0 if total_questoes > 0 else 0.0
        report_txt += f"{serial} - {nome:<40} Nota: {nota:.2f}\n"

    with open(paths['REPORT'], 'w', encoding='utf-8') as f:
        f.write(report_txt)
        
    print(report_txt)
    print(f"[+] Relatório salvo em: {paths['REPORT']}")

# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == "--create":
            cmd_create()
            sys.exit(0)
        elif sys.argv[1] == "--edit":
            cmd_edit()
            sys.exit(0)

    if len(sys.argv) < 3:
        show_help()
        sys.exit(1)

    turma = sys.argv[1]
    cmd = sys.argv[2]
    
    paths = get_project_paths(turma)

    if cmd == "--create":
        cmd_create(nome_turma_predefinido=turma)
    elif cmd == "--edit":
        cmd_edit(nome_turma_predefinido=turma)
    elif cmd == "--exams":
        cmd_exams(paths)
    elif cmd == "--submit":
        if len(sys.argv) < 5:
            print("Erro: Forneça o serial e as respostas. Exemplo: python3 shc_2_2.py turma_a --submit 01 abc")
        else:
            cmd_submit(paths, sys.argv[3], sys.argv[4])
    elif cmd == "--report":
        cmd_report(paths)
    else:
        print("[-] Comando desconhecido.")
        show_help()