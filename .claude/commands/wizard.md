# Wizard — Criar Novo Repositório Enterprise

**Antes de qualquer pergunta**, verifique se o `gh` CLI está instalado e autenticado.

Rode:
```bash
gh --version 2>&1
```

Se o comando falhar (não reconhecido / não encontrado), detecte o sistema operacional:
```bash
python -c "import platform; print(platform.system())"
```

Exiba como texto a instrução de instalação correta para o SO detectado:
- **Windows**: `winget install GitHub.cli`
- **Darwin** (macOS): `brew install gh`
- **Linux**: `sudo apt install gh` (ou o package manager da distro — apt, dnf, pacman)

Use `AskUserQuestion`: `Feito` | `Cancelar wizard` — se cancelar, encerre o fluxo.

Se `gh --version` funcionar, rode:
```bash
gh auth status 2>&1
```

Analise o output:
- Contém `Logged in to github.com` **e** todos os escopos `gist`, `project`, `read:org`, `repo`, `workflow` aparecem em `Token scopes:` → continue silenciosamente, sem exibir nada.
- Contém `Logged in to github.com` mas faltam um ou mais desses escopos → exiba como texto:
  ```
  O gh CLI está autenticado, mas faltam escopos necessários para o Kanban e workflows.

  Rode em um terminal externo (fora do Claude Code):
    gh auth refresh --scopes "gist,project,read:org,repo,workflow"

  Autorize no browser e volte aqui.
  ```
  Use `AskUserQuestion`: `Feito` | `Pular por agora`
- Não contém `Logged in to github.com` → exiba como texto:
  ```
  O gh CLI precisa ser autenticado com os escopos corretos.

  Rode em um terminal externo (fora do Claude Code):
    gh auth login --scopes "gist,project,read:org,repo,workflow"

  Autorize no browser e volte aqui.
  ```
  Use `AskUserQuestion`: `Feito` | `Pular por agora`

---

Use a ferramenta `AskUserQuestion` para coletar as respostas abaixo uma de cada vez:

1. **Nome do repositório** — usar `AskUserQuestion` com as opções fixas `Digitar nome do repositório` e `Cancelar wizard`. O usuário seleciona "Outro" (campo automático do widget) para digitar o nome desejado. Se escolher `Cancelar wizard`, encerre o fluxo.
2. **Visibilidade** — escolha estrita: `Privado` ou `Público` (sem opção de escrita livre)
3. **Modo de configuração** — escolha estrita: `Simples` ou `Avançado (cloud)` (sem opção de escrita livre)
   - **Simples**: cria o repositório, instala dependências (npm + pip)
   - **Avançado**: tudo do simples + perguntas de configuração cloud + gera arquivos de setup
4. **Instalar skills Caveman?** — escolha estrita: `Sim` ou `Não` (sem opção de escrita livre)

Se o usuário escolheu **Avançado**, faça as perguntas adicionais abaixo (uma de cada vez) antes de executar o script:

5. **Habilitar compactação antecipada de contexto?** — escolha estrita: `Sim` ou `Não`
   - Padrão atual: 95%. Recomendado: 70% (compacta mais cedo, menos perda de contexto)
   - Se Sim: edita `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` de `95` para `70` no `settings.json` do filho
6. **Habilitar Agent Teams (múltiplos agentes em paralelo)?** — escolha estrita: `Sim` ou `Não`
   - Permite rodar múltiplos agentes Claude em paralelo no mesmo projeto
   - Se Sim: edita `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` de `0` para `1` no `settings.json` do filho
7. **Gerar setup script para `gh` CLI na VM cloud?** — escolha estrita: `Sim` ou `Não`
   - Gera `scripts/cloud_setup.sh` no filho com instalação de `gh` CLI e autenticação
8. **Gerar Docker Compose para desenvolvimento?** — escolha estrita: `Sim` ou `Não`
   - Gera `docker-compose.yml` base no filho (PostgreSQL + serviços de desenvolvimento)

Após coletar as respostas, verifique se a pasta já existe localmente:
```bash
python -c "from pathlib import Path; p = Path('.').resolve().parent / '<nome>'; print('exists' if p.exists() else 'ok')"
```

