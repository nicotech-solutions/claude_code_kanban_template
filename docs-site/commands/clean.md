# /clean

Commita e faz push de tudo que está pendente localmente.

---

## Quando usar

- Antes de encerrar uma sessão de trabalho
- Quando há arquivos modificados sem commit
- Para sincronizar local com remote

---

## O que faz

1. `git status` — lista arquivos modificados
2. `git add -A` — adiciona tudo
3. Gera mensagem de commit com Conventional Commits
4. `git commit`
5. `git push`

---

## Convenção de commits

| Tipo | Escopo | Quando usar |
|---|---|---|
| `feat`, `fix`, `refactor` | (nenhum) | trabalho de produto |
| `docs`, `chore`, `build` | `(system)` | infraestrutura agentic |

Exemplos:
```
feat: adicionar autenticação OAuth
docs(system): atualizar memória do projeto via /update-memory
chore(system): instalar hooks de sessão
```
