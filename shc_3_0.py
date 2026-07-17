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
    'STUDENTS': './students.txt'
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

# =====================================================================
# NOVO COMANDO: --create (Cria a pasta, head, tail e modelos de questões)
# =====================================================================
def cmd_create():
    # 1. Garante a existência da pasta quests/ silenciosamente
    if not os.path.exists(PATHS['QUESTS_DIR']):
        os.makedirs(PATHS['QUESTS_DIR'])

    # 2. Pergunta a quantidade de forma direta
    while True:
        try:
            num_questoes = int(input("Quantas questões você deseja para esta prova? "))
            if num_questoes > 0:
                break
            print("[-] Digite um número maior que zero.")
        except ValueError:
            print("[-] Digite apenas números inteiros.")

    # 3. Cria head.txt e tail.txt silenciosamente se não existirem
    head_path = os.path.join(PATHS['QUESTS_DIR'], "head.txt")
    if not os.path.exists(head_path):
        with open(head_path, 'w', encoding='utf-8') as f:
            f.write("\\begin{flushleft}\n")
            f.write("Universidade Federal do Ceará\\\\\n")
            f.write("Campus de Quixadá\\\\\n")
            f.write("Professor Ricardo Reis\\\\\n")
            f.write("Álgebra Linear - 2024.2\\\\\n")
            f.write("\\end{flushleft}\n")

    tail_path = os.path.join(PATHS['QUESTS_DIR'], "tail.txt")
    if not os.path.exists(tail_path):
        with open(tail_path, 'w', encoding='utf-8') as f:
            f.write("% Rodapé LaTeX\n\\vspace{0.5cm}\\centerline{\\textbf{Fim da Prova!}}\n\\end{document}\n")

    # 4. Conta quantas questões JÁ EXISTEM fisicamente na pasta
    existentes = sorted([f for f in os.listdir(PATHS['QUESTS_DIR']) if f.startswith("quest") and f.endswith(".txt")])
    qtd_existente = len(existentes)

    # 5. Aplica a lógica inteligente de incremento e gera a mensagem curta
    if qtd_existente > 0:
        if num_questoes > qtd_existente:
            adicionais = num_questoes - qtd_existente
            print(f"[*] {qtd_existente} questões existentes. Adicionando mais {adicionais}.")
        else:
            print(f"[*] {qtd_existente} questões existentes. Nenhuma questão nova adicionada.")
    else:
        print(f"[+] Criando {num_questoes} novas questões.")

    # 6. Cria apenas os arquivos que estão faltando (sem sobrescrever nada!)
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
    d = load_project(PATHS['PROJECT'])
    
    if not os.path.exists(PATHS['STUDENTS']):
        print(f"[-] Erro: Arquivo de estudantes ausente em: {PATHS['STUDENTS']}")
        return
        
    students = []
    with open(PATHS['STUDENTS'], 'r', encoding='utf-8') as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue
            if '\t' in line_str:
                partes = line_str.split('\t', 1)
            else:
                partes = line_str.split(None, 1)
            
            if len(partes) >= 2:
                matricula = partes[0].strip()
                nome = partes[1].strip().replace("_", "\\_")
                students.append([matricula, nome])
            else:
                students.append([partes[0].strip(), "Estudante Sem Nome"])

    head_path = os.path.join(PATHS['QUESTS_DIR'], "head.txt")
    tail_path = os.path.join(PATHS['QUESTS_DIR'], "tail.txt")
    
    if not os.path.exists(head_path) or not os.path.exists(tail_path):
        print("[-] Erro crítico: Arquivos 'head.txt' ou 'tail.txt' ausentes na pasta 'quests/'.")
        return

    with open(head_path, 'r', encoding='utf-8') as f:
        head_content = f.read()
    with open(tail_path, 'r', encoding='utf-8') as f:
        tail_content = f.read()

    q_files = sorted([f for f in os.listdir(PATHS['QUESTS_DIR']) if f.startswith("quest") and f.endswith(".txt")])
    if not q_files:
        print("[-] Erro: Nenhuma questão encontrada na pasta 'quests/'.")
        return

    # PREÂMBULO LIMPO: Força a numeração das questões para Arábico (1, 2, 3...)
    # e das alternativas para Letras minúsculas (a, b, c...) sem herdar estilos
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
    
    for idx, student in enumerate(students):
        matricula = student[0]
        nome = student[1]
        serial = f"{idx+1:02d}"
        
        # Cabeçalho da Prova individual
        tex_output += f"\\noindent\\textbf{{SERIAL DA PROVA: {serial}}} \\hfill \\textbf{{Álgebra Linear}}\\\\\n"
        tex_output += "\\rule{\\linewidth}{0.2mm}\\\\\n" 
        tex_output += head_content + "\n"
        
        # Lista de questões isolada por aluno (garante numeração sempre arábica 1, 2, 3)
        tex_output += " \\begin{enumerate}[label=\\arabic*., ref=\\arabic*]\n"
        version_map = {}
        
        for q_file in q_files:
            q_num = q_file.replace("quest", "").replace(".txt", "")
            q_data = parse_question_file(PATHS['QUESTS_DIR'], q_file)
            
            if not q_data:
                continue
                
            tex_output += f"    \\item {q_data['enunciado']}\n"
            # Lista de alternativas isolada (garante alternativas sempre a, b, c, d, e)
            tex_output += "    \\begin{enumerate}[label=\\alph*)]\n"
            
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
            
        d['VERSIONS'][serial] = {
            'nome': nome,
            'matricula': matricula,
            'map': version_map
        }
        
        tex_output += " \\end{enumerate}\n"
        
        # Identificação e tabela de gabarito para preenchimento no rodapé
        tex_output += "\n\\vspace{0.3cm}\n"
        tex_output += f"\\noindent Matrícula: {matricula}\\\\ Nome: {nome} \\\\ Serial da Prova: \\textbf{{{serial}}}\\\\\n"
        tex_output += "\\begin{tabular}{|" + "|".join(["l"] * len(q_files)) + "|}\\hline\n"
        tex_output += "  &  ".join([f"{i+1:02d}" for i in range(len(q_files))]) + " \\\\ \\hline \n"
        tex_output += "  &  ".join([" " * len(q_files)]) + " \\\\ \\hline \n"
        tex_output += "\\end{tabular}\n\n"
        
        # ADICIONA O FIM DA PROVA (tail.txt) INDIVIDUALMENTE AQUI!
        # Removendo marcas que possam fechar o documento prematuramente
        tail_clean = tail_content.replace("\\end{document}", "")
        tex_output += tail_clean + "\n"
        
        # Força quebra de página de forma limpa para o próximo aluno
        tex_output += "\\clearpage\n\n"

    # Encerra o documento LaTeX global
    tex_output += "\\end{document}\n"
    
    with open(PATHS['PROVAS'], 'w', encoding='utf-8') as f:
        f.write(tex_output)
        
    save_project(PATHS['PROJECT'], d)
    print(f"[+] Provas LaTeX geradas em: {PATHS['PROVAS']}")
    
    print("[*] Compilando PDF...")
    result = subprocess.run(["pdflatex", "-interaction=nonstopmode", PATHS['PROVAS']], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if result.returncode == 0:
        print("[+] PDF compilado com sucesso em: ./provas.pdf")
    else:
        print("[-] Erro ao compilar o PDF! O LaTeX encontrou erros de sintaxe.")
        print("    Você pode verificar os erros detalhados abrindo o arquivo './provas.log'")

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
    
    report_txt = "RELATÓRIO DE NOTAS DA TURMA\n" + "="*40 + "\n"
    
    for serial, v_info in sorted(d.get('VERSIONS', {}).items()):
        nome = v_info['nome']
        mapa_questoes = v_info['map']
        respostas_aluno = d.get('SUBMITS', {}).get(serial, [])
        
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