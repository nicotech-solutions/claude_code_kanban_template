# /update-memory

Registra decisões importantes, restrições e entregáveis aprovados na memória persistente.

---

## Quando usar

- Após uma decisão arquitetural importante
- Após aprovação de um entregável significativo
- Quando uma restrição nova foi descoberta
- Ao final de uma fase do projeto

---

## O que faz

1. **PM audita** — git log + issues fechadas + novos docs desde o último registro
2. **Identifica** o que é relevante para registrar na memória
3. **Atualiza** `project_history.md` (adiciona ao topo — não sobrescreve)
4. Opcionalmente atualiza `user_profile.md` ou `project_genesis.md`
5. Commit: `docs(system): atualizar memória do projeto via /update-memory`

---

## O que registrar

**Registre:**
- Decisões arquiteturais com justificativa
- Restrições descobertas em produção
- Pivots de produto com contexto
- Entregáveis aprovados pelo usuário

**Não registre:**
- Progresso rotineiro de issues (o Kanban já faz isso)
- Detalhes de implementação (o código já documenta)
- Informações que mudam com frequência
