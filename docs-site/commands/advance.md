# /advance

Avança o Kanban: fecha prontos, valida próximas, paraleliza independentes e delega.

---

## Quando usar

- Após o kickoff, para dar início à execução
- A cada sessão de trabalho (é o command mais usado no dia a dia)
- Quando você quer ver o projeto progredir

---

## O que faz

1. **PM lê o Kanban** — identifica estado atual de todos os cards
2. **PO fecha prontos** — valida entregáveis em Done e fecha as issues
3. **TL valida próximas** — confirma critérios e dependências
4. **PM paraleliza** — delega issues independentes em paralelo via Agent Teams
5. **Especialistas executam** — movem cards, executam, abrem PRs
6. **TL revisa** — code review e merge
7. **PO fecha** — move para Done, fecha issue

---

## Critérios para fechar uma issue

O PO valida antes de fechar:
- [ ] Entregável existe e está commitado
- [ ] PR foi aprovado pelo TL
- [ ] CI passa (ruff, black, pytest)
- [ ] Critérios de aceitação da issue foram atendidos
- [ ] Documentação atualizada se necessário

---

## Paralelismo com Agent Teams

Com `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, o PM pode delegar múltiplas issues em paralelo:

```
PM → Task: "TL execute issue #12 (data pipeline)"
PM → Task: "TL execute issue #15 (auth endpoint)"  ← simultâneo
PM → Task: "researcher pesquise benchmark X"        ← simultâneo
```

Issues com dependências entre si **não** são paralelizadas.
