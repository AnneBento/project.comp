import curses
import os
import sys
import subprocess

# funções importadas do shc_ui.py
from shc_3_3 import (
    load_project,
    save_project,
    cmd_provas,
    cmd_submeter,
    cmd_recorrigir,
    cmd_relatorio_notas,
    cmd_relatorio_estatistico,
    calcular_nota_aluno,
    PATHS   
)


def popup_input(stdscr, title, prompt):
    """Exibe um pop-up centralizado para leitura de dados digitados."""
    h, w = stdscr.getmaxyx()
    window_h, window_w = 8, min(68, w - 4)
    start_y, start_x = (h - window_h) // 2, (w - window_w) // 2

    window = curses.newwin(window_h, window_w, start_y, start_x)
    window.keypad(True)
    window.box()

    try:
        window.addstr(1, 2, f"[ {title} ]", curses.A_BOLD)
        max_text_len = window_w - 4
        window.addstr(3, 2, prompt[:max_text_len])
    except curses.error:
        pass

    window.refresh()

    curses.echo()
    curses.curs_set(1)

    input_bytes = window.getstr(4, 2, max(1, window_w - 6))
    texto = input_bytes.decode('utf-8').strip()

    curses.noecho()
    curses.curs_set(0)
    return texto


def popup_msg(stdscr, title, linhas):
    """Exibe mensagens ou dados formatados dentro de um quadro isolado."""
    h, w = stdscr.getmaxyx()
    window_h = max(len(linhas) + 6, 8)
    window_w = min(68, w - 4)
    start_y, start_x = max(0, (h - window_h) // 2), max(0, (w - window_w) // 2)

    window = curses.newwin(window_h, window_w, start_y, start_x)
    window.keypad(True)
    window.box()

    try:
        window.addstr(1, 2, f"[ {title} ]", curses.A_BOLD)

        for idx, l in enumerate(linhas):
            if 3 + idx < window_h - 2:
                window.addstr(3 + idx, 2, str(l)[:window_w - 4])

        window.addstr(window_h - 2, 2, "Pressione qualquer tecla para continuar...")
    except curses.error:
        pass

    window.refresh()
    window.getch()


def popup_confirmar_submissao(stdscr, serial, nome, matricula, respostas, nota):
    """Prévia com botões [ SIM ] e [ NÃO ] navegáveis pelas setas."""
    h, w = stdscr.getmaxyx()
    window_h, window_w = 12, min(68, w - 4)
    start_y, start_x = (h - window_h) // 2, (w - window_w) // 2

    window = curses.newwin(window_h, window_w, start_y, start_x)
    window.keypad(True)
    window.box()

    max_l = window_w - 4
    opcao_selecionada = 0  # 0 = SIM, 1 = NÃO

    while True:
        try:
            window.erase()
            window.box()

            window.addstr(1, 2, "[ CONFIRMAÇÃO DE SUBMISSÃO ]", curses.A_BOLD)
            window.addstr(3, 2, f"Serial:     {serial}"[:max_l])
            window.addstr(4, 2, f"Aluno:      {nome}"[:max_l])
            window.addstr(5, 2, f"Matrícula:  {matricula}"[:max_l])
            window.addstr(6, 2, f"Respostas:  {respostas.upper()}"[:max_l])
            window.addstr(7, 2, f"Nota:       {nota:.1f}"[:max_l], curses.A_BOLD)

            # Botões selecionáveis
            btn_sim = "[ SIM - REGISTRAR ]"
            btn_nao = "[ NÃO - CANCELAR ]"

            if opcao_selecionada == 0:
                window.addstr(9, 4, f"> {btn_sim} <", curses.A_BOLD | curses.color_pair(1))
                window.addstr(9, 32, f"  {btn_nao}  ", curses.A_DIM)
            else:
                window.addstr(9, 4, f"  {btn_sim}  ", curses.A_DIM)
                window.addstr(9, 32, f"> {btn_nao} <", curses.A_BOLD | curses.color_pair(1))

        except curses.error:
            pass

        window.refresh()
        key = window.getch()

        if key in [curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN]:
            opcao_selecionada = 1 - opcao_selecionada
        elif key in [10, 13]:  # ENTER
            break

    return opcao_selecionada == 0


def popup_relatorio_opcao(stdscr, title, file_path):
    """Oferece botões [ SIM ] e [ NÃO ] navegáveis com as setas para abrir o relatório."""
    h, w = stdscr.getmaxyx()
    window_h, window_w = 10, min(68, w - 4)
    start_y, start_x = (h - window_h) // 2, (w - window_w) // 2

    window = curses.newwin(window_h, window_w, start_y, start_x)
    window.keypad(True)
    window.box()

    opcao_selecionada = 0  # 0 = SIM, 1 = NÃO

    while True:
        try:
            window.erase()
            window.box()

            window.addstr(1, 2, f"[ {title} ]", curses.A_BOLD)
            window.addstr(3, 2, "Relatório gerado com sucesso!")
            window.addstr(4, 2, "Deseja abrir o arquivo agora?")

            # Renderiza os botões
            btn_sim = "[ SIM ]"
            btn_nao = "[ NÃO ]"

            if opcao_selecionada == 0:
                window.addstr(6, 12, f"> {btn_sim} <", curses.A_BOLD | curses.color_pair(1))
                window.addstr(6, 32, f"  {btn_nao}  ", curses.A_DIM)
            else:
                window.addstr(6, 12, f"  {btn_sim}  ", curses.A_DIM)
                window.addstr(6, 32, f"> {btn_nao} <", curses.A_BOLD | curses.color_pair(1))

            window.addstr(8, 2, "Use as setas [←/→] e pressione [ENTER]", curses.A_DIM)
        except curses.error:
            pass

        window.refresh()
        key = window.getch()

        if key in [curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN]:
            opcao_selecionada = 1 - opcao_selecionada
        elif key in [10, 13]:  # ENTER
            break

    if opcao_selecionada == 0:
        caminho_absoluto = os.path.abspath(file_path)
        try:
            # Tenta abrir com o Bloco de Notas garantindo compatibilidade no Windows
            subprocess.Popen(['notepad.exe', caminho_absoluto])
        except Exception:
            try:
                # Fallback caso notepad não responda
                os.startfile(caminho_absoluto)
            except Exception as e:
                popup_msg(stdscr, "ERRO", [
                    f"Não foi possível abrir o relatório:",
                    f"{str(e)[:50]}"
                ])


# menu
def main_menu(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    opcoes = [
        "1. Gerar Provas (a partir de data.students)",
        "2. Submeter Respostas (Digitar Cartão)",
        "3. Ver Submissão e Nota por Serial",
        "4. Recorrigir Provas",
        "5. Gerar Relatório Geral de Notas",
        "6. Gerar Relatório Estatístico",
        "7. Sair"
    ]

    selecionado = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        titulo = "=== SISTEMA SHC - PAINEL INTERATIVO ==="
        try:
            stdscr.addstr(1, max(0, (w - len(titulo)) // 2), titulo[:w - 2], curses.A_BOLD)
            stdscr.addstr(2, 2, "Navegue [↑/↓], aperte NÚMEROS [1-7] para atalho ou [ENTER]."[:w - 4], curses.A_DIM)
            stdscr.addstr(3, 0, "-" * max(0, w - 1))
        except curses.error:
            pass

        d = load_project(PATHS['PROJECT'])
        qtd_provas = len(d.get('VERSIONS', {}))
        qtd_submits = len(d.get('SUBMITS', {}))

        max_len = max(10, w - 8)

        for idx, item in enumerate(opcoes):
            y = 5 + idx
            x = 4

            status = ""
            if idx == 0:
                status = f" ({qtd_provas} geradas)"
            elif idx in [1, 2]:
                status = f" ({qtd_submits}/{qtd_provas} submetidas)"

            label = f"{item}{status}"[:max_len - 2]

            try:
                if idx == selecionado:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y, x, f"> {label}")
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(y, x, f"  {label}")
            except curses.error:
                pass

        try:
            stdscr.addstr(h - 2, 2, "[Atalhos]: Teclas 1-7  |  [Setas]: Navegar  |  [Enter]: Executar"[:w - 4], curses.A_DIM)
        except curses.error:
            pass

        stdscr.refresh()

        key = stdscr.getch()

        # NAVEGAÇÃO COM SETAS
        if key == curses.KEY_UP:
            selecionado = (selecionado - 1) % len(opcoes)
        elif key == curses.KEY_DOWN:
            selecionado = (selecionado + 1) % len(opcoes)

        # ATALHOS NUMÉRICOS DIRETO (TECLAS '1' A '7')
        elif ord('1') <= key <= ord('7'):
            selecionado = key - ord('1')
            key = 10  # Simula a tecla Enter para acionar a opção imediatamente

        # EXECUÇÃO DA OPÇÃO SELECIONADA
        if key in [10, 13]:
            if selecionado == 0:  # 1. Gerar Provas
                cmd_provas()
                popup_msg(stdscr, "SUCESSO", ["Provas geradas com sucesso a partir de data.students!"])

            elif selecionado == 1:  # 2. Submeter Respostas
                serial = popup_input(stdscr, "SUBMISSÃO", "Informe o Serial da prova (ex: 01):")
                if serial:
                    versions = d.get('VERSIONS', {})
                    if serial not in versions:
                        popup_msg(stdscr, "ERRO", [f"O serial '{serial}' não foi encontrado no projeto."])
                    else:
                        aluno_info = versions[serial]
                        nome = aluno_info['nome'].replace("\\_", "_")
                        matricula_raw = aluno_info['matricula']
                        matricula = str(matricula_raw[0]) if isinstance(matricula_raw, list) else str(matricula_raw)
                        total_esperado = len(aluno_info['map'])

                        respostas = popup_input(stdscr, "SUBMISSÃO", f"Digite as {total_esperado} respostas do Serial {serial}:")
                        respostas_limpas = respostas.lower().replace(" ", "").strip()

                        if len(respostas_limpas) != total_esperado:
                            popup_msg(stdscr, "ERRO DE VALIDAÇÃO", [
                                f"A prova esperava {total_esperado} respostas,",
                                f"mas foram recebidas {len(respostas_limpas)} ('{respostas_limpas}')."
                            ])
                        else:
                            d_temp = dict(d)
                            d_temp['SUBMITS'] = dict(d.get('SUBMITS', {}))
                            d_temp['SUBMITS'][serial] = list(respostas_limpas)
                            nota_preview = calcular_nota_aluno(serial, d_temp)

                            confirmado = popup_confirmar_submissao(
                                stdscr, serial, nome, matricula, respostas_limpas, nota_preview
                            )

                            if confirmado:
                                cmd_submeter(serial, respostas_limpas, interativo=False)
                                popup_msg(stdscr, "SUBMETIDO", [
                                    f"Respostas do serial {serial} ({nome}) salvas com sucesso!",
                                    f"Nota final registrada: {nota_preview:.1f}"
                                ])
                            else:
                                popup_msg(stdscr, "CANCELADO", ["Operação cancelada. Nenhuma alteração foi salva."])

            elif selecionado == 2:  # 3. Ver Submissão e Nota por Serial
                serial = popup_input(stdscr, "CONSULTAR NOTA", "Digite o Serial do aluno:")
                if serial:
                    versions = d.get('VERSIONS', {})
                    if serial in versions:
                        nome = versions[serial]['nome'].replace("\\_", "_")
                        matricula_raw = versions[serial]['matricula']
                        matricula = str(matricula_raw[0]) if isinstance(matricula_raw, list) else str(matricula_raw)
                        
                        if serial in d.get('SUBMITS', {}):
                            nota = calcular_nota_aluno(serial, d)
                            res = "".join(d['SUBMITS'][serial]).upper()
                            popup_msg(stdscr, "DADOS DE SUBMISSÃO", [
                                f"Aluno:      {nome}",
                                f"Matrícula:  {matricula}",
                                f"Serial:     {serial}",
                                f"Respostas:  {res}",
                                f"Nota Final: {nota:.1f}"
                            ])
                        else:
                            popup_msg(stdscr, "DADOS DE SUBMISSÃO", [
                                f"Aluno:     {nome}",
                                f"Matrícula: {matricula}",
                                f"Serial:    {serial}",
                                "Status:    PENDENTE DE SUBMISSÃO"
                            ])
                    else:
                        popup_msg(stdscr, "ERRO", [f"Serial '{serial}' não foi encontrado."])

            elif selecionado == 3:  # 4. Recorrigir
                cmd_recorrigir()
                popup_msg(stdscr, "RECORREÇÃO", ["Todas as submissões foram recalculadas com sucesso!"])

            elif selecionado == 4:  # 5. Relatório de Notas
                cmd_relatorio_notas()
                popup_relatorio_opcao(stdscr, "RELATÓRIO DE NOTAS", PATHS['REPORT_NOTAS'])

            elif selecionado == 5:  # 6. Relatório Estatístico
                cmd_relatorio_estatistico()
                popup_relatorio_opcao(stdscr, "RELATÓRIO ESTATÍSTICO", PATHS['REPORT_ESTATISTICA'])

            elif selecionado == 6:  # 7. Sair
                break


if __name__ == "__main__":
    curses.wrapper(main_menu)