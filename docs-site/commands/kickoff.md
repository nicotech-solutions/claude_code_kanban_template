# /kickoff

Conduz o discovery completo e monta o backlog antes de qualquer execução.

---

## Quando usar

- Ao iniciar um projeto (logo após o `/wizard`)
- Ao retomar um projeto sem direção clara
- Ao pivotar e redefinir o escopo

---

## As 6 fases

| Fase | Agente | O que acontece |
|---|---|---|
| 0a | PM | Perguntas narrativas ao fundador |
| 0b | PM | Síntese e confirmação |
| 0c | PM | Persistência da memória em `.claude/memory/` |
| 1 | researcher | Discovery — mercado, concorrência, benchmarks técnicos |
| 2 | PM | Relatório executivo + apresentação |
| 3 | PO | Backlog completo em 6 dimensões |
| 4 | PM | Aprovação do usuário |
| 5 | TL | Delegação inicial das primeiras issues |

---

## Fase 0 — Memória persistente

A Fase 0 cria 4 arquivos em `.claude/memory/`:

```
MEMORY.md          — índice de todos os arquivos
user_profile.md    — perfil do fundador
project_genesis.md — gênese, problema, ancoragens, exclusões
project_history.md — histórico de decisões (vazio no início)
```

Commit: `docs(system): criar memória inicial do projeto via /kickoff`

---

## Backlog em 6 dimensões

O PO cria issues cobrindo:

1. **Discovery** — validação de problema, entrevistas, dados de mercado
2. **Negócio** — modelo de receita, pitch, parcerias, métricas de negócio
3. **Produto** — MVP, roadmap, UX, priorização de features
4. **Tech** — arquitetura, stack, pipelines, segurança, CI/CD
5. **Lançamento** — GTM, canais, comunicação, beta
6. **Operações** — monitoramento, suporte, processos internos

---

## Resultado

Ao final do kickoff:
- Memória em `.claude/memory/`
- Relatório em `docs/business/relatorio_YYYY-MM-DD_v1.md`
- Kanban com issues em todas as 6 dimensões
- Primeiras issues delegadas para execução
