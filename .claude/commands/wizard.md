# Wizard — Criar Novo Repositório

Use a ferramenta `AskUserQuestion` para coletar as respostas abaixo uma de cada vez:

1. **Nome do repositório** — campo de texto livre (permitir escrita livre)
2. **Visibilidade** — escolha estrita: `Privado` ou `Público` (sem opção de escrita livre)
3. **Instalar skills Caveman?** — escolha estrita: `Sim` ou `Não` (sem opção de escrita livre)

Após coletar o nome, verifique se a pasta já existe localmente:
```bash
python -c "from pathlib import Path; p = Path('.').resolve().parent / '<nome>'; print('exists' if p.exists() else 'ok')"
```

Se retornar `exists`, use `AskUserQuestion` para perguntar:
- **Apagar a pasta existente e continuar** — remove a pasta com `rm -rf` e prossiga normalmente (sem `--skip-clone`)
- **Escolher outro nome** — volte à pergunta 1

Se retornar `ok`, prossiga normalmente.

Com as respostas finais, execute:
```bash
python scripts/new_repo.py --name <nome> --visibility <private|public> --yes [--caveman | --skip-caveman]
```

$ARGUMENTS

---

## Após a criação do repositório

Quando o wizard concluir com sucesso, informe ao usuário:

> "Repositório criado. Agora vamos iniciar o projeto corretamente."

Em seguida, execute imediatamente o comando `/kickoff` para:
1. Entender o problema que o projeto resolve
2. Montar o backlog completo (negócio + produto + tech + marketing)
3. Obter aprovação antes de qualquer execução

**Nunca pule o kickoff.** Projetos que começam sem discovery e backlog aprovado acumulam retrabalho.
