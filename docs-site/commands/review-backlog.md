# /review-backlog

Varredura proativa do Kanban: fecha prontos, identifica lacunas, refina e cria novas issues.

---

## Quando usar

- Board está desatualizado ou confuso
- Fim de sprint ou fase
- Antes de apresentação para stakeholders
- Quando surgem novas decisões que geram novas issues

---

## O que faz

1. **PO percorre todas as issues abertas** — estado por estado
2. **Fecha issues prontas** — que estão Done mas não foram fechadas
3. **Identifica bloqueios** — issues In Progress sem progresso há mais de 3 dias
4. **Detecta lacunas** — dimensões sem cobertura adequada
5. **Cria novas issues** — para lacunas identificadas
6. **Remove duplicatas** — fecha issues redundantes
7. **Reporta** — resumo do estado do board + ações tomadas

---

## Saída esperada

```
Review do Kanban — {data}

Fechadas: #12, #15
Bloqueadas: #18 (aguardando decisão de produto)
Novas issues criadas: #23 (observabilidade), #24 (testes E2E)
Lacunas: dimensão Operações sem cobertura — criadas 2 issues
```
