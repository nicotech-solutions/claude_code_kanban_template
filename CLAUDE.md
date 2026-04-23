# Claude Code Kanban Template — Instruções para o Claude Code

Este repositório é um **template de criação de projetos**. Quando você está aqui, seu papel é ajudar a criar novos projetos a partir deste template — não desenvolver produto.

## Seu papel aqui

Você opera como **ferramenta de criação de repositórios**. O que faz sentido neste contexto:

- Rodar `/wizard` para criar um novo projeto filho
- Manter e melhorar os arquivos do template (agentes, commands, workflows, scripts)
- Não há kanban de produto aqui, não há backlog de features, não há agentes de especialidade sendo acionados

## O que este template cria

Ao rodar `/wizard`, um novo repositório filho é criado com:

- 12 agentes especializados em `.claude/agents/`
- Kanban no GitHub Projects pré-populado com épicos de negócio, produto, tech, lançamento e operações
- Commands: `/kickoff`, `/advance`, `/review-backlog`, `/review`, `/deploy`, `/fix-issue`, `/clean`
- CI/CD configurado (ruff, black, pytest)
- `CLAUDE.md` e `AGENTS.md` gerados especificamente para o projeto filho

O filho começa com `/kickoff` — que conduz discovery, monta backlog completo e obtém aprovação antes de qualquer execução.

## Arquivos importantes deste template

| Arquivo | Propósito |
|---|---|
| `scripts/new_repo.py` | Lógica do wizard de criação |
| `scripts/templates/CLAUDE.md` | CLAUDE.md gerado no filho |
| `scripts/templates/AGENTS.md` | AGENTS.md gerado no filho |
| `scripts/templates/kickoff.md` | Command `/kickoff` copiado para o filho |
| `.github/workflows/setup-kanban.yml` | Cria o Kanban e épicos no projeto filho |
| `.claude/commands/wizard.md` | Command `/wizard` — só existe no pai |
| `.claude/commands/sync-to-projects.md` | Propaga mudanças do template para os projetos filhos |
| `.claude/commands/sync-to-template.md` | Propaga melhorias de um filho de volta para o template |

## Regras de branches neste template

```
feature/* → dev → main
```

- Merges de `feature/*` → `dev`: usar `gh pr merge --merge --delete-branch` (feature branches são descartáveis)
- Merges de `dev` → `main`: usar `gh pr merge --merge` **sem** `--delete-branch` (dev é permanente)

## Iniciar

Use `/wizard` para criar um novo projeto filho.
