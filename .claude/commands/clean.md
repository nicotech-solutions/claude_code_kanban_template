# Clean — Commit & Push Pending Changes

Você é o **`project-manager`**. Faça a limpeza do repositório local de forma segura.

---

## Passo 1 — Inspecionar

```bash
git status
git diff --stat HEAD
```

Classifique cada arquivo pendente:
- **Commitar** — código, docs, scripts, skills, configs, assets gerados (PDF, PPTX, XLSX, CSV, MD)
- **Ignorar** — já coberto pelo `.gitignore` (node_modules, *.zip, *.pyc, locks temporários, etc.)

Se `git status` mostrar "nothing to commit, working tree clean" → informe o usuário e pare.

---

## Passo 2 — Mostrar ao usuário

Antes de qualquer ação, liste o que será commitado:

```
📦 Vou commitar:
  + path/to/arquivo1
  + path/to/arquivo2
  ~ arquivo/modificado
```

Nunca commitar silenciosamente.

---

## Passo 3 — Staged seletivo

Adicione apenas os arquivos identificados como "Commitar". **Nunca use `git add -A` ou `git add .` sem inspecionar antes.**

```bash
git add <arquivo1> <arquivo2> ...
```

Se houver dúvida sobre um arquivo, pule e informe o usuário.

---

## Passo 4 — Commit

Mensagem seguindo Conventional Commits:
- `chore:` — limpeza, config, assets gerados
- `feat:` — novos entregáveis (docs, scripts, skills)
- `fix:` — correções

Um único commit por `/clean`, salvo se os conjuntos de arquivos forem claramente não relacionados.

---

## Passo 5 — Push

```bash
git push
```

Se falhar por remote à frente, rodar `git pull --rebase` antes de tentar novamente.

---

## Passo 6 — Confirmar

```
✅ Pronto. Working tree limpa.
```

Ou listar arquivos pulados intencionalmente e o motivo.

---

## Regras

- Nunca commitar `.env`, `.mcp.json`, `CLAUDE.local.md`, credenciais ou segredos
- Nunca commitar `node_modules/` — adicionar ao `.gitignore` se não estiver
- Nunca usar `--amend` em commits anteriores
- Se `.gitignore` estiver faltando entradas que causaram a bagunça, atualizá-lo como parte deste commit
