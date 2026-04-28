# Componentes

Detalhamento de cada componente da infraestrutura do template.

---

## `.claude/settings.json`

Controla permissões e variáveis de ambiente para todos os agentes.

```json
{
  "permissions": {
    "allow": ["Bash(git:*)", "Bash(gh:*)", "Agent(*)", ...],
    "deny": ["Bash(git push --force*)", "Bash(git reset --hard*)", ...]
  },
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "95"
  },
  "hooks": {
    "SessionStart": [{"command": "bash scripts/hooks/session_start.sh"}],
    "PostToolUse": [{"command": "bash scripts/hooks/post_write.sh"}]
  }
}
```

---

## Memória persistente (`.claude/memory/`)

Criada no `/kickoff` (Fase 0). Quatro arquivos:

| Arquivo | Conteúdo | Quem lê |
|---|---|---|
| `MEMORY.md` | Índice de todos os arquivos de memória | PM, PO |
| `user_profile.md` | Perfil do fundador — background, objetivos, estilo | PM, PO |
| `project_genesis.md` | Gênese, problema resolvido, ancoragens, exclusões | PM, PO, TL |
| `project_history.md` | Histórico de decisões e entregas | PM, TL |

Convenção: PM e PO leem todos os 5 arquivos antes de agir. TL lê `project_genesis.md` + git log. Especialistas leem apenas o kickoff e git log.

---

## Hooks automáticos

### `session_start.sh`

Executado no início de cada sessão Claude Code.

- Em projetos filho: exibe o Kanban (entregas recentes, cards ativos, inconsistências)
- Em sessões cloud (`CLAUDE_CODE_REMOTE=true`): instala dependências Python e Node

### `post_write.sh`

Executado após cada escrita de arquivo.

- `.py`: roda `ruff check --fix` + `black`
- `docs/**/*.md`: roda `generate_docs.js` (gera PDF/DOCX)
- `docs/**/*.md`: valida convenção de nome `*_YYYY-MM-DD_v*.md`

---

## Skills enterprise (`.agents/skills/`)

11 skills de domínio disponíveis para os agentes:

| Skill | Usado por |
|---|---|
| `product-management` | project-manager, product-owner |
| `code-review` | tech-lead |
| `data-engineering` | data-engineer |
| `ml-engineering` | ml-engineer |
| `ai-engineering` | ai-engineer |
| `frontend-engineering` | frontend-engineer |
| `security-audit` | security-auditor |
| `qa-testing` | qa |
| `market-research` | researcher, marketing-strategist |
| `go-to-market` | marketing-strategist |
| `infra-devops` | infra-devops |

---

## GitHub Actions (`.github/workflows/`)

| Workflow | Função |
|---|---|
| `setup-kanban.yml` | Cria GitHub Project com labels, views e issue inicial no projeto filho |
| `ci.yml` | CI: ruff, black, pytest em todo PR |
