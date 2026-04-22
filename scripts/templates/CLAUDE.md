# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# {repo_name}

## Stack
- Python 3.11+
- Tests: pytest
- Formatting: ruff, black
- Env management: uv ou conda

## Conventions
- Type hints em todas as funções públicas
- Docstrings apenas quando o "porquê" não é óbvio
- Prefira dataclasses ou Pydantic para modelos de dados
- Notebooks em `notebooks/`, código reutilizável em `src/`
- Nunca commitar dados brutos ou modelos pesados — use `.gitignore`

## Architecture Notes
- Scripts CLI usam `typer` ou `argparse`
- Logs estruturados para rastrear execuções

## What to Avoid
- Não usar `print()` para debug — use `logging`
- Não hardcodar paths — use `pathlib.Path`
- Não misturar lógica de negócio com I/O

## Equipe Multi-Agentes

Este projeto inclui 11 agentes em `.claude/agents/`. O ponto de entrada padrão é o `project-manager`.

| Agente | Responsabilidade |
|---|---|
| `project-manager` | Ponto de entrada — delega, consolida resultados, apresentações e relatórios |
| `tech-lead` | Orquestrador técnico, code review, dono da documentação técnica |
| `product-owner` | Kanban, backlog, roadmap, priorização |
| `data-engineer` | Pipelines, ETL, qualidade de dados |
| `ml-engineer` | Modelos, features, experimentos |
| `ai-engineer` | LLMs, agentes, RAG, evals |
| `infra-devops` | Cloud, CI/CD, containers |
| `qa` | Testes unitários, integração, e2e |
| `researcher` | Pesquisa técnica e de produto, benchmarks, inteligência competitiva |
| `security-auditor` | Segurança, vulnerabilidades |
| `frontend-engineer` | Web, UI, UX |

## Regras de Kanban

O kanban é a fonte de verdade do processo. Todos os agentes devem consultá-lo antes de agir.

| Papel | Agente | Permissões |
|---|---|---|
| Dono | `product-owner` | cria, fecha, move qualquer card, árbitro final |
| Leitor obrigatório | `project-manager` | lê o kanban antes de toda delegação |
| Criador de issues | `project-manager`, `product-owner` | abrem issues novas |
| Atualizador | todos os especialistas | move o próprio card para `In Progress` e `In Review` |
| Fechador | `product-owner` + `tech-lead` | movem para `Done` após aprovação |

## Regras de Código e PR

| Etapa | Responsável |
|---|---|
| Escrever código | agente especialista da tarefa |
| Abrir PR | agente especialista que implementou |
| Code review | `tech-lead` — sempre |
| Security review | `security-auditor` — PRs com infra, auth ou dados sensíveis |
| QA review | `qa` — valida cobertura de testes |
| Aprovar PR | `tech-lead` |
| Merge | `tech-lead`; `infra-devops` em PRs de CI/CD quando delegado |
| Fechar issue | `product-owner` após merge |

Regra central: **nenhum agente faz merge do próprio trabalho sem aprovação do `tech-lead`**.

## Skills Disponíveis

Skills base em `.agents/skills/` — uma por agente. Skills Caveman são opcionais:

- `caveman` — comunicação ultra-comprimida (~75% menos tokens)
- `caveman-commit` — mensagens de commit comprimidas
- `caveman-review` — code review em uma linha por finding
