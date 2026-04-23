# Sync Framework

Sincroniza os arquivos de framework (`.claude/agents/`, `.claude/commands/`, `CLAUDE.md`, `AGENTS.md`) do template para os projetos filhos informados.

**Uso:** `/sync-framework <projeto1>, <projeto2>, ...`

Os projetos são resolvidos relativamente ao diretório pai deste template (`../`).

---

## Processo obrigatório

### Passo 1 — Identificar projetos

Parse os argumentos separados por vírgula. Para cada projeto, resolve o caminho como `../<nome>`. Verifique se o diretório existe — se não existir, informe e pule.

### Passo 2 — Mapear diferenças

Para cada projeto, compare com o template:

**Arquivos do template (fonte de verdade):**
- `.claude/agents/*.md`
- `.claude/commands/*.md` — exceto `wizard.md` e `sync-framework.md`
- `.agents/skills/**` — exceto qualquer pasta com nome iniciando em `caveman`
- `scripts/templates/CLAUDE.md`
- `scripts/templates/AGENTS.md`
- `scripts/templates/README.md`

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

Para cada arquivo NOVO ou DESATUALIZADO:
- Agentes: copie `.claude/agents/<nome>.md` diretamente
- Commands: copie `.claude/commands/<nome>.md` diretamente
- Skills: copie `.agents/skills/<nome>/` diretamente — pule pastas `caveman*`
- `CLAUDE.md`: gere a partir de `scripts/templates/CLAUDE.md` substituindo `{repo_name}` pelo nome do projeto
- `AGENTS.md`: gere a partir de `scripts/templates/AGENTS.md` substituindo `{repo_name}` pelo nome do projeto
- `README.md`: gere a partir de `scripts/templates/README.md` substituindo `{repo_name}` pelo nome do projeto

Nunca toque em arquivos classificados como `EXTRA`.

### Passo 6 — Reportar resultado

```
✅ <projeto> — X arquivos sincronizados
   + .claude/agents/marketing-strategist.md
   ~ .claude/commands/fix-issue.md
```

Lembre ao usuário que precisa commitar e dar push em cada projeto sincronizado.

---

## Regras

- Nunca sobrescrever arquivos `EXTRA` — são customizações do filho
- Nunca commitar automaticamente — deixar para o usuário
- `wizard.md` e `sync-framework.md` nunca vão para filhos
- Skills `caveman*` são opcionais por projeto — nunca sincronizar
- Se o usuário não passar argumentos, perguntar quais projetos sincronizar

$ARGUMENTS
