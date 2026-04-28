# Convenções

Regras de nomenclatura, branches, commits e documentos.

---

## Branches

```
feature/* → dev → main
```

| Operação | Comando |
|---|---|
| Merge feature → dev | `gh pr merge --merge --delete-branch` |
| Merge dev → main | `gh pr merge --merge` (sem `--delete-branch`) |
| Cleanup após feature merge | `git checkout dev && git pull && git branch -D <nome>` |
| Sync após dev → main merge | `git checkout dev && git merge main --no-edit && git push origin dev` |

**Nunca push direto em main.**

Exceção: documentação em `docs/`, skills em `.agents/skills/`, arquivos `.md` de agentes e commands podem ir direto para `dev`.

---

## Commits

Dois regimes:

| Tipo de mudança | Formato | Exemplo |
|---|---|---|
| Trabalho de produto | `<tipo>: <descrição>` | `feat: adicionar auth OAuth` |
| Infraestrutura agentic | `<tipo>(system): <descrição>` | `docs(system): atualizar memória via /update-memory` |

Tipos válidos: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`, `build`, `ci`, `style`.

---

## Documentos

### Versionamento obrigatório

Todos os documentos em `docs/` seguem a convenção:

```
{nome}_{YYYY-MM-DD}_v{N}.md
```

Exemplos:
```
relatorio_2025-03-15_v1.md
relatorio_2025-03-15_v2.md   ← revisão no mesmo dia
arquitetura_2025-04-01_v1.md
```

### Regras

- **Nunca sobrescrever** — sempre criar nova versão com `v{N+1}`
- **Versões antigas** → mover para `archive/` após aprovação da nova versão
- **generate_docs.js** → roda automaticamente via hook ao salvar `.md` em `docs/`

### Estrutura de pastas

```
docs/
├── business/     # relatórios, GTM, modelo de negócio
├── product/      # specs, roadmap, UX
├── tech/         # arquitetura, ADRs, runbooks
├── research/     # pesquisas de mercado, benchmarks
└── updates/      # updates periódicos para stakeholders
```

---

## Agentes e commands

- **Arquivos de agente** (`.claude/agents/*.md`) — seguem nome do agente, sem versionamento
- **Commands** (`.claude/commands/*.md`) — nome do command, sem versionamento
- **Skills** (`.agents/skills/*/SKILL.md`) — um SKILL.md por diretório de skill

---

## Kanban — status válidos

| Status | Significado |
|---|---|
| `Backlog` | Identificada, não priorizada |
| `Todo` | Priorizada, pronta para execução |
| `In Progress` | Em execução por um especialista |
| `In Review` | PR aberto, aguardando review do TL |
| `Done` | Entregue, aprovada, issue fechada |
