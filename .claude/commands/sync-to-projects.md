# Sync to Projects

Sincroniza os arquivos de framework do template para os projetos filhos informados. O template é a fonte de verdade — os filhos são atualizados para refletir o template.

**Uso:** `/sync-to-projects <projeto1>, <projeto2>, ...`

Os projetos são resolvidos relativamente ao diretório pai deste template (`../`).

> **Este comando só vai do template para os filhos.** Para propagar melhorias de um filho de volta ao template, use `/sync-to-template`.

---

## Processo obrigatório

### Passo 1 — Identificar projetos

Parse os argumentos separados por vírgula. Para cada projeto, resolve o caminho como `../<nome>`. Verifique se o diretório existe — se não existir, informe e pule.

### Passo 2 — Mapear diferenças

Para cada projeto, compare com o template:

**Arquivos do template (fonte de verdade):**
- `scripts/templates/agents/*.md` → comparados contra `.claude/agents/` do filho
- `.claude/commands/*.md` — exceto `wizard.md`, `sync-to-projects.md`, `sync-to-template.md` e `sync-master.md`
- `scripts/templates/commands/*.md` → todos comparados contra `.claude/commands/` do filho (esses commands chegam no filho via wizard, não via `.claude/commands/` do template — qualquer novo arquivo adicionado a esta pasta é automaticamente incluído)
- `.agents/skills/**` — exceto qualquer pasta com nome iniciando em `caveman`
- `scripts/hooks/session_start.sh` → comparado contra `scripts/hooks/session_start.sh` do filho
- `scripts/hooks/post_write.sh` → comparado contra `scripts/hooks/post_write.sh` do filho
- `.gitattributes` → comparado contra `.gitattributes` do filho
- `scripts/templates/.gitattributes` → comparado contra `scripts/templates/.gitattributes` do filho
- `scripts/templates/CLAUDE.md` → comparado contra `CLAUDE.md` do filho (substituindo `{repo_name}` pelo nome do projeto antes de comparar)
- `scripts/templates/AGENTS.md` → comparado contra `AGENTS.md` do filho (substituindo `{repo_name}` pelo nome do projeto antes de comparar)

**Como comparar — use diff, não leia os arquivos inteiros:**

Para cada arquivo da lista acima, compare via shell:

```bash
diff <caminho-template> <caminho-filho> 2>/dev/null
```

- Arquivo não existe no filho → `NOVO`
- diff vazio → `OK` (pula — não carregue o conteúdo)
- diff com diferença → `DESATUALIZADO` (exiba o diff ao usuário)

Para `CLAUDE.md` e `AGENTS.md`, compare após substituição de `{repo_name}`:

```bash
sed 's/{repo_name}/<nome-projeto>/g' scripts/templates/CLAUDE.md | diff - ../<projeto>/CLAUDE.md
```

Para skills (diretórios), use `diff -r`:

```bash
diff -r .agents/skills/<nome>/ ../<projeto>/.agents/skills/<nome>/ 2>/dev/null
```

**Classifique cada arquivo:**
- `NOVO` — existe no template mas não no filho
- `DESATUALIZADO` — existe nos dois mas conteúdo difere
- `OK` — idêntico (ignorar na listagem)
- `EXTRA` — existe no filho mas não no template (não tocar)

### Passo 3 — Reportar ao usuário

Exiba um relatório por projeto:

```
📁 <projeto>
  NOVO         .claude/agents/marketing-strategist.md
  DESATUALIZADO .claude/commands/fix-issue.md
  EXTRA        .claude/agents/custom-agent.md  ← não será tocado
  OK           (11 arquivos idênticos)
```

Se todos os arquivos estiverem OK, informe e encerre para esse projeto.

### Passo 4 — Confirmar antes de agir

Pergunte ao usuário:

```
Deseja sincronizar os arquivos NOVO e DESATUALIZADO acima?
Para projetos com EXTRA: esses arquivos não serão alterados.
```

Aguarde confirmação explícita antes de prosseguir.

### Passo 5 — Sincronizar

Para cada arquivo NOVO ou DESATUALIZADO, **não commite direto** — crie um branch e abra PR:

```bash
git checkout -b sync/to-projects-YYYY-MM-DD
```

Copie os arquivos via shell — não reescreva o conteúdo:

```bash
# Agentes
cp scripts/templates/agents/<nome>.md ../<projeto>/.claude/agents/<nome>.md

# Commands de .claude/commands/ do template
cp .claude/commands/<nome>.md ../<projeto>/.claude/commands/<nome>.md

# Commands de scripts/templates/commands/
cp scripts/templates/commands/<nome>.md ../<projeto>/.claude/commands/<nome>.md

# Skills (exceto caveman*) — rm antes para evitar aninhamento se destino já existe
rm -rf ../<projeto>/.agents/skills/<nome>
cp -r .agents/skills/<nome> ../<projeto>/.agents/skills/<nome>

# Hooks e .gitattributes
cp scripts/hooks/session_start.sh ../<projeto>/scripts/hooks/session_start.sh
cp scripts/hooks/post_write.sh ../<projeto>/scripts/hooks/post_write.sh
cp .gitattributes ../<projeto>/.gitattributes
cp scripts/templates/.gitattributes ../<projeto>/scripts/templates/.gitattributes

# CLAUDE.md e AGENTS.md — substituir {repo_name} pelo nome do projeto
sed 's/{repo_name}/<nome-projeto>/g' scripts/templates/CLAUDE.md > ../<projeto>/CLAUDE.md
sed 's/{repo_name}/<nome-projeto>/g' scripts/templates/AGENTS.md > ../<projeto>/AGENTS.md
```

Nunca toque em arquivos classificados como `EXTRA`.

Após copiar, commit, abra PR para `dev` e faça o merge:

```bash
git add .claude/ .agents/ CLAUDE.md AGENTS.md
git commit -m "chore: sync framework from template"
git push -u origin sync/to-projects-YYYY-MM-DD
gh pr create --base dev --title "chore: sync framework from template" --body "Sincronização automática via /sync-to-projects."
gh pr merge --merge --delete-branch
git checkout dev && git pull
```

Após o merge em `dev`, pergunte ao usuário:

```
✅ <projeto> — X arquivos mergiados em dev.
Deseja promover para main agora?
```

Aguarde confirmação explícita antes de mergiar em `main`.

### Passo 6 — Reportar resultado

```
✅ <projeto> — X arquivos sincronizados
   + .claude/agents/marketing-strategist.md
   ~ .claude/commands/fix-issue.md

Mergiado em dev. Aguardando sua confirmação para promover para main.
```

---

## Regras

- Nunca sobrescrever arquivos `EXTRA` — são customizações do filho
- Nunca commitar direto — sempre branch + PR para `dev`; `main` só quando o usuário pedir explicitamente
- `wizard.md`, `sync-to-projects.md` e `sync-to-template.md` nunca vão para filhos
- Skills `caveman*` são opcionais por projeto — nunca sincronizar
- Se o usuário não passar argumentos, perguntar quais projetos sincronizar
- **O template tem dois `CLAUDE.md`**: o root (`CLAUDE.md`) descreve o próprio template e **nunca vai para filhos**. O que vai para filhos é `scripts/templates/CLAUDE.md` (com `{repo_name}`), copiado para a raiz do filho como `CLAUDE.md`
- **Nunca fazer `cp CLAUDE.md` do root do template** — sempre usar `scripts/templates/CLAUDE.md` como fonte
- **Commands de filho que vieram de `scripts/templates/commands/`** nunca devem ser tratados como EXTRA — são commands legítimos instalados pelo wizard

$ARGUMENTS
