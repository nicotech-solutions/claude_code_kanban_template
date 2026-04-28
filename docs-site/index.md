# Claude Code Enterprise Template

**Sistema multi-agente para projetos enterprise** construído sobre o Claude Code CLI.

---

## O que é isso?

O `claude-code-enterprise-template` é um repositório-modelo que transforma o Claude Code em um **ambiente de desenvolvimento colaborativo com equipe de agentes especializados**. Em vez de um único assistente respondendo perguntas, você tem uma equipe de 12 agentes — cada um com papel, permissões e responsabilidades definidas — trabalhando em conjunto para conduzir um projeto do discovery ao lançamento.

!!! tip "Para quem é?"
    Times de produto e engenharia que querem usar IA de forma estruturada e auditável em projetos de longa duração — startups, projetos internos, MVPs e plataformas enterprise.

---

## Principais características

- **12 agentes especializados** — do project-manager ao security-auditor, do data-engineer ao frontend-engineer
- **Kanban integrado ao GitHub Projects** — nenhum trabalho acontece sem issue no board
- **Versionamento explícito de documentos** — `{nome}_YYYY-MM-DD_v{N}.md`, sem sobrescrita
- **Dois regimes de trabalho** — Discovery (`/kickoff`) e Execução (`/advance`)
- **Memória persistente** — o projeto lembra decisões, restrições e histórico entre sessões
- **Hooks automáticos** — formatação, geração de PDF/DOCX, validação de convenções
- **Rastreabilidade total** — commits, PRs e issues ligados; sessions cloud identificáveis

---

## Como usar este site

| Você quer... | Vá para... |
|---|---|
| Criar um projeto em 5 minutos | [Início rápido](quickstart.md) |
| Entender como tudo se encaixa | [Arquitetura](architecture/overview.md) |
| Ver o fluxo completo do kickoff | [Discovery](flow/discovery.md) |
| Saber o que cada agente faz | [Agentes](agents/overview.md) |
| Consultar um command específico | [Commands](commands/overview.md) |
| Ver como os agentes interagem | [Interações](interactions.md) |
| Regras de nomenclatura e branches | [Convenções](conventions.md) |

---

## Início imediato

```bash
# 1. Clone o template
git clone https://github.com/ggnicolau/claude-code-enterprise-template.git
cd claude-code-enterprise-template

# 2. Configure o ambiente
uv sync
cp .env.example .env
# edite .env com GH_TOKEN

# 3. Abra no Claude Code
claude

# 4. O wizard cria o projeto filho e inicia o kickoff automaticamente
/wizard
```
