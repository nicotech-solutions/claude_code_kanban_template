# Início rápido

Crie e inicie um projeto enterprise em menos de 10 minutos.

---

## Pré-requisitos

- [Claude Code CLI](https://docs.anthropic.com/claude-code) instalado
- Python 3.11+ e [`uv`](https://github.com/astral-sh/uv)
- Conta no GitHub com Personal Access Token (`GH_TOKEN`) com scopes: `repo`, `project`, `workflow`, `read:org`, `gist`
- `gh` CLI instalado e autenticado (`gh auth login`)

---

## Passo 1 — Clonar o template

```bash
git clone https://github.com/ggnicolau/claude-code-enterprise-template.git
cd claude-code-enterprise-template
```

!!! info "Você trabalha no template, não em um fork"
    O `/wizard` cria o projeto filho a partir daqui. Não é necessário clicar em "Use this template" manualmente — o wizard faz isso via API.

---

## Passo 2 — Configurar o ambiente

```bash
uv sync
cp .env.example .env
```

Edite `.env` e preencha:

```bash
GH_TOKEN=ghp_...   # Personal Access Token
```

---

## Passo 3 — Abrir no Claude Code

```bash
claude
```

O `template-coordinator` exibe a mensagem de orientação com os commands disponíveis.

---

## Passo 4 — Rodar o wizard

```
/wizard
```

O wizard faz uma série de perguntas e cuida de tudo:

| Pergunta | O que define |
|---|---|
| Nome do repositório | nome do repo filho no GitHub |
| Visibilidade | público ou privado |
| Modo | **Simples** (recomendado para começar) ou **Avançado** (cloud, Docker, Agent Teams) |
| Skills Caveman? | modo de comunicação comprimido (~75% menos tokens) |

Após confirmar, o wizard:

1. Valida que o `gh` CLI está instalado e autenticado com os escopos corretos
2. Cria o repositório no GitHub via API
3. Remove arquivos internos do template que não fazem sentido no projeto filho
4. Gera `CLAUDE.md` e `AGENTS.md` parametrizados com o nome do projeto
5. Copia os 12 agentes e os commands para o filho
6. Cria branch `dev`
7. Configura o secret `GH_TOKEN` no repositório filho
8. Dispara o workflow `setup-kanban.yml` — cria o GitHub Project com labels e views
9. Valida que tudo foi criado corretamente

!!! tip "Modo Avançado"
    Escolha Avançado se for rodar tarefas pesadas na cloud (Claude Code cloud / GitHub Actions). O wizard guia a configuração passo a passo: GitHub App, `gh` CLI, autenticação, Claude Code CLI, `/web-setup` e `/remote-env`.

---

## Passo 5 — Abrir o projeto filho e rodar o kickoff

Após o wizard concluir, abra o repositório filho no Claude Code:

```bash
cd ../{seu-projeto}
claude
```

Em seguida, inicie o projeto:

```
/kickoff
```

O kickoff conduz o discovery completo:

| Fase | O que acontece |
|---|---|
| 0 | Criação da memória persistente — contexto do fundador, gênese, ancoragens |
| 1 | Discovery com researcher |
| 2 | Relatório + apresentação (PM) |
| 3 | Backlog completo em 6 dimensões (PO) |
| 4 | Aprovação do usuário |
| 5 | Delegação inicial (TL) |

!!! info "Duração"
    30–60 minutos. Pode pausar e retomar — o estado fica no Kanban e na memória.

---

## Passo 6 — Avançar no trabalho

Após o kickoff, use `/advance` para mover o projeto:

```
/advance
```

O `project-manager` fecha issues prontas, seleciona as próximas e delega ao tech-lead.

---

## O que foi criado no projeto filho

```
{seu-projeto}/
├── .claude/
│   ├── agents/          # 12 agentes especializados
│   ├── commands/        # /kickoff, /advance, /review, /deploy, ...
│   └── memory/          # memória persistente (criada no kickoff)
├── .agents/
│   └── skills/          # 11 skills enterprise + caveman x3
├── docs/                # entregáveis do projeto
├── src/                 # código fonte
├── tests/               # testes automatizados
├── notebooks/           # análise exploratória
├── scripts/
│   ├── generate_docs.js # gerador PDF/DOCX
│   └── hooks/           # hooks automáticos
└── .env                 # tokens (não versionado)
```