Se retornar `exists`, use `AskUserQuestion` para perguntar:
- **Apagar a pasta existente e continuar** — remove a pasta com `rm -rf` e prossiga normalmente (sem `--skip-clone`)
- **Escolher outro nome** — volte à pergunta 1

Se retornar `ok`, prossiga normalmente.

Com as respostas finais, execute:
```bash
python scripts/new_repo.py --name <nome> --visibility <private|public> --yes [--advanced] \
  [--autocompact] [--agent-teams] [--cloud-setup] [--docker] \
  [--caveman | --skip-caveman]
```

- Inclua `--advanced` se o usuário escolheu modo Avançado
- Inclua `--autocompact` se respondeu Sim na pergunta 5
- Inclua `--agent-teams` se respondeu Sim na pergunta 6
- Inclua `--cloud-setup` se respondeu Sim na pergunta 7
- Inclua `--docker` se respondeu Sim na pergunta 8

$ARGUMENTS

---

## Após a criação do repositório (modo Simples)

Informe ao usuário:

> "Repositório enterprise criado. Agora vamos iniciar o projeto corretamente."

Execute imediatamente o comando `/kickoff`.

**Nunca pule o kickoff.** Projetos que começam sem discovery e backlog aprovado acumulam retrabalho.

---

## Após a criação do repositório (modo Avançado)

Guie cada passo abaixo **um de cada vez**: primeiro exiba as instruções como texto markdown normal (para o usuário poder copiar links e comandos), depois use `AskUserQuestion` só para a confirmação.

---

**Passo A — GitHub App**

Exiba como texto:
```
Para que o Claude Code acesse seus repositórios privados na cloud, instale o GitHub App:

  https://github.com/apps/claude

Após instalar: Settings -> Configure -> All repositories
```

Use `AskUserQuestion`:
- Opções: `Feito` | `Pular por agora`

---

**Passo B — Instalar Claude Code CLI**

Exiba como texto:
```
O Claude Code CLI desbloqueia sessões cloud via terminal e os comandos /web-setup e /remote-env.

Em PowerShell externo (escolha um):
  irm https://claude.ai/install.ps1 | iex   (requer Git for Windows)
  winget install Anthropic.ClaudeCode

Após instalar, adicione ao PATH:
  C:\Users\<usuario>\.local\bin
  (Painel de Controle -> Sistema -> Variáveis de Ambiente -> PATH -> reinicie o terminal)
```

Use `AskUserQuestion`:
- Opções: `Feito` | `Já tenho o CLI` | `Pular por agora`

---

**Passo C — /web-setup**

Exiba como texto:
```
Com o CLI instalado e o gh autenticado, execute no terminal do Claude Code:

  /web-setup

Isso sincroniza seu token GitHub com a conta Anthropic. Configuração única por máquina.
```

Use `AskUserQuestion`:
- Opções: `Feito` | `Pular por agora`

---

**Passo D — /remote-env**

Exiba como texto:
```
Execute no terminal do Claude Code para selecionar o ambiente cloud padrão deste projeto:

  /remote-env
```

Use `AskUserQuestion`:
- Opções: `Feito` | `Pular por agora`

Após todos os passos (ou pulados), exiba como texto:

```
Configuração cloud concluída. Como funciona o Claude Code cloud para este projeto:

Você tem dois modos de trabalho:

  Local (seu computador): escreve código, edita documentos, commita
    -> git push para sincronizar com a cloud

  Cloud (VM da Anthropic): Claude roda tarefas pesadas, avança o Kanban,
    revisa entregáveis — sem precisar do seu computador ligado

O git é a ponte: tudo que você pusha fica disponível na cloud.
A VM é descartada ao fechar a sessão — sem estado persistente.

Para abrir uma sessão cloud:
  Browser: claude.ai/code
  Terminal: claude --remote "Run /advance"

Pelo celular:
  App Claude mobile -> Sessions -> monitore ou aprove decisões em background

Para acessar seu PC de fora:
  claude --remote-control  (no terminal local)
  Seu computador vira servidor remoto acessível pelo celular.

Guia completo com configurações avançadas: docs/setup/cloud_guide.md
```

Execute imediatamente o comando `/kickoff`.

**Nunca pule o kickoff.** Projetos que começam sem discovery e backlog aprovado acumulam retrabalho.
