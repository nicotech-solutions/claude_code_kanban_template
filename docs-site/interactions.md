# Interações entre agentes

Como os agentes se comunicam, colaboram e transferem trabalho.

---

## Matriz de interações

| Agente | Responde a | Trabalha com |
|---|---|---|
| `project-manager` | Usuário | tech-lead, product-owner, researcher, marketing-strategist |
| `tech-lead` | project-manager | data-engineer, ml-engineer, ai-engineer, infra-devops, qa, security-auditor, frontend-engineer, researcher |
| `product-owner` | project-manager | researcher, marketing-strategist, Kanban |
| `researcher` | PM / PO / TL | todos que precisam de inteligência |
| `marketing-strategist` | PM / PO | researcher |
| `data-engineer` | tech-lead | researcher, qa |
| `ml-engineer` | tech-lead | data-engineer, researcher |
| `ai-engineer` | tech-lead | researcher, ml-engineer |
| `infra-devops` | tech-lead | security-auditor |
| `frontend-engineer` | tech-lead | infra-devops, researcher |
| `qa` | tech-lead | data-engineer, ml-engineer |
| `security-auditor` | tech-lead / infra-devops | infra-devops |

---

## Fluxo de uma feature completa

```mermaid
sequenceDiagram
    participant User as Usuário
    participant PM as project-manager
    participant PO as product-owner
    participant TL as tech-lead
    participant Esp as Especialista
    participant GH as GitHub

    User->>PM: /advance
    PM->>GH: lê Kanban
    PM->>PO: Task: feche issues Done
    PO->>GH: fecha issues validadas
    PM->>TL: Task: "execute issue #N"
    TL->>Esp: Task: "implemente X"
    Esp->>GH: cria branch + implementa
    Esp->>GH: abre PR
    Esp->>TL: Task: "PR #M pronto"
    TL->>GH: review + merge
    TL->>PM: Task: "issue #N concluída"
    PM->>PO: Task: "feche issue #N"
    PO->>GH: move para Done + fecha issue
    PM->>User: reporta conclusão
```

---

## Regras de comunicação

1. **Task para especialistas** — sempre via `Task()` com contexto completo (issue número, critérios, branch a usar)
2. **Resposta ao PM** — especialistas reportam ao TL ou PM via `Task` ao concluir
3. **Sem comunicação lateral** — especialistas não falam entre si diretamente (passam pelo TL)
4. **Kanban como estado compartilhado** — todos leem o board antes de agir

---

## Conflitos e escalation

| Situação | Resolução |
|---|---|
| Dois agentes querem modificar o mesmo arquivo | TL decide a ordem |
| Especialista encontra bloqueio técnico | Reporta ao TL com opções |
| Decisão de produto necessária | TL escala para PM → usuário |
| Vulnerabilidade de segurança | security-auditor reporta ao TL → PM → usuário |
