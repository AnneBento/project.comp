# 📝 Gerador e Corretor de Provas Embaralhadas

Sistema em Python integrado com LaTeX projetado para automatizar o ciclo completo de aplicação de exames educacionais: desde a elaboração e embaralhamento dinâmico de questões e alternativas para cada estudante, até a compilação do PDF das provas físicas, submissão de gabaritos e geração automática de relatórios de notas.

> O sistema foi especialmente refinado com foco em **acessibilidade**, garantindo que a saída do terminal e os relatórios gerados sejam limpos e fáceis de ler por sintetizadores de voz (como o leitor de tela Orca).

---

## 📂 Estrutura do Projeto

```
projeto_provas/
├── quests/
│   ├── head.txt          # Cabeçalho padrão de cada prova (ex: instruções)
│   ├── tail.txt          # Rodapé padrão ("Fim da Prova!")
│   ├── quest01.txt       # Arquivos das questões no padrão estruturado
│   ├── quest02.txt
│   └── ...
├── students.txt          # Lista de estudantes (Matrícula [espaço/tab] Nome)
├── shc_3_0.py             # Script principal do sistema
├── project.comp          # Banco de dados temporário com os mapas de embaralhamento
└── README.md              # Documentação do projeto
```

---

## ⚙️ Requisitos

Para gerar e compilar as provas, você precisará de:

1. **Python 3** instalado na sua máquina.
2. **TeX Live** (ou outro compilador LaTeX que forneça o comando `pdflatex`).
3. O pacote LaTeX **enumitem** instalado (usado para padronizar as listas e travar a numeração).

### Dependências do LaTeX

```bash
sudo apt install texlive-latex-base texlive-latex-extra texlive-lang-portuguese
```

---

## 🧩 Como as Questões São Estruturadas

Cada arquivo de questão (ex: `quest01.txt`) deve ser escrito usando sintaxe LaTeX com a seguinte estrutura de controle:

- O primeiro item (`\item{1, c}`) deve ser **sempre** a alternativa correta.
- Os itens subsequentes (`\item{2, e}` a `\item{5, e}`) são as alternativas incorretas.

> ⚠️ **Nota:** remova quaisquer marcadores visuais como `(Gabarito)` do texto, para que os alunos não vejam a resposta. O script faz o mapeamento puramente pelo marcador `{1, c}`.

---

## 🚀 Como Usar o Sistema

### Passo 1 — Gerar e compilar as provas

```bash
python3 shc_3_0.py --create
```

### Passo 2 — Gerar as provas individualizadas

Gera o arquivo LaTeX com todas as provas embaralhadas de forma aleatória para cada estudante presente em `students.txt`:

```bash
python3 shc_3_0.py --exams
```

O script gera o arquivo `provas.tex` e o compila automaticamente para produzir `provas.pdf`. Ele também grava no arquivo oculto do projeto `project.comp` exatamente qual foi o mapa de embaralhamento de cada estudante.

### Passo 3 — Lançar as respostas dos alunos

```bash
python3 shc_3_0.py --submit [SERIAL] [RESPOSTAS]
```

**Exemplo de submissão:**

```bash
python3 shc_3_0.py --submit 01 caccc
python3 shc_3_0.py --submit 02 dbbdc
python3 shc_3_0.py --submit 03 acbbd
```

### Passo 4 — Gerar o relatório de notas

```bash
python3 shc_3_0.py --report/
```