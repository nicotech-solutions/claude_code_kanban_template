# /fix-issue

Corrige um bug específico relatado em código, análise ou documento.

---

## Quando usar

- Para corrigir um bug encontrado em produção ou em review
- Para implementar uma correção urgente

---

## Como usar

```
/fix-issue #42
```

Ou com descrição:

```
/fix-issue "autenticação falha quando token expira em sessões longas"
```

---

## O que faz

1. **TL lê a issue** — entende o problema e o contexto
2. Identifica o agente especialista mais adequado
3. Delega a correção com critérios claros
4. O especialista implementa, testa e abre PR
5. TL revisa e mergia
6. PO fecha a issue

---

## Regras

- Bugs de segurança → aciona `security-auditor` antes de qualquer correção
- Bugs de dados → aciona `data-engineer` + `qa` para validar
- Bugs de UI → aciona `frontend-engineer`
- Bugs de infra → aciona `infra-devops`
