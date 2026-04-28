# Arquitetura — Visão geral

O template é organizado em quatro camadas que se comunicam de forma ordenada.

---

## Diagrama de camadas

```mermaid
graph TB
    subgraph UI["Interface"]
        USER["Fundador / PM"]
        CLI["Claude Code CLI"]
    end

    subgraph COORD["Camada de Coordenação"]
        PM["project-manager\n(CLAUDE.md)"]
        TL["tech-lead"]
        PO["product-owner"]
    end

    subgraph SPEC["Camada de Especialistas"]
        direction LR
        DE["data-engineer"]
        MLE["ml-engineer"]
        AIE["ai-engineer"]
        IDF["infra-devops"]
        QA["qa"]
        SEC["security-auditor"]
        FE["frontend-engineer"]
        RES["researcher"]
        MKT["marketing-strategist"]
    end

    subgraph INFRA["Infraestrutura"]
        GH["GitHub Projects\n(Kanban)"]
        MEM["Memória persistente\n(.claude/memory/)"]
        HOOKS["Hooks automáticos\n(post_write.sh)"]
        DOCS["Gerador de docs\n(generate_docs.js)"]
    end

    USER -->|"digita /comando"| CLI
    CLI -->|"lê CLAUDE.md"| PM
    PM -->|"delega via Task"| TL
    PM -->|"delega via Task"| PO
    PM -->|"aciona diretamente"| RES
    TL -->|"orquestra"| SPEC
    PO -->|"gerencia"| GH
    SPEC -->|"lê/escreve"| GH
    SPEC -->|"produz docs em"| DOCS
    HOOKS -->|"dispara em write"| DOCS
    PM -->|"lê antes de agir"| MEM
    PO -->|"atualiza"| MEM
```

---

## As quatro camadas

### 1. Interface

O usuário interage exclusivamente com o **Claude Code CLI** via texto. Os `/commands` são atalhos para fluxos de trabalho pré-definidos. Fora de um command, o `project-manager` responde como um assistente normal.

### 2. Coordenação

Três agentes controlam o fluxo de trabalho:

| Agente | Papel |
|---|---|
| `project-manager` | Ponto de entrada. Lê o Kanban, delega ao TL ou PO, consolida resultados. **Nunca executa trabalho técnico.** |
| `tech-lead` | Orquestrador técnico. Revisa PRs, faz merge, delega aos especialistas de engenharia. |
| `product-owner` | Dono do backlog. Gerencia o Kanban, prioriza issues, fecha cards concluídos. |

### 3. Especialistas

9 agentes temáticos. Cada um:

- Lê a issue antes de agir
- Move o card para "In Progress" no Kanban
- Produz o entregável (código, documento ou análise)
- Commita e notifica o TL ou PM para revisão
- **Nunca faz merge do próprio trabalho**

### 4. Infraestrutura

| Componente | Função |
|---|---|
| GitHub Projects | Kanban — fonte de verdade do estado do projeto |
| `.claude/memory/` | Memória persistente entre sessões (perfil, história, decisões) |
| `post_write.sh` | Hook pós-escrita: formata Python, gera PDF/DOCX, valida nomes |
| `generate_docs.js` | Converte `.md` em PDF/DOCX/PPTX para compartilhamento |

---

## Princípios de design

1. **Kanban como árbitro** — nenhum agente age sem consultar o board; nenhum entregável existe sem issue
2. **Especialização estrita** — cada agente tem papel único; nenhum faz o trabalho de outro
3. **Rastreabilidade total** — commits referenciam issues; PRs têm contexto; memória registra decisões
4. **Sem sobrescrita** — versões anteriores vão para `archive/`; o corrente fica visível em `ls`
5. **Separação system/produto** — mudanças em `.claude/` seguem regras de código (branch + PR + review)
