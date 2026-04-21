# Project Overview

Senior Python project workspace.

## Stack
- Python 3.11+
- Tests: pytest
- Formatting: ruff, black
- Env management: uv or conda

## Conventions
- Type hints em todas as funcoes publicas
- Docstrings apenas quando o "porque" nao e obvio
- Prefira dataclasses ou Pydantic para modelos de dados
- Notebooks em `notebooks/`, codigo reutilizavel em `src/`
- Nunca commitar dados brutos ou modelos pesados - use `.gitignore`

## Architecture Notes
- Scripts CLI usam `typer` ou `argparse`
- Logs estruturados para rastrear execucoes

## What to Avoid
- Nao usar `print()` para debug - use `logging`
- Nao hardcodar paths - use `pathlib.Path`
- Nao misturar logica de negocio com I/O

## Template Usage
- Este repositorio tambem funciona como template para criar novos repositorios no GitHub.
- Neste folder, se o usuario disser `iniciar`, `start`, `novo repo` ou algo equivalente, prefira usar o wizard `python scripts/new_repo.py`.
- Se o usuario pedir para criar um novo projeto a partir deste template, prefira criar um repositorio privado, salvo instrucao contraria.
- Ao criar um novo repositorio a partir do template, configurar o secret `GH_PAT` no repositorio novo antes de depender da criacao do GitHub Project.
- Depois de configurar `GH_PAT`, rodar a workflow `Setup Kanban`.
- Comando padrao do wizard: `python scripts/new_repo.py`
- Validar ao final:
- existe um project com nome `<repo> Kanban`
- o project aparece na aba `Projects` do repositorio
- existem as views `Board`, `Table` e `Done`
- a issue `Getting Started` existe
- a issue `Getting Started` foi adicionada ao project com status `Todo`

## Template Notes
- No primeiro push do repositorio criado a partir do template, a workflow pode executar antes de `GH_PAT` estar configurado.
- Nessa situacao, a workflow deve continuar sem falhar e apenas pular a criacao do GitHub Project.
- Depois que `GH_PAT` existir, rodar `Setup Kanban` manualmente para criar o project e as views.
- A API atual do GitHub permite criar a view `Board`, mas o agrupamento visual por `Status` pode ainda exigir ajuste manual na interface do GitHub.
