import curses
import sys
import os
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
    """JANELA POP-UP CENTRALIZADA PARA LEITURA DE ENTRADA"""
    h, w = stdscr.getmaxyx()
    window_h, window_w = 8, 62
    start_y, start_x = (h - window_h) // 2, (w - window_w) // 2

    window = curses.newwin(window_h, window_w, start_y, start_x)
    window.keypad(True)
    window.box()

    window.addstr(1, 2, f"[ {title} ]", curses.A_BOLD)
    window.addstr(3, 2, prompt[:58])
    window.refresh()

    # Habilita o cursor para digitação
    curses.echo()
    curses.curs_set(1)

    # Lê os caracteres informados pelo usuário
    input_bytes = window.getstr(4, 2, 50)
    texto = input_bytes.decode('utf-8').strip()

    curses.noecho()
    curses.curs_set(0)
    return texto


def popup_msg(stdscr, title, linhas):
    """Exibe um bloco de texto centralizado"""
    h, w = stdscr.getmaxyx()
    window_h, window_w = max(len(linhas) + 6, 8), 64
    start_y, start_x = (h - window_h) // 2, (w - window_w) // 2

    window = curses.newwin(window_h, window_w, start_y, start_x)
    window.keypad(True)
    window.box()

    window.addstr(1, 2, f"[ {title} ]", curses.A_BOLD)

    for idx, l in enumerate(linhas):
        window.addstr(3 + idx, 2, str(l)[:60])

    window.addstr(window_h - 2, 2, "Pressione qualquer tecla para voltar.")
    window.refresh()
    window.getch()


def popup_confirmar_submissao(stdscr, serial, nome, matricula, respostas, nota):
    """Prévia da nota antes da confirmação"""
    h, w = stdscr.getmaxyx()
    window_h, window_w = 12, 64
    start_y, start_x = (h - window_h) // 2, (w - window_w) // 2

    window = curses.newwin(window_h, window_w, start_y, start_x)
    window.keypad(True)
    window.box()

    window.addstr(1, 2, "[CONFIRMAÇÃO DE SUBMISSÃO]", curses.A_BOLD)
    window.addstr(3, 2, f"Serial:     {serial}")
    window.addstr(4, 2, f"Aluno:      {nome[:45]}")
    window.addstr(5, 2, f"Matrícula:  {matricula}")
    window.addstr(6, 2, f"Respostas:  {respostas.upper()}")
    window.addstr(7, 2, f"Nota:       {nota:.1f}", curses.A_BOLD)
    window.addstr(9, 2, "Deseja confirmar o registro para este aluno? [S/n]: ", curses.A_DIM)
    window.refresh()

    curses.echo()
    curses.curs_set(1)
    resp = window.getstr(9, 53, 5).decode('utf-8').strip().lower()
    curses.noecho()
    curses.curs_set(0)

    return resp in ['', 's', 'sim']


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
        stdscr.addstr(1, max(0, (w - len(titulo)) // 2), titulo, curses.A_BOLD)
        stdscr.addstr(2, 2, "Navegue com as SETAS [↑/↓] e pressione [ENTER] para selecionar.", curses.A_DIM)
        stdscr.addstr(3, 0, "-" * w)

        d = load_project(PATHS['PROJECT'])
        qtd_provas = len(d.get('VERSIONS', {}))
        qtd_submits = len(d.get('SUBMITS', {}))

        for idx, item in enumerate(opcoes):
            y = 5 + idx
            x = 4

            status = ""
            if idx == 0:
                status = f" ({qtd_provas} geradas)"
            elif idx in [1, 2]:
                status = f" ({qtd_submits}/{qtd_provas} submetidas)"

            label = f"{item}{status}"

            if idx == selecionado:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, f"> {label:<65}")
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, f"  {label:<65}")

        stdscr.addstr(h - 2, 2, "[Setas]: Navegar  |  [Enter]: Selecionar  |  [Esc/7]: Sair", curses.A_DIM)
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selecionado = (selecionado - 1) % len(opcoes)
        elif key == curses.KEY_DOWN:
            selecionado = (selecionado + 1) % len(opcoes)

        elif key in [10, 13]:
            if selecionado == 0:  # Gerar Provas
                cmd_provas()
                popup_msg(stdscr, "SUCESSO", ["Provas geradas com sucesso a partir de data.students!"])

            elif selecionado == 1:  # Submeter Respostas
                serial = popup_input(stdscr, "SUBMISSÃO", "Informe o Serial da prova (ex: 01):")
                if serial:
                    versions = d.get('VERSIONS', {})
                    if serial not in versions:
                        popup_msg(stdscr, "ERRO", [f"O serial '{serial}' não foi encontrado no projeto."])
                    else:
                        aluno_info = versions[serial]
                        nome = aluno_info['nome'].replace("\\_", "_")
                        matricula = aluno_info['matricula']
                        total_esperado = len(aluno_info['map'])

                        respostas = popup_input(stdscr, "SUBMISSÃO", f"Digite as {total_esperado} respostas do Serial {serial}:")
                        respostas_limpas = respostas.lower().replace(" ", "").strip()

                        if len(respostas_limpas) != total_esperado:
                            popup_msg(stdscr, "ERRO DE VALIDAÇÃO", [
                                f"A prova esperava {total_esperado} respostas,",
                                f"mas foram recebidas {len(respostas_limpas)} ('{respostas_limpas}')."
                            ])
                        else:
                            # Calcula a nota prévia
                            d_temp = dict(d)
                            d_temp['SUBMITS'] = dict(d.get('SUBMITS', {}))
                            d_temp['SUBMITS'][serial] = list(respostas_limpas)
                            nota_preview = calcular_nota_aluno(serial, d_temp)

                            # Pergunta antes de gravar
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

            elif selecionado == 2:  # Ver Submissão e Nota por Serial
                serial = popup_input(stdscr, "CONSULTAR NOTA", "Digite o Serial do aluno:")
                if serial:
                    versions = d.get('VERSIONS', {})
                    if serial in versions:
                        nome = versions[serial]['nome'].replace("\\_", "_")
                        matricula = versions[serial]['matricula']
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

            elif selecionado == 3:  # Recorrigir
                cmd_recorrigir()
                popup_msg(stdscr, "RECORREÇÃO", ["Todas as submissões foram recalculadas com sucesso!"])

            elif selecionado == 4:  # Relatório de Notas
                cmd_relatorio_notas()
                popup_msg(stdscr, "RELATÓRIO DE NOTAS", ["Arquivo 'report_notas.txt' gerado com sucesso."])

            elif selecionado == 5:  # Relatório Estatístico
                cmd_relatorio_estatistico()
                popup_msg(stdscr, "ESTATÍSTICA", ["Arquivo 'report_estatistica.txt' gerado com sucesso."])

            elif selecionado == 6:  # Sair
                break

if __name__ == "__main__":
    curses.wrapper(main_menu)