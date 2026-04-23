# {repo_name}

> Descrição curta do projeto — o que faz e para quem.

---

## Visão Geral

_(Preencher após o `/kickoff`: objetivo, problema que resolve, principais funcionalidades.)_

---

## Como Rodar

### Pré-requisitos

- Python 3.11+
- [`uv`](https://github.com/astral-sh/uv) instalado

### Instalação

```bash
git clone https://github.com/<org>/{repo_name}.git
cd {repo_name}
uv sync
```

### Variáveis de Ambiente

Copie o exemplo e preencha os valores:

```bash
cp .env.example .env
```

### Executar

```bash
uv run python -m src.main
```

---

## Desenvolvimento

```bash
# Testes
uv run pytest

# Linting e formatação
uv run ruff check .
uv run black .
```

Pull requests passam por CI automático (ruff + black + pytest).

---

## Estrutura

```text
src/          # código principal
tests/        # testes
notebooks/    # exploração e análise
.claude/
  agents/     # 12 agentes especializados
  commands/   # /kickoff, /advance, /review-backlog, /review, /deploy, /fix-issue, /clean
```

---

## Commands

| Command | O que faz |
|---|---|
| `/kickoff` | Inicia o projeto — discovery com você, pesquisa, relatório, apresentação, backlog completo |
| `/advance` | Avança no Kanban — fecha prontos, valida com PO, paraleliza issues independentes, delega |
| `/review-backlog` | Varredura proativa — fecha prontos, identifica lacunas, refina e cria novas issues |
| `/review` | Code review de um PR pelo tech-lead |
| `/deploy` | Deploy via infra-devops |
| `/fix-issue` | Corrige um bug ou problema reportado |
| `/clean` | Commita e faz push de tudo pendente localmente |

---

## Equipe de Agentes

O ponto de entrada é o `project-manager`. Rode `/kickoff` para iniciar o projeto ou continue pelo Kanban do GitHub Projects.

| Agente | Responsabilidade |
|---|---|
| `project-manager` | Ponto de entrada — delega, consolida |
| `tech-lead` | Orquestração técnica, code review |
| `product-owner` | Kanban, backlog, roadmap |
| `data-engineer` | Pipelines, ETL |
| `ml-engineer` | Modelos, experimentos |
| `ai-engineer` | LLMs, agentes, RAG |
| `infra-devops` | Cloud, CI/CD |
| `qa` | Testes e qualidade |
| `researcher` | Pesquisa técnica e de produto |
| `security-auditor` | Segurança |
| `frontend-engineer` | Web, UI, UX |
| `marketing-strategist` | Marketing, go-to-market, canais, publicidade |

---

## Status

Acompanhe o progresso no [GitHub Projects](https://github.com/<org>/{repo_name}/projects).
