#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import os
import pickle
import random
import subprocess

# Caminhos simplificados e centralizados
PATHS = {
    'QUESTS_DIR': './quests',
    'PROJECT': './project.comp',
    'PROVAS': './provas.tex',
    'REPORT': './report.txt',
    'STUDENTS': './students.txt',
    'HEAD': './quests/head.txt',
    'TAIL': './quests/tail.txt'
}

def load_project(path): 
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
    return {}

def save_project(path, data): 
    with open(path, 'wb') as f:
        pickle.dump(data, f) 

def load_text_file(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def save_text_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def load_students(path):
    students = []
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        students.append((parts[0], parts[1]))
    return students

def parse_question_file(quests_dir, filename):
    path = os.path.join(quests_dir, filename)
    if not os.path.exists(path):
        return None

    enunciado = ""
    items = {}
    
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
                item_id = int(meta[0].strip())
                texto = line_str[end_bracket+1:].strip()
                items[item_id] = texto
            
    return {"enunciado": enunciado, "items": items}

def load_all_questions(quests_dir):
    all_quests = {}
    if not os.path.exists(quests_dir):
        return all_quests
    for file in sorted(os.listdir(quests_dir)):
        if file.startswith("quest") and file.endswith(".txt"):
            try:
                q_num = int(file.replace("quest", "").replace(".txt", ""))
                q_data = parse_question_file(quests_dir, file)
                if q_data and q_data["enunciado"]:
                    all_quests[q_num] = q_data
            except ValueError:
                continue
    return all_quests

def get_correct_answers(quests_dir):
    gabarito_real = {}
    if not os.path.exists(quests_dir):
        return gabarito_real
        
    for file in os.listdir(quests_dir):
        if file.startswith("quest") and file.endswith(".txt"):
            try:
                q_num = int(file.replace("quest", "").replace(".txt", ""))
                path = os.path.join(quests_dir, file)
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line_str = line.strip()
                        if line_str.startswith("\\item"):
                            sb = line_str.find("{")
                            eb = line_str.find("}")
                            if sb != -1 and eb != -1:
                                meta = line_str[sb+1:eb].split(",")
                                item_id = int(meta[0].strip())
                                status = meta[1].strip()
                                if status == 'c':
                                    gabarito_real[q_num] = item_id
            except ValueError:
                continue
    return gabarito_real

def compile_latex(tex_path):
    if not os.path.exists(tex_path):
        return
    print("[*] Compilando o arquivo LaTeX...")
    try:
        subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[+] PDF gerado com sucesso!")
    except FileNotFoundError:
        print("[-] Aviso: 'pdflatex' não encontrado. O arquivo .tex foi gerado, mas não pôde ser compilado.")

# =====================================================================
# COMANDOS DO SISTEMA
# =====================================================================
def cmd_create():
    if not os.path.exists(PATHS['QUESTS_DIR']):
        os.makedirs(PATHS['QUESTS_DIR'])

    while True:
        try:
            num_questoes = int(input("Quantas questões você deseja para esta prova? "))
            if num_questoes > 0:
                break
            print("[-] Digite um número maior que zero.")
        except ValueError:
            print("[-] Digite apenas números inteiros.")

    head_path = PATHS['HEAD']
    if not os.path.exists(head_path):
        with open(head_path, 'w', encoding='utf-8') as f:
            f.write("\\documentclass[12pt]{article}\n\\usepackage[utf8]{inputenc}\n\\usepackage[brazil]{babel}\n\\usepackage{enumitem}\n\\usepackage{amsfonts}\n\\usepackage{amssymb}\n\\newcommand{\\quest}{\\vspace{0.3cm}\\item}\n\\begin{document}\n")
            f.write("\\begin{flushleft}\n")
            f.write("Universidade Federal do Ceará\\\\\n")
            f.write("Campus de Quixadá\\\\\n")
            f.write("Professor Ricardo Reis\\\\\n")
            f.write("Álgebra Linear\\\\\n")
            f.write("Nome: {{NOME}}\\\\\n")
            f.write("Matrícula: {{MATRICULA}}\\\\\n")
            f.write("SERIAL DA PROVA: {{SERIAL}}\\\\\n")
            f.write("\\end{flushleft}\n")
            f.write("\\begin{enumerate}\n")

    tail_path = PATHS['TAIL']
    if not os.path.exists(tail_path):
        with open(tail_path, 'w', encoding='utf-8') as f:
            f.write("\\end{enumerate}\n\\vspace{0.5cm}\\centerline{\\textbf{Fim da Prova!}}\n\\end{document}\n")

    existentes = sorted([f for f in os.listdir(PATHS['QUESTS_DIR']) if f.startswith("quest") and f.endswith(".txt")])
    qtd_existente = len(existentes)

    if qtd_existente > 0:
        if num_questoes > qtd_existente:
            adicionais = num_questoes - qtd_existente
            print(f"[*] {qtd_existente} questões existentes. Adicionando mais {adicionais}.")
        else:
            print(f"[*] {qtd_existente} questões existentes. Nenhuma questão nova adicionada.")
    else:
        print(f"[+] Criando {num_questoes} novas questões.")

    for i in range(1, num_questoes + 1):
        q_filename = f"quest{i:02d}.txt"
        q_path = os.path.join(PATHS['QUESTS_DIR'], q_filename)
        
        if not os.path.exists(q_path):
            with open(q_path, 'w', encoding='utf-8') as f:
                f.write(f"%% -- QUESTÃO {i:02d} --\n\n")
                f.write(f"\\quest Escreva aqui o enunciado da Questão {i:02d}.\n\n")
                f.write(f"\\item{{1, c}} Primeira alternativa da Questão {i:02d} (Gabarito)\n")
                f.write(f"\\item{{2, e}} Segunda alternativa da Questão {i:02d}\n")
                f.write(f"\\item{{3, e}} Terceira alternativa da Questão {i:02d}\n")
                f.write(f"\\item{{4, e}} Quarta alternativa da Questão {i:02d}\n")
                f.write(f"\\item{{5, e}} Quinta alternativa da Questão {i:02d}\n")

    print("[+] Concluído com sucesso!")

def cmd_exams():
    students = load_students(PATHS['STUDENTS'])
    if not students:
        print(f"[-] Erro: O arquivo {PATHS['STUDENTS']} está vazio ou não existe.")
        return

    head = load_text_file(PATHS['HEAD'])
    tail = load_text_file(PATHS['TAIL'])
    all_quests = load_all_questions(PATHS['QUESTS_DIR']) 
    
    if not all_quests:
        print("[-] Erro: Nenhuma questão válida encontrada na pasta 'quests'.")
        return

    project_data = {
        'VERSIONS': {},
        'SUBMITS': {}
    }
    
    tex_content = ""
    
    for matricula, nome in students:
        serial = f"{len(project_data['VERSIONS']) + 1:02d}"
        
        # 1. EMBARALHAMENTO SIMULTÂNEO DAS QUESTÕES
        q_numbers = list(all_quests.keys())
        random.shuffle(q_numbers)
        
        version_map = {}
        student_tex = f"% --- SERIAL DA PROVA: {serial} ---\n"
        student_tex += head.replace("{{NOME}}", nome).replace("{{MATRICULA}}", matricula).replace("{{SERIAL}}", serial)
        
        for visual_idx, q_num in enumerate(q_numbers, start=1):
            q_data = all_quests[q_num]
            student_tex += f"\n\\quest {q_data['enunciado']}\n\\begin{{enumerate}}[label=\\alph*)]\n"
            
            # 2. EMBARALHAMENTO SIMULTÂNEO DOS ITENS
            item_ids = list(q_data['items'].keys())
            random.shuffle(item_ids)
            
            letters = ['a', 'b', 'c', 'd', 'e']
            question_map = {}
            
            for idx, item_id in enumerate(item_ids):
                if idx >= len(letters): 
                    break
                letra = letters[idx]
                texto_alternativa = q_data['items'][item_id]
                
                student_tex += f"    \\item {texto_alternativa}\n"
                question_map[letra] = item_id
            
            student_tex += "\\end{enumerate}\n"
            version_map[q_num] = question_map
            
        student_tex += f"\n{tail}\n\\newpage\n"
        tex_content += student_tex
        
        project_data['VERSIONS'][serial] = {
            'nome': nome,
            'matricula': matricula,
            'map': version_map
        }
        
    save_text_file(PATHS['PROVAS'], tex_content)
    save_project(PATHS['PROJECT'], project_data)
    
    compile_latex(PATHS['PROVAS'])
    print(f"[+] Provas geradas com embaralhamento duplo simultâneo para {len(students)} alunos!")

def cmd_submit(serial, respostas_str):
    d = load_project(PATHS['PROJECT'])
    if 'SUBMITS' not in d:
        d['SUBMITS'] = {}
    if serial not in d.get('VERSIONS', {}):
        print(f"[-] Erro: O Serial {serial} não existe no projeto atual.")
        return
        
    d['SUBMITS'][serial] = list(respostas_str.lower().strip())
    save_project(PATHS['PROJECT'], d)
    print(f"[+] Respostas do Serial {serial} salvas!")

def cmd_report():
    d = load_project(PATHS['PROJECT'])
    gabarito_atual = get_correct_answers(PATHS['QUESTS_DIR'])
    
    report_txt = "RELATÓRIO DE NOTAS DA TURMA\n" + "="*30 + "\n"
    
    for serial, v_info in sorted(d.get('VERSIONS', {}).items()):
        nome = v_info['nome']
        mapa_questoes = v_info['map']
        respostas_aluno = d.get('SUBMITS', {}).get(serial, [])
        
        acertos = 0
        total_questoes = len(mapa_questoes)
        
        # O laço itera sobre a ordem real do banco de dados das questões
        for idx, q_num in enumerate(sorted(mapa_questoes.keys())):
            if idx < len(respostas_aluno):
                letra_marcada = respostas_aluno[idx]
                id_marcado = mapa_questoes[q_num].get(letra_marcada)
                id_correto = gabarito_atual.get(q_num)
                
                if id_marcado and id_marcado == id_correto:
                    acertos += 1
                    
        nota = (acertos / total_questoes) * 10.0 if total_questoes > 0 else 0.0
        # Saída limpa e perfeitamente amigável para o leitor de telas Orca
        report_txt += f"Serial {serial}: {nome} - Nota: {nota:.2f}\n"

    with open(PATHS['REPORT'], 'w', encoding='utf-8') as f:
        f.write(report_txt)
        
    print(report_txt)
    print(f"[+] Relatório salvo em: {PATHS['REPORT']}")

def show_help():
    print("\n   SISTEMA DE PROVAS EMBARALHADAS SIMPLIFICADO")
    print("   ==========================================")
    print("   Uso:")
    print("     python3 shc_3_0.py --create         (Cria a pasta 'quests' e os arquivos vazios)")
    print("     python3 shc_3_0.py --exams          (Gera provas.tex e provas.pdf)")
    print("     python3 shc_3_0.py --submit <S> <R> (Submete respostas. Ex: --submit 01 ab)")
    print("     python3 shc_3_0.py --report         (Gera relatório de notas)")
    print("\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
        
    cmd = sys.argv[1]
    
    if cmd == "--create":
        cmd_create()
    elif cmd == "--exams":
        cmd_exams()
    elif cmd == "--submit":
        if len(sys.argv) < 4:
            print("[-] Erro: Forneça o serial e as respostas. Exemplo: python3 shc_3_0.py --submit 01 abc")
        else:
            cmd_submit(sys.argv[2], sys.argv[3])
    elif cmd == "--report":
        cmd_report()
    else:
        show_help()