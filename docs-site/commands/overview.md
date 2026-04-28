# Commands — Visão geral

Commands são fluxos de trabalho pré-definidos acionados com `/nome`. São arquivos Markdown em `.claude/commands/` que o `project-manager` lê e executa.

---

## Tabela de commands

| Command | Regime | Quando usar |
|---|---|---|
| [`/wizard`](wizard.md) | Setup | Criar novo projeto filho enterprise |
| [`/kickoff`](kickoff.md) | Discovery | Iniciar o projeto — contexto, discovery, backlog |
| [`/advance`](advance.md) | Execução | Avançar no Kanban — fecha prontos, paraleliza, delega |
| [`/review-backlog`](review-backlog.md) | Execução | Board desatualizado, fim de fase, antes de apresentação |
| [`/review`](review.md) | Execução | Code review pontual de PR |
| [`/deploy`](deploy.md) | Execução | Deploy para produção com checklist |
| [`/fix-issue`](fix-issue.md) | Execução | Corrigir bug específico |
| [`/clean`](clean.md) | Qualquer | Commitar e fazer push de tudo pendente |
| [`/update-memory`](update-memory.md) | Qualquer | Atualizar memória do projeto |

---

## Como funcionam

1. O usuário digita `/nome` (com argumentos opcionais)
2. Claude Code carrega o Markdown do command
3. O `project-manager` lê as instruções e as executa
4. Especialistas são acionados via `Task` conforme necessário
5. O PM consolida os resultados e reporta

!!! info "Commands não são código"
    São fluxos em linguagem natural. Não há scripts ou binários — o "motor" é o próprio LLM interpretando as instruções passo a passo.

---

## Regra: sem command, sem ação

Fora de um command ativo, o `project-manager` apenas conversa. Não delega, não cria issues, não commita, não executa nada.

Toda ação concreta requer um `/comando` explícito.
