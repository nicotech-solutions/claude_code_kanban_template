# Claude Code Kanban Template

Template base para novos projetos Python com Claude Code configurado e kanban via GitHub Issues.

## O que está incluído

```
.claude/
  agents/
    code-reviewer.md      # Subagente revisor de código
    security-auditor.md   # Subagente auditor de segurança
  commands/
    review.md             # /project:review
    deploy.md             # /project:deploy
    fix-issue.md          # /project:fix-issue
  skills/
    testing-patterns/     # Padrões de teste Python
  settings.json           # Permissões base (python, pytest, ruff, black, git, uv)
CLAUDE.md                 # Instruções do projeto para o Claude
.gitignore                # Exclui arquivos sensíveis (.mcp.json, CLAUDE.local.md)
```

## Slash commands

| Comando | O que faz |
|---|---|
| `/project:review` | Dispara `code-reviewer` e `security-auditor` em **paralelo** e consolida um relatório único com severidade 🔴🟡🔵 |
| `/project:fix-issue` | Identifica causa raiz e aplica correção mínima |
| `/project:deploy` | Checklist de deploy (testes, requirements, gitignore, tag) |

## Como usar

1. Clique em **Use this template** → **Create a new repository**
2. Clone o novo repo localmente
3. Crie `.mcp.json` com seu PAT do GitHub (não commitar — já está no `.gitignore`)
4. Crie `CLAUDE.local.md` com suas preferências pessoais (não commitar)
5. Abra o projeto no Claude Code: `claude`

## Kanban

Issues do projeto são gerenciadas via **GitHub Projects** (Board view). Colunas sugeridas: `Backlog → Todo → In Progress → Review → Done`.

## Arquivos locais (não commitados)

| Arquivo | Propósito |
|---|---|
| `.mcp.json` | Configuração dos MCP servers (contém tokens) |
| `CLAUDE.local.md` | Preferências pessoais do Claude Code |
| `.claude/settings.local.json` | Overrides locais de permissões |
