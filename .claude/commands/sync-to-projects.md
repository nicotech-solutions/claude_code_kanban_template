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
- `.claude/agents/*.md`
- `.claude/commands/*.md` — exceto `wizard.md`, `sync-to-projects.md` e `sync-to-template.md`
- `scripts/templates/commands/*.md` → todos comparados contra `.claude/commands/` do filho (esses commands chegam no filho via wizard, não via `.claude/commands/` do template — qualquer novo arquivo adicionado a esta pasta é automaticamente incluído)
- `.agents/skills/**` — exceto qualquer pasta com nome iniciando em `caveman`
- `scripts/templates/CLAUDE.md` → comparado contra `CLAUDE.md` do filho (substituindo `{repo_name}` pelo nome do projeto antes de comparar)
- `scripts/templates/AGENTS.md` → comparado contra `AGENTS.md` do filho (substituindo `{repo_name}` pelo nome do projeto antes de comparar)

**Para cada arquivo, classifique:**
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

Copie os arquivos:
- Agentes: copie `.claude/agents/<nome>.md` diretamente
- Commands de `.claude/commands/`: copie diretamente
- Commands de `scripts/templates/commands/`: copie todos os `.md` para `.claude/commands/` do filho
- Skills: copie `.agents/skills/<nome>/` diretamente — pule pastas `caveman*`
- `CLAUDE.md`: gere a partir de `scripts/templates/CLAUDE.md` substituindo `{repo_name}` pelo nome do projeto
- `AGENTS.md`: gere a partir de `scripts/templates/AGENTS.md` substituindo `{repo_name}` pelo nome do projeto

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
