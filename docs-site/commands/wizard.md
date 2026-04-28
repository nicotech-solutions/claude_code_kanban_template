# /wizard

Cria um novo repositório filho enterprise a partir deste template.

---

## Quando usar

Ao iniciar um novo projeto — é o primeiro command a rodar, antes de qualquer outro.

---

## O que faz

1. Verifica se `gh` CLI está instalado e autenticado com os escopos corretos
2. Coleta: nome do repositório, visibilidade, modo (Simples/Avançado), Caveman
3. Em modo Avançado: coleta opções de cloud (autocompact, agent-teams, cloud-setup, docker)
4. Verifica se a pasta local já existe
5. Executa `python scripts/new_repo.py` com os parâmetros coletados
6. Em modo Avançado: guia configuração cloud (GitHub App, CLI, /web-setup, /remote-env)
7. Executa `/kickoff` automaticamente

---

## Modos

### Simples (recomendado para começar)

- Cria o repositório
- Configura agentes, commands e Kanban
- Instala dependências (npm + pip)
- Inicia `/kickoff`

### Avançado (cloud)

Tudo do Simples, mais:

| Opção | O que faz |
|---|---|
| Autocompact 70% | Compacta contexto mais cedo — menos perda em sessões longas |
| Agent Teams | Habilita múltiplos agentes em paralelo |
| Cloud setup script | Gera `scripts/cloud_setup.sh` para instalar `gh` em VMs |
| Docker Compose | Gera `docker-compose.yml` (PostgreSQL + Redis) |

---

## Argumentos do script

```bash
python scripts/new_repo.py --name <nome> --visibility <private|public> --yes \
  [--advanced] [--autocompact] [--agent-teams] [--cloud-setup] [--docker] \
  [--caveman | --skip-caveman]
```

---

## Escopos necessários no gh CLI

O wizard valida que o token tem todos os escopos obrigatórios:

| Escopo | Para quê |
|---|---|
| `repo` | Criar repositório, push, secrets |
| `read:org` | Listar organizações e membros |
| `gist` | Requerido pelo gh auth para tokens completos |
| `workflow` | Criar e disparar GitHub Actions |
| `project` | Criar e gerenciar GitHub Projects (Kanban) |

Se faltar algum:
```bash
gh auth refresh --scopes "gist,project,read:org,repo,workflow"
```
