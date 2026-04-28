# Referência rápida

Consulta rápida para os principais elementos do sistema.

---

## Commands

| Command | Uso |
|---|---|
| `/wizard` | Criar projeto filho |
| `/kickoff` | Discovery completo + backlog |
| `/advance` | Avançar Kanban |
| `/review-backlog` | Varredura proativa |
| `/review` | Code review de PR |
| `/deploy` | Deploy com checklist |
| `/fix-issue` | Corrigir bug |
| `/clean` | Commit + push pendentes |
| `/update-memory` | Registrar decisões na memória |

---

## Agentes

| Agente | Acionado por | Papel |
|---|---|---|
| `project-manager` | Usuário | Coordenação geral |
| `tech-lead` | PM | Técnico |
| `product-owner` | PM | Produto e Kanban |
| `researcher` | PM / PO / TL | Inteligência |
| `marketing-strategist` | PM / PO | GTM |
| `data-engineer` | TL | Dados e pipelines |
| `ml-engineer` | TL | Modelos de ML |
| `ai-engineer` | TL | LLMs e agentes |
| `infra-devops` | TL | Cloud e CI/CD |
| `qa` | TL | Testes |
| `security-auditor` | TL / infra-devops | Segurança |
| `frontend-engineer` | TL | Web e UI |

---

## Memória persistente

| Arquivo | Quem lê | Conteúdo |
|---|---|---|
| `.claude/memory/MEMORY.md` | PM, PO | Índice |
| `.claude/memory/user_profile.md` | PM, PO | Perfil do fundador |
| `.claude/memory/project_genesis.md` | PM, PO, TL | Gênese e ancoragens |
| `.claude/memory/project_history.md` | PM, TL | Histórico de decisões |

---

## Skills disponíveis

| Skill | Localização |
|---|---|
| `product-management` | `.agents/skills/product-management/SKILL.md` |
| `code-review` | `.agents/skills/code-review/SKILL.md` |
| `data-engineering` | `.agents/skills/data-engineering/SKILL.md` |
| `ml-engineering` | `.agents/skills/ml-engineering/SKILL.md` |
| `ai-engineering` | `.agents/skills/ai-engineering/SKILL.md` |
| `frontend-engineering` | `.agents/skills/frontend-engineering/SKILL.md` |
| `security-audit` | `.agents/skills/security-audit/SKILL.md` |
| `qa-testing` | `.agents/skills/qa-testing/SKILL.md` |
| `market-research` | `.agents/skills/market-research/SKILL.md` |
| `go-to-market` | `.agents/skills/go-to-market/SKILL.md` |
| `infra-devops` | `.agents/skills/infra-devops/SKILL.md` |
| `caveman` | `.agents/skills/caveman/SKILL.md` |
| `caveman-commit` | `.agents/skills/caveman-commit/SKILL.md` |
| `caveman-review` | `.agents/skills/caveman-review/SKILL.md` |

---

## Permissões bloqueadas

```
git push --force
git reset --hard
git clean -f
gh repo delete
gh secret set/delete
gh auth login/token
```

---

## Variáveis de ambiente

| Variável | Padrão | Significado |
|---|---|---|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` | Múltiplos agentes em paralelo |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | `95` | Compacta contexto ao atingir 95% |
| `GH_TOKEN` | (do .env) | Token GitHub para gh CLI |

---

## Instalar MkDocs localmente

```bash
pip install mkdocs-material
mkdocs serve
# Acesse: http://127.0.0.1:8000
```
