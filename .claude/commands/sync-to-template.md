# Sync to Template

Propaga melhorias de um projeto filho de volta para o template. Use quando o filho evoluiu um arquivo que deve virar padrão para todos os projetos.

**Uso:** `/sync-to-template <projeto>` (um projeto por vez — você está decidindo o que vira padrão)

O projeto é resolvido relativamente ao diretório pai do template (`../`).

> **Este comando só vai do filho para o template.** Para propagar melhorias do template para os filhos, use `/sync-to-projects`.

---

## Processo obrigatório

### Passo 1 — Identificar projeto

Parse o argumento. Resolve o caminho como `../<nome>`. Verifique se o diretório existe — se não, informe e encerre.

### Passo 2 — Mapear diferenças

Compare o filho com o template:

**Arquivos comparados (filho é a fonte de avaliação):**
- `.claude/agents/*.md` → contra `.claude/agents/` do template
- `.claude/commands/*.md` — exceto `wizard.md`, `sync-to-projects.md` e `sync-to-template.md` → contra `.claude/commands/` do template
- `.claude/commands/*.md` que correspondam a `scripts/templates/commands/` → contra `scripts/templates/commands/` do template
- `.agents/skills/**` — exceto pastas `caveman*` → contra `.agents/skills/` do template
- `CLAUDE.md` do filho → contra `scripts/templates/CLAUDE.md` (substituindo o nome do projeto por `{repo_name}` antes de comparar)
- `AGENTS.md` do filho → contra `scripts/templates/AGENTS.md` (substituindo o nome do projeto por `{repo_name}` antes de comparar)

**Para cada arquivo, classifique:**
- `FILHO MAIS NOVO` — conteúdo difere e o filho parece mais completo/atualizado
- `TEMPLATE MAIS NOVO` — conteúdo difere e o template parece mais completo/atualizado
- `OK` — idêntico (ignorar na listagem)
- `SÓ NO FILHO` — existe no filho mas não no template (candidato a adicionar ao template)
- `SÓ NO TEMPLATE` — existe no template mas não no filho (ignorar aqui)

### Passo 3 — Reportar ao usuário

Exiba o relatório:

```
📁 <projeto> → template

  FILHO MAIS NOVO    .claude/agents/marketing-strategist.md
  FILHO MAIS NOVO    .claude/commands/fix-issue.md
  SÓ NO FILHO        .claude/agents/custom-agent.md
  TEMPLATE MAIS NOVO .claude/agents/qa.md  ← template não será sobrescrito
  OK                 (25 arquivos idênticos)
```

Para cada `TEMPLATE MAIS NOVO`: informe que o template já está à frente e não será sobrescrito por este sync.

Se não houver `FILHO MAIS NOVO` nem `SÓ NO FILHO`, informe e encerre.

### Passo 4 — Confirmar antes de agir

Pergunte ao usuário arquivo por arquivo (ou em bloco se forem muitos):

```
Os arquivos acima do filho serão copiados para o template.
Arquivos SÓ NO FILHO: deseja adicioná-los ao template também?
Confirma?
```

Aguarde confirmação explícita antes de prosseguir.

### Passo 5 — Sincronizar no template

Crie um branch no template e copie os arquivos confirmados:

```bash
git checkout -b sync/to-template-YYYY-MM-DD
```

Copie os arquivos:
- Agentes: copie para `.claude/agents/` do template
- Commands de `.claude/commands/` do filho: copie para `.claude/commands/` do template
- Commands que correspondam a `scripts/templates/commands/`: copie para `scripts/templates/commands/` do template
- Skills: copie para `.agents/skills/` do template — pule pastas `caveman*`
- `CLAUDE.md` do filho: substitua o nome do projeto por `{repo_name}` e salve em `scripts/templates/CLAUDE.md`
- `AGENTS.md` do filho: substitua o nome do projeto por `{repo_name}` e salve em `scripts/templates/AGENTS.md`

Após copiar, commit e abra PR para `dev` do template:

```bash
git add .
git commit -m "chore: sync improvements from <projeto> to template"
git push -u origin sync/to-template-YYYY-MM-DD
gh pr create --base dev --title "chore: sync improvements from <projeto> to template" --body "Melhorias propagadas via /sync-to-template."
```

### Passo 6 — Reportar resultado

```
✅ Template atualizado com melhorias de <projeto>
   ~ .claude/agents/marketing-strategist.md
   ~ .claude/commands/fix-issue.md
   + .claude/agents/custom-agent.md

PR aberto para revisão antes do merge.
Após merge no template, rode /sync-to-projects para propagar aos demais filhos.
```

---

## Regras

- Um projeto por vez — você está decidindo o que vira padrão, não é automático
- Nunca sobrescrever arquivo do template onde o template está mais novo
- `CLAUDE.md` e `AGENTS.md`: sempre substituir o nome do projeto por `{repo_name}` antes de salvar no template
- Nunca copiar `wizard.md`, `sync-to-projects.md` ou `sync-to-template.md` do filho (não existem no filho, mas por segurança)
- Skills `caveman*` nunca vão para o template
- Sempre abrir PR — nunca commitar direto em `dev` ou `main` do template
- Após merge no template, lembre o usuário de rodar `/sync-to-projects` para propagar aos demais filhos

$ARGUMENTS
