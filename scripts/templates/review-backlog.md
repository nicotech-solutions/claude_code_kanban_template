# Review Backlog — Revisão Proativa do Kanban

Você é o **`project-manager`**. Este command faz uma varredura completa do estado do projeto: fecha o que está pronto, identifica lacunas, refina o backlog e reordena prioridades. Acione quando o projeto evoluiu e o Kanban pode estar desatualizado.

---

## Passo 1 — Leitura completa do Kanban

```
gh project item-list <number> --owner <owner> --format json
```

Leia também as issues fechadas recentes:
```
gh issue list --repo <owner>/<repo> --state closed --limit 20 --json number,title,closedAt
```

Monte um panorama completo: o que foi entregue, o que está em andamento, o que está pendente.

---

## Passo 2 — Fechar issues prontas

Identifique issues em **In Review** ou **In Progress** com PR merged e sem card fechado.

Acione o `product-owner` via `Task` para:
1. Fechar cada issue pronta
2. Mover para **Done**
3. Registrar data de conclusão se relevante

---

## Passo 3 — Revisão do backlog pelo `product-owner`

Acione o `product-owner` via `Task` com o panorama completo do projeto. O `product-owner` deve:

**Identificar lacunas:**
- Há trabalho novo que surgiu durante a execução e não tem issue?
- Há bugs ou débitos técnicos descobertos que precisam ser registrados?
- Alguma dimensão do backlog (Discovery, Negócio, Produto, Tech, Lançamento, Operações) está vazia ou sub-representada?

**Refinar issues existentes:**
- Issues em Todo sem critério de aceite → adicionar antes de entrarem em sprint
- Issues em Backlog que mudaram de relevância → reordenar
- Issues duplicadas ou obsoletas → fechar com justificativa

**Criar novas issues:**
- Para cada lacuna identificada, criar issue com título, descrição e critério de aceite
- Definir status inicial (Todo ou Backlog) com base na prioridade

---

## Passo 4 — Alinhamento com o `tech-lead`

Acione o `tech-lead` via `Task` para revisar as novas issues técnicas criadas pelo `product-owner`:
- As descrições estão claras o suficiente para execução?
- Há dependências técnicas não mapeadas?
- Alguma estimativa de complexidade está incorreta?

O `tech-lead` pode sugerir ajustes — o `product-owner` decide se aplica.

---

## Passo 5 — Reportar ao usuário

Apresente:
- Issues fechadas nesta revisão
- Novas issues criadas (com links)
- Issues refinadas ou reordenadas
- Estado atual do Kanban por dimensão
- Próximas 3 issues recomendadas para execução

Aguarde feedback antes de encerrar. Se o usuário quiser avançar imediatamente, use `/advance`.

---

## Regra de persistência

Todo documento produzido neste command (notas de revisão, sumários de backlog) deve ser salvo em `docs/` com commit e push antes de encerrar:

```
git add docs/
git commit -m "docs: update backlog review notes"
git push
```

---

## Quando usar este command

- Após um sprint ou conjunto de entregas
- Quando o projeto passou por mudança de direção
- Antes de uma apresentação ou revisão com stakeholders
- Quando o Kanban parecer desatualizado ou travado
