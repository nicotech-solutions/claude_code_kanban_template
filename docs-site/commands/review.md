# /review

Code review pontual de um PR específico.

---

## Quando usar

- Para revisar um PR antes de mergiar
- Quando o tech-lead quer uma segunda opinião
- Para revisar PRs de código gerado por especialistas

---

## O que faz

1. **TL lê o diff completo** do PR indicado
2. Avalia: corretude, segurança, performance, legibilidade, cobertura de testes
3. Usa a skill `code-review` (`.agents/skills/code-review/SKILL.md`)
4. Adiciona comentários inline no PR via `gh pr review`
5. Aprova ou solicita mudanças

---

## Como usar

```
/review PR#42
```

Ou sem argumento — o TL identifica o PR mais recente aberto.

---

## Critérios de aprovação

- [ ] Lógica correta e sem regressões
- [ ] Sem credenciais ou secrets hardcoded
- [ ] Testes existentes passam, novos testes cobrem o novo código
- [ ] CI (ruff, black, pytest) passa
- [ ] Sem vulnerabilidades óbvias (OWASP top 10)
