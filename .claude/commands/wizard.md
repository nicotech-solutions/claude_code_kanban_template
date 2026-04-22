# Wizard — Criar Novo Repositório

Use a ferramenta `AskUserQuestion` para coletar as respostas abaixo uma de cada vez:

1. **Nome do repositório** — campo de texto livre
2. **Visibilidade** — escolha: `Privado` ou `Público`
3. **Instalar skills Caveman?** — escolha: `Sim` ou `Não`

Com as respostas, execute:
```bash
python scripts/new_repo.py --name <nome> --visibility <private|public> --yes [--caveman | --skip-caveman]
```

$ARGUMENTS
