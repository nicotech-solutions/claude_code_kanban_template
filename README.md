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
  settings.json           # Permissões base (python, pytest, ruff, black, git, uv, MCP GitHub)
.github/
  workflows/
    setup-kanban.yml      # Cria labels + Project board (auto na 1ª push)
    ci.yml                # Lint + testes em todo PR
src/                      # Código reutilizável
tests/                    # Testes pytest
notebooks/                # Jupyter notebooks
scripts/
  verify.sh               # Verifica ambiente local
pyproject.toml            # Dependências e config de ferramentas
CLAUDE.md                 # Instruções do projeto para o Claude
CLAUDE.local.md.example   # Modelo para preferências pessoais (não commitar)
.mcp.json.example         # Modelo para configurar MCP servers (não commitar)
.gitignore                # Exclui arquivos sensíveis
```

## Como usar

1. Clique em **Use this template** → **Create a new repository**

2. Adicione o secret `GH_PAT` nas configurações do novo repo:
   - Crie um **classic PAT** em [github.com/settings/tokens](https://github.com/settings/tokens) com escopo `project`
   - Vá em **Settings → Secrets → Actions → New repository secret**
   - Nome: `GH_PAT`, valor: seu PAT

3. O workflow **Setup Kanban** roda automaticamente na primeira push e:
   - Cria as labels (backlog, todo, in-progress, review, done)
   - Cria o Project board com colunas Kanban
   - Cria uma issue "🚀 Getting Started" com o checklist de setup

4. Clone o repo localmente:
   ```bash
   git clone https://github.com/SEU_USUARIO/SEU_REPO.git
   cd SEU_REPO
   ```

5. Configure os arquivos locais (não commitados):
   ```bash
   cp .mcp.json.example .mcp.json              # preencha com seu token
   cp CLAUDE.local.md.example CLAUDE.local.md  # personalize
   ```

6. Instale as dependências e verifique o ambiente:
   ```bash
   uv sync
   bash scripts/verify.sh
   ```

7. Abra o projeto no Claude Code:
   ```bash
   claude
   ```

## Slash commands

| Comando | O que faz |
|---|---|
| `/project:review` | Dispara `code-reviewer` e `security-auditor` em **paralelo** e consolida relatório com severidade 🔴🟡🔵 |
| `/project:fix-issue` | Identifica causa raiz e aplica correção mínima |
| `/project:deploy` | Checklist de deploy (testes, requirements, gitignore, tag) |

## CI

Todo PR roda automaticamente:
- `ruff check` — lint
- `black --check` — formato
- `pytest` — testes

## Kanban

Issues gerenciadas via **GitHub Projects** (Board view). Colunas: `Backlog → Todo → In Progress → Review → Done`.

## Arquivos locais (não commitados)

| Arquivo | Propósito |
|---|---|
| `.mcp.json` | Configuração dos MCP servers (contém tokens) |
| `CLAUDE.local.md` | Preferências pessoais do Claude Code |
| `.claude/settings.local.json` | Overrides locais de permissões |
