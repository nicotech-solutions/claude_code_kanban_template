# {repo_name}

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
