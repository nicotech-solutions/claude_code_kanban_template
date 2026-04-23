# Fix Issue

Dado o seguinte problema ou erro, identifique a causa raiz e aplique a correção mínima necessária.

Não refatore além do escopo do bug. Adicione teste de regressão se aplicável.

## Processo obrigatório

1. **Leia a issue no Kanban** — entenda o escopo antes de agir
2. **Crie um branch** com nome descritivo: `fix/<descricao-curta>`
3. **Implemente a correção mínima** — sem refatorações fora do escopo
4. **Adicione teste de regressão** se aplicável
5. **Abra PR** para revisão do `tech-lead`
6. **Aguarde aprovação** do `tech-lead` antes do merge — o tech-lead deve fazer o review real, não apenas aprovar formalmente
7. **Após merge confirmado**, execute obrigatoriamente o cleanup local:
   ```bash
   git checkout main && git pull && git branch -D <nome-do-branch> 2>/dev/null || true
   ```
8. **Feche a issue** após o merge

## Regras

- Nunca fazer merge do próprio trabalho sem aprovação do `tech-lead`
- O cleanup de branch é obrigatório — sem exceção
- Se o branch já existir remotamente deletado mas não localmente, o comando acima ainda deve ser rodado

$ARGUMENTS
