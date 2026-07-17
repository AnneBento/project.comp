# 📝 Sistema de Provas Embaralhadas Simplificado (SHC v3.0)

Este script em Python automatiza a geração de provas impressas personalizadas em LaTeX com **embaralhamento duplo simultâneo** — as questões mudam de ordem para cada aluno, e as alternativas dentro de cada questão também mudam de lugar. O sistema também gerencia a submissão de respostas e gera um relatório automático de notas.

---

## 📁 Estrutura de Pastas e Arquivos

Para o script funcionar perfeitamente, o seu diretório de projeto deve seguir esta estrutura básica:

```text
seu-projeto/
├── shc_3_0.py          # O script principal
├── students.txt        # Lista de estudantes (Matrícula + Nome)
└── quests/             # Pasta gerenciada pelo sistema
    ├── head.txt        # Cabeçalho padrão da instituição
    ├── tail.txt        # Rodapé padrão da prova
    ├── quest01.txt     # Arquivo de questão 1
    └── quest02.txt     # Arquivo de questão 2 (e assim por diante...)
```

> ⚠️ **Nota sobre o `students.txt`:** cada linha deve conter a matrícula seguida por um espaço ou tabulação e o nome do aluno.
> Exemplo: `123456 João Silva`

---

## 🛠️ Como Estruturar as Questões (`quests/questXX.txt`)

Cada arquivo de questão dentro da pasta `quests/` deve seguir rigorosamente a sintaxe abaixo:

```latex
%% -- QUESTÃO 01 --
\quest Este é o enunciado da questão de Álgebra Linear. Quanto é 2+2?

\item{1, c} Esta é a alternativa correta (letra 'c' indica Correct)
\item{2, e} Esta é uma alternativa errada (letra 'e' indica Error)
\item{3, e} Terceira alternativa errada
\item{4, e} Quarta alternativa errada
```

---

## 🚀 Fluxo de Trabalho (Passo a Passo)

### Passo 1 — Inicializar o Projeto

Para criar a estrutura inicial, a pasta `quests/`, os modelos de cabeçalho, rodapé e arquivos base de questões, rode:

```bash
python3 shc_3_0.py --create
```

O script perguntará quantas questões você deseja e criará os arquivos que faltam, sem sobrescrever os existentes.

### Passo 2 — Gerar as Provas (PDF)

Após configurar o `students.txt` e escrever suas questões na pasta `quests/`, gere o caderno de provas integrado executando:

```bash
python3 shc_3_0.py --exams
```

Este comando cria o arquivo `provas.tex`, salva a ordem de embaralhamento de cada aluno no banco de dados local `project.comp` e compila automaticamente o arquivo `provas.pdf` em duas colunas com folhas de resposta individuais.

### Passo 3 — Submeter as Respostas dos Alunos

Após aplicar a prova e recolher os gabaritos, insira as respostas de cada aluno usando o **Serial da Prova** impresso na folha dele:

```bash
python3 shc_3_0.py --submit <SERIAL> <RESPOSTAS>
```

**Exemplo:** se o aluno do Serial `01` marcou sequencialmente as alternativas `a`, `b`, `c`, `d`, `e`:

```bash
python3 shc_3_0.py --submit 01 abcde
```

### Passo 4 — Gerar o Relatório de Notas

Para computar as notas de toda a turma de forma automática (o sistema cruza o gabarito real com a ordem exata de questões/itens que aquele serial específico recebeu), execute:

```bash
python3 shc_3_0.py --report
```

As notas são exibidas no terminal e salvas detalhadamente no arquivo `report.txt`.

---

## ⚙️ Pré-requisitos

Para compilar o PDF com sucesso, certifique-se de ter um interpretador LaTeX instalado no sistema:

- **Linux (Ubuntu/Debian):**
  ```bash
  sudo apt install texlive-latex-base texlive-latex-extra texlive-lang-portuguese
  ```
- **Python:** 3.x (utiliza apenas bibliotecas nativas)
