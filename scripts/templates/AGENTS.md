# {repo_name} — Equipe de Agentes

Este projeto usa uma equipe de 11 agentes especializados. O ponto de entrada padrão é o `project-manager`.

## Time

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

## Como usar

Inicie sempre pelo `project-manager` — ele entende o contexto, consulta o kanban e delega para o agente certo.

Para tarefas técnicas específicas, você pode acionar diretamente o especialista:
- Código e arquitetura → `tech-lead`
- Backlog e priorização → `product-owner`
- Pesquisa → `researcher`

## Fluxo de Kanban

| Papel | Agente | Permissões |
|---|---|---|
| Dono | `product-owner` | cria, fecha, move qualquer card, árbitro final |
| Leitor obrigatório | `project-manager` | lê o kanban antes de toda delegação |
| Criador de issues | `project-manager`, `product-owner` | abrem issues novas |
| Atualizador | todos os especialistas | move o próprio card para `In Progress` e `In Review` |
| Fechador | `product-owner` + `tech-lead` | movem para `Done` após aprovação |

## Fluxo de Código e PR

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
