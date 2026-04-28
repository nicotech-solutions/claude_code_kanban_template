from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MCP_CONFIG_PATH = ROOT / ".mcp.json"
SETUP_KANBAN_WORKFLOW_NAME = "Setup Kanban"
SETUP_KANBAN_WORKFLOW_FILE = "setup-kanban.yml"


def run_command(command: list[str], env: dict[str, str]) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def load_env() -> dict[str, str]:
    env = os.environ.copy()
    if env.get("GH_TOKEN"):
        return env

    dot_env_path = ROOT / ".env"
    if dot_env_path.exists():
        for line in dot_env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                env.setdefault(key.strip(), value.strip())
    if env.get("GH_TOKEN"):
        return env

    if MCP_CONFIG_PATH.exists():
        data = json.loads(MCP_CONFIG_PATH.read_text(encoding="utf-8"))
        auth_header = (
            data.get("mcpServers", {})
            .get("github", {})
            .get("headers", {})
            .get("Authorization", "")
        )
        if auth_header.startswith("Bearer "):
            env["GH_TOKEN"] = auth_header.removeprefix("Bearer ").strip()
    return env


# IMPORTANTE: Nunca remova escopos deste set sem entender o impacto.
# Cada escopo é obrigatório para uma parte do wizard:
#   repo      — criar repositório, push, secrets
#   read:org  — listar organizações e membros
#   gist      — requerido pelo gh auth para tokens com permissões completas
#   workflow  — criar/disparar GitHub Actions workflows
#   project   — criar e gerenciar GitHub Projects (Kanban)
# Se o token ativo não tiver um escopo, o wizard exibe instrução para
# rodar `gh auth refresh --scopes "gist,project,read:org,repo,workflow"`
# e NUNCA deve remover o escopo da lista para contornar a validação.
REQUIRED_SCOPES = {"repo", "read:org", "gist", "workflow", "project"}


def is_gh_installed() -> bool:
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=False)
        return True
    except FileNotFoundError:
        return False


def check_gh_scopes(env: dict[str, str]) -> set[str]:
    """Return the set of OAuth scopes the active gh token has."""
    result = subprocess.run(
        ["gh", "auth", "status"],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    output = result.stdout + result.stderr
    for line in output.splitlines():
        if "Token scopes:" in line:
            raw = line.split("Token scopes:", 1)[1]
            return {s.strip().strip("'\"") for s in raw.split(",")}
    return set()


def ensure_gh_scopes(env: dict[str, str]) -> None:
    """Exit with instructions if gh is missing or any required scope is absent."""
    if not is_gh_installed():
        print()
        print("Erro: gh CLI nao encontrado.")
        print()
        print("Instale em um terminal externo (fora do Claude Code):")
        print("  winget install GitHub.cli")
        print()
        print("Depois execute o wizard novamente.")
        sys.exit(1)

    present = check_gh_scopes(env)
    missing = REQUIRED_SCOPES - present
    if not missing:
        return

    scopes_str = ",".join(sorted(REQUIRED_SCOPES))
    authenticated = bool(present)
    print()
    print("Erro: o token do GitHub nao tem todos os escopos necessarios.")
    print(f"  Faltando: {', '.join(sorted(missing))}")
    print()
    print("Rode em um terminal externo (fora do Claude Code):")
    if authenticated:
        print(f'  gh auth refresh --scopes "{scopes_str}"')
    else:
        print(f'  gh auth login --scopes "{scopes_str}"')
    print()
    print("Autorize no browser e execute o wizard novamente.")
    sys.exit(1)


def bootstrap_local_credentials(env: dict[str, str]) -> dict[str, str]:
    """Garante que .env e .mcp.json existem localmente com o token ativo do gh."""
    if env.get("GH_TOKEN"):
        token = env["GH_TOKEN"]
    else:
        result = subprocess.run(
            ["gh", "auth", "token"],
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        token = result.stdout.strip()

    if not token:
        return env

    dot_env = ROOT / ".env"
    if not dot_env.exists():
        dot_env.write_text(f"GH_TOKEN={token}\n", encoding="utf-8")
        print("- .env criado com GH_TOKEN.")

    mcp_json = ROOT / ".mcp.json"
    if not mcp_json.exists():
        import json as _json
        mcp_content = {
            "mcpServers": {
                "github": {
                    "type": "http",
                    "url": "https://api.githubcopilot.com/mcp",
                    "headers": {"Authorization": f"Bearer {token}"},
                }
            }
        }
        mcp_json.write_text(_json.dumps(mcp_content, indent=2), encoding="utf-8")
        print("- .mcp.json criado com token GitHub.")

    env = env.copy()
    env["GH_TOKEN"] = token
    return env


@dataclass(slots=True)
class ValidationReport:
    repo_url: str
    project_url: str
    project_linked_to_repo: bool
    board_exists: bool
    table_exists: bool
    done_exists: bool
    getting_started_exists: bool
    issue_in_project: bool
    issue_status: str

    @property
    def is_valid(self) -> bool:
        return all(
            [
                bool(self.project_url),
                self.project_linked_to_repo,
                self.board_exists,
                self.table_exists,
                self.done_exists,
                self.getting_started_exists,
                self.issue_in_project,
                self.issue_status == "Todo",
            ]
        )


def parse_origin_repo(env: dict[str, str]) -> str:
    origin_url = run_command(["git", "config", "--get", "remote.origin.url"], env)
    match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)", origin_url)
    if not match:
        raise RuntimeError(
            "Nao foi possivel identificar o repositorio de origem do template."
        )
    return f"{match.group('owner')}/{match.group('repo')}"


def prompt_text(label: str, default: str | None = None, required: bool = True) -> str:
    while True:
        suffix = f" [{default}]" if default else ""
        value = input(f"{label}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default
        if not required:
            return ""
        print("Valor obrigatorio. Tente novamente.")


def prompt_choice(label: str, options: list[tuple[str, str]], default_key: str) -> str:
    print(label)
    for index, (_, description) in enumerate(options, start=1):
        print(f"{index}. {description}")

    keys = [key for key, _ in options]
    default_index = keys.index(default_key) + 1

    while True:
        raw_value = input(f"Escolha uma opcao [{default_index}]: ").strip()
        if not raw_value:
            return default_key
        if raw_value.isdigit():
            index = int(raw_value) - 1
            if 0 <= index < len(options):
                return options[index][0]
        lowered = raw_value.lower()
        if lowered in keys:
            return lowered
        print("Opcao invalida. Tente novamente.")


def build_repo_name(raw_name: str) -> str:
    sanitized = re.sub(r"[^a-zA-Z0-9._-]+", "-", raw_name.strip())
    sanitized = re.sub(r"-{2,}", "-", sanitized).strip("-")
    if not sanitized:
        raise ValueError("Nome de repositorio invalido.")
    return sanitized


def maybe_set_secret(
    env: dict[str, str],
    full_name: str,
    secret_name: str,
    secret_value: str,
) -> None:
    process = subprocess.run(
        ["gh", "secret", "set", secret_name, "--repo", full_name],
        cwd=ROOT,
        env=env,
        text=True,
        input=secret_value,
        capture_output=True,
        check=False,
    )
    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip())


def maybe_run_workflow(env: dict[str, str], full_name: str, workflow_name: str) -> str:
    workflow_identifier = resolve_workflow_identifier(
        env=env,
        full_name=full_name,
        workflow_name=workflow_name,
        workflow_file=SETUP_KANBAN_WORKFLOW_FILE,
    )
    return run_command(
        ["gh", "workflow", "run", workflow_identifier, "--repo", full_name],
        env,
    )


def list_workflows(env: dict[str, str], full_name: str) -> list[dict[str, object]]:
    output = run_command(
        ["gh", "api", f"repos/{full_name}/actions/workflows"],
        env,
    )
    return json.loads(output).get("workflows", [])


def clone_repo_locally(env: dict[str, str], full_name: str, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    return run_command(["gh", "repo", "clone", full_name, str(destination)], env)


# Arquivos que existem apenas no template e não fazem sentido em projetos reais
TEMPLATE_ONLY_FILES = [
    "scripts/new_repo.py",
    "scripts/verify.sh",
    "tests/test_new_repo.py",
    ".claude/commands/wizard.md",
    ".claude/commands/sync-to-projects.md",
    ".claude/commands/sync-to-template.md",
    "AGENTS.md",
    # coordinator is Claude reading CLAUDE.md — children don't need this agent file
    ".claude/agents/template-coordinator.md",
]

TEMPLATE_ONLY_DIRS = [
    "scripts/templates",
    "meta",
]


def cleanup_template_files(destination: Path, repo_name: str) -> None:
    """Remove arquivos de template e gera CLAUDE.md e AGENTS.md para o projeto."""
    import shutil
    import subprocess

    # Remove arquivos específicos do template
    removed = []
    for rel_path in TEMPLATE_ONLY_FILES:
        target = destination / rel_path
        if target.exists():
            target.unlink()
            removed.append(rel_path)

    # Remove diretórios exclusivos do template
    for rel_path in TEMPLATE_ONLY_DIRS:
        target = destination / rel_path
        if target.exists():
            shutil.rmtree(target)
            removed.append(rel_path)

    # Gera CLAUDE.md e AGENTS.md a partir dos templates
    templates_dir = ROOT / "scripts" / "templates"
    for tpl_name in ("CLAUDE.md", "AGENTS.md"):
        tpl_path = templates_dir / tpl_name
        if tpl_path.exists():
            content = tpl_path.read_text(encoding="utf-8").replace(
                "{repo_name}", repo_name
            )
            (destination / tpl_name).write_text(content, encoding="utf-8")

    # Copia README.md para o filho
    readme_tpl = templates_dir / "README.md"
    if readme_tpl.exists():
        (destination / "README.md").write_text(
            readme_tpl.read_text(encoding="utf-8").replace("{repo_name}", repo_name),
            encoding="utf-8",
        )

    # Copia todos os commands de scripts/templates/commands/ para .claude/commands/ do filho
    commands_dir = templates_dir / "commands"
    if commands_dir.exists():
        dest_commands = destination / ".claude" / "commands"
        dest_commands.mkdir(parents=True, exist_ok=True)
        for cmd_file in commands_dir.glob("*.md"):
            (dest_commands / cmd_file.name).write_text(
                cmd_file.read_text(encoding="utf-8"), encoding="utf-8"
            )

    # Copia agents de scripts/templates/agents/ para .claude/agents/ do filho
    agents_tpl = templates_dir / "agents"
    if agents_tpl.exists():
        dest_agents = destination / ".claude" / "agents"
        dest_agents.mkdir(parents=True, exist_ok=True)
        for agent_file in agents_tpl.glob("*.md"):
            (dest_agents / agent_file.name).write_text(
                agent_file.read_text(encoding="utf-8"), encoding="utf-8"
            )

    # Copia package.json do template para o filho (deps do gerador de docs)
    pkg_tpl = templates_dir / "package.json"
    if pkg_tpl.exists():
        (destination / "package.json").write_text(
            pkg_tpl.read_text(encoding="utf-8"), encoding="utf-8"
        )

    # Copia styles/ do template para scripts/templates/styles no filho
    styles_tpl = templates_dir / "styles"
    if styles_tpl.exists():
        dest_styles = destination / "scripts" / "templates" / "styles"
        dest_styles.mkdir(parents=True, exist_ok=True)
        for style_file in styles_tpl.iterdir():
            if style_file.is_file():
                (dest_styles / style_file.name).write_text(
                    style_file.read_text(encoding="utf-8"), encoding="utf-8"
                )

    # Copia .gitattributes para scripts/templates/ do filho
    gitattributes_tpl = templates_dir / ".gitattributes"
    if gitattributes_tpl.exists():
        dest_templates_dir = destination / "scripts" / "templates"
        dest_templates_dir.mkdir(parents=True, exist_ok=True)
        (dest_templates_dir / ".gitattributes").write_text(
            gitattributes_tpl.read_text(encoding="utf-8"), encoding="utf-8"
        )

    # Copia o gerador de docs (scripts/generate_docs.js) para o filho
    gen_src = ROOT / "scripts" / "generate_docs.js"
    if gen_src.exists():
        dest_scripts = destination / "scripts"
        dest_scripts.mkdir(parents=True, exist_ok=True)
        (dest_scripts / "generate_docs.js").write_text(
            gen_src.read_text(encoding="utf-8"), encoding="utf-8"
        )

    # Copia arquivos example do template para o filho
    for example_file in (
        ".env.example",
        ".mcp.json.example",
        "CLAUDE.local.md.example",
    ):
        src = ROOT / example_file
        if src.exists():
            (destination / example_file).write_text(
                src.read_text(encoding="utf-8"), encoding="utf-8"
            )

    # Copia credenciais reais se existirem (gitignored — não vão para o repo)
    for cred_file in (".env", ".mcp.json"):
        src = ROOT / cred_file
        if src.exists():
            (destination / cred_file).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    subprocess.run(
        ["git", "add", "-A"], cwd=destination, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "chore: initialize project files from template"],
        cwd=destination,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "push"], cwd=destination, check=True, capture_output=True)

    # Cria branch dev a partir de main
    subprocess.run(
        ["git", "checkout", "-b", "dev"],
        cwd=destination,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "push", "-u", "origin", "dev"],
        cwd=destination,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "checkout", "main"], cwd=destination, check=True, capture_output=True
    )

    if removed:
        print(f"- Arquivos de template removidos: {', '.join(removed)}")
    print("- CLAUDE.md e AGENTS.md gerados para o projeto.")
    print("- Branch 'dev' criado e publicado.")


def build_local_clone_path(repo_name: str, base_dir: Path | None = None) -> Path:
    return (base_dir or ROOT.parent) / repo_name


def ensure_local_clone_absent(destination: Path) -> None:
    if destination.exists():
        raise RuntimeError(
            f"A pasta local {destination} ja existe. Use outro nome ou mova/remova a pasta."
        )


def resolve_workflow_identifier(
    env: dict[str, str],
    full_name: str,
    workflow_name: str,
    workflow_file: str,
    retries: int = 5,
    delay_seconds: float = 2.0,
) -> str:
    last_seen: list[str] = []
    expected_path = f".github/workflows/{workflow_file}"
    for attempt in range(retries):
        workflows = list_workflows(env, full_name)
        last_seen = [
            str(
                workflow.get("name") or workflow.get("path") or workflow.get("id") or ""
            )
            for workflow in workflows
        ]
        for workflow in workflows:
            name = str(workflow.get("name", ""))
            path = str(workflow.get("path", ""))
            if (
                name == workflow_name
                or path == expected_path
                or path.endswith(f"/{expected_path}")
            ):
                return str(workflow["id"])
        if attempt < retries - 1:
            time.sleep(delay_seconds)
    available = ", ".join(last_seen) if last_seen else "nenhuma workflow encontrada"
    raise RuntimeError(
        f"Workflow {workflow_name!r} nao encontrada em {full_name}. Disponiveis: {available}"
    )


def find_project(env: dict[str, str], project_title: str) -> str:
    query = (
        "query { viewer { projectsV2(first: 100, orderBy: {field: TITLE, direction: ASC}) "
        "{ nodes { title url closed } } } }"
    )
    output = run_command(["gh", "api", "graphql", "-f", f"query={query}"], env)
    data = json.loads(output)
    for node in data["data"]["viewer"]["projectsV2"]["nodes"]:
        if node["title"] == project_title and not node["closed"]:
            return node["url"]
    return ""


def wait_for_project_url(
    env: dict[str, str],
    project_title: str,
    *,
    max_wait_seconds: int = 45,
    poll_interval: int = 5,
) -> str:
    """Polls find_project() until the project appears or timeout. Returns URL or empty string."""
    deadline = time.monotonic() + max_wait_seconds
    attempt = 0
    while time.monotonic() < deadline:
        url = find_project(env, project_title)
        if url:
            return url
        attempt += 1
        if attempt == 1:
            print(f"\nAguardando criacao do GitHub Project (ate {max_wait_seconds}s)...")
        time.sleep(poll_interval)
    return ""


def list_repo_issues(env: dict[str, str], full_name: str) -> list[dict[str, object]]:
    output = run_command(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            full_name,
            "--json",
            "number,title,state",
        ],
        env,
    )
    return json.loads(output)


def summarize_validation(
    env: dict[str, str],
    full_name: str,
    project_title: str,
    *,
    max_wait_seconds: int = 90,
    poll_interval: int = 10,
) -> None:
    deadline = time.monotonic() + max_wait_seconds
    attempt = 0
    report = build_validation_report(env, full_name, project_title)
    while not report.is_valid and time.monotonic() < deadline:
        attempt += 1
        if attempt == 1:
            print(
                f"\nAguardando workflow Setup Kanban concluir (ate {max_wait_seconds}s)..."
            )
        time.sleep(poll_interval)
        report = build_validation_report(env, full_name, project_title)

    print("\nValidacao")
    print(f"- Repositorio: {report.repo_url}")
    print(f"- Project: {report.project_url or 'nao encontrado'}")
    print(
        "- Project listado na aba Projects do repo: "
        f"{'ok' if report.project_linked_to_repo else 'faltando'}"
    )
    print(f"- View Board: {'ok' if report.board_exists else 'faltando'}")
    print(f"- View Table: {'ok' if report.table_exists else 'faltando'}")
    print(f"- View Done: {'ok' if report.done_exists else 'faltando'}")
    print(
        "- Issue Getting Started: "
        f"{'ok' if report.getting_started_exists else 'nao encontrada'}"
    )
    print(
        "- Issue no project: "
        f"{'ok' if report.issue_in_project else 'nao adicionada ao project'}"
    )
    print(f"- Status da issue: {report.issue_status or 'nao definido'}")

    if not report.is_valid:
        raise RuntimeError("Validacao final falhou.")


def build_validation_report(
    env: dict[str, str],
    full_name: str,
    project_title: str,
) -> ValidationReport:
    query = """
    query {
      viewer {
        projectsV2(first: 100, orderBy: {field: TITLE, direction: ASC}) {
          nodes {
            title
            url
            closed
            repositories(first: 20) {
              nodes {
                nameWithOwner
              }
            }
            views(first: 20) {
              nodes {
                name
              }
            }
            items(first: 100) {
              nodes {
                content {
                  __typename
                  ... on Issue {
                    title
                    number
                  }
                }
                fieldValues(first: 20) {
                  nodes {
                    __typename
                    ... on ProjectV2ItemFieldSingleSelectValue {
                      name
                      field {
                        ... on ProjectV2SingleSelectField {
                          name
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    output = run_command(["gh", "api", "graphql", "-f", f"query={query}"], env)
    data = json.loads(output)
    projects = data["data"]["viewer"]["projectsV2"]["nodes"]
    project = next(
        (
            node
            for node in projects
            if node["title"] == project_title and not node["closed"]
        ),
        None,
    )
    issues = list_repo_issues(env, full_name)
    issue = next((item for item in issues if item["title"] == "Getting Started"), None)
    project_linked_to_repo = any(
        node.get("nameWithOwner") == full_name
        for node in (project or {}).get("repositories", {}).get("nodes", [])
    )

    view_names = {
        node["name"]
        for node in (project or {}).get("views", {}).get("nodes", [])
        if node.get("name")
    }
    issue_in_project = False
    issue_status = ""
    if project and issue:
        for item in project["items"]["nodes"]:
            content = item.get("content") or {}
            if (
                content.get("__typename") == "Issue"
                and content.get("number") == issue["number"]
            ):
                issue_in_project = True
                for field_value in item.get("fieldValues", {}).get("nodes", []):
                    field = field_value.get("field") or {}
                    if (
                        field_value.get("__typename")
                        == "ProjectV2ItemFieldSingleSelectValue"
                        and field.get("name") == "Status"
                    ):
                        issue_status = str(field_value.get("name", ""))
                        break
                break

    return ValidationReport(
        repo_url=f"https://github.com/{full_name}",
        project_url=project["url"] if project else "",
        project_linked_to_repo=project_linked_to_repo,
        board_exists="Board" in view_names,
        table_exists="Table" in view_names,
        done_exists="Done" in view_names,
        getting_started_exists=issue is not None,
        issue_in_project=issue_in_project,
        issue_status=issue_status,
    )


CAVEMAN_SKILL_CONTENT = """\
---
name: caveman
description: >
  Ultra-compressed communication mode. Cuts token usage ~75% by speaking like caveman
  while keeping full technical accuracy. Supports intensity levels: lite, full (default), ultra.
  Use when user says "caveman mode", "talk like caveman", "use caveman", "less tokens",
  "be brief", or invokes /caveman.
---

Respond terse like smart caveman. All technical substance stay. Only fluff die.

## Persistence

ACTIVE EVERY RESPONSE. No revert after many turns. Off only: "stop caveman" / "normal mode".

Default: **full**. Switch: `/caveman lite|full|ultra`.

## Rules

Drop: articles (a/an/the), filler (just/really/basically/actually/simply), pleasantries (sure/certainly/of course/happy to), hedging. Fragments OK. Short synonyms (big not extensive, fix not "implement a solution for"). Technical terms exact. Code blocks unchanged.

Pattern: `[thing] [action] [reason]. [next step].`

Not: "Sure! I'd be happy to help you with that. The issue you're experiencing is likely caused by..."
Yes: "Bug in auth middleware. Token expiry check use `<` not `<=`. Fix:"

## Intensity

| Level | What changes |
|-------|-------------|
| **lite** | No filler/hedging. Keep articles + full sentences. Professional but tight |
| **full** | Drop articles, fragments OK, short synonyms. Classic caveman |
| **ultra** | Abbreviate (DB/auth/config/req/res/fn/impl), strip conjunctions, arrows for causality (X -> Y) |

## Boundaries

Code/commits/PRs: write normal. Security warnings and destructive op confirmations: full sentences. Resume caveman after.
"""


CAVEMAN_COMMIT_SKILL_CONTENT = """\
---
name: caveman-commit
description: >
  Ultra-compressed commit message generator. Conventional Commits format. Subject <= 50 chars,
  body only when "why" isn't obvious. Use when user says "write a commit", "commit message",
  "generate commit", "/commit", or invokes /caveman-commit. Auto-triggers when staging changes.
---

Write commit messages terse and exact. Conventional Commits format. No fluff. Why over what.

## Rules

**Subject line:**
- `<type>(<scope>): <imperative summary>` - `<scope>` optional
- Types: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`, `build`, `ci`, `style`, `revert`
- Imperative mood: "add", "fix", "remove" - not "added", "adds", "adding"
- <=50 chars when possible, hard cap 72
- No trailing period

**Body (only if needed):**
- Skip when subject is self-explanatory
- Add body only for: non-obvious *why*, breaking changes, migration notes, linked issues
- Wrap at 72 chars. Bullets `-` not `*`
- Reference issues/PRs at end: `Closes #42`, `Refs #17`

**Never include:**
- "This commit does X", "I", "we", "now", "currently"
- "Generated with Claude Code" or any AI attribution
- Emoji (unless project convention requires)

## Auto-Clarity

Always include body for: breaking changes, security fixes, data migrations, reverts.

## Boundaries

Only generates the message as a code block. Does not run `git commit`. "stop caveman-commit": revert to verbose style.
"""

CAVEMAN_REVIEW_SKILL_CONTENT = """\
---
name: caveman-review
description: >
  Ultra-compressed code review comments. Each comment is one line: location, problem, fix.
  Use when user says "review this PR", "code review", "review the diff", "/review", or
  invokes /caveman-review. Auto-triggers when reviewing pull requests.
---

Write code review comments terse and actionable. One line per finding. Location, problem, fix. No throat-clearing.

## Rules

**Format:** `L<line>: <problem>. <fix>.` or `<file>:L<line>: ...` for multi-file diffs.

**Severity prefix:**
- `red bug:` - broken behavior, will cause incident
- `yellow risk:` - works but fragile (race, missing null check, swallowed error)
- `blue nit:` - style, naming, micro-optim. Author can ignore
- `q:` - genuine question, not a suggestion

**Drop:**
- "I noticed that...", "It seems like...", "You might want to consider..."
- "Great work!", "Looks good overall but..."
- Hedging ("perhaps", "maybe", "I think") - use `q:` instead

**Keep:**
- Exact line numbers and symbol names in backticks
- Concrete fix, not "consider refactoring"
- The *why* if fix isn't obvious

## Auto-Clarity

Drop terse for: CVE-class security findings, architectural disagreements, onboarding contexts.

## Boundaries

Reviews only - does not write the fix, does not approve/request-changes. "stop caveman-review": revert to verbose style.
"""


def install_caveman_skill(destination: Path) -> None:
    skills_base = destination / ".agents" / "skills"
    for name, content in [
        ("caveman", CAVEMAN_SKILL_CONTENT),
        ("caveman-commit", CAVEMAN_COMMIT_SKILL_CONTENT),
        ("caveman-review", CAVEMAN_REVIEW_SKILL_CONTENT),
    ]:
        skill_dir = skills_base / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")


def ensure_repo_absent(env: dict[str, str], full_name: str) -> None:
    result = subprocess.run(
        ["gh", "repo", "view", full_name, "--json", "nameWithOwner"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        raise RuntimeError(f"O repositorio {full_name} ja existe.")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Wizard para criar um novo repositorio a partir deste template."
    )
    parser.add_argument("--name", help="Nome do novo repositorio.")
    parser.add_argument(
        "--visibility",
        choices=["private", "public"],
        help="Visibilidade do novo repositorio.",
    )
    parser.add_argument("--description", default=None, help="Descricao do repositorio.")
    parser.add_argument(
        "--template-branch",
        default=None,
        help="Branch do template a usar como base do repo novo. Default: branch atual do template.",
    )
    parser.add_argument(
        "--skip-secret",
        action="store_true",
        help="Nao configura o secret GH_PAT no repositorio novo.",
    )
    parser.add_argument(
        "--skip-workflow",
        action="store_true",
        help="Nao roda a workflow Setup Kanban apos criar o repositorio.",
    )
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="Nao roda a validacao final.",
    )
    parser.add_argument(
        "--skip-clone",
        action="store_true",
        help="Nao clona o repositorio novo localmente.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirma automaticamente a criacao sem pedir aprovacao final.",
    )
    parser.add_argument(
        "--advanced",
        action="store_true",
        help="Modo avancado: gera cloud_guide.md e exibe orientacoes /web-setup + GitHub App.",
    )
    parser.add_argument(
        "--cloud-setup",
        action="store_true",
        help="Gera scripts/cloud_setup.sh com instalacao de gh CLI para VM cloud.",
    )
    parser.add_argument(
        "--autocompact",
        action="store_true",
        help="Adiciona CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=70 ao settings.json do filho.",
    )
    parser.add_argument(
        "--agent-teams",
        action="store_true",
        help="Adiciona CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 ao settings.json do filho.",
    )
    parser.add_argument(
        "--docker",
        action="store_true",
        help="Gera docker-compose.yml base para desenvolvimento.",
    )
    caveman_group = parser.add_mutually_exclusive_group()
    caveman_group.add_argument(
        "--caveman",
        action="store_true",
        default=None,
        help="Instala o skill Caveman no repositorio novo.",
    )
    caveman_group.add_argument(
        "--skip-caveman",
        action="store_true",
        help="Nao instala o skill Caveman.",
    )
    return parser.parse_args(list(argv))


def detect_template_branch() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip() or "main"


def is_interactive() -> bool:
    return sys.stdin.isatty()


def should_confirm_creation(args: argparse.Namespace, interactive: bool) -> bool:
    return interactive and not args.yes


def should_prompt(args: argparse.Namespace, interactive: bool) -> bool:
    return interactive and not args.yes


def generate_cloud_guide(destination: Path, repo_name: str) -> None:
    """Gera docs/setup/cloud_guide.md com instruções para configuração cloud."""
    content = f"""\
# Guia de Configuração Cloud — {repo_name}

Este guia cobre a configuração do Claude Code para uso em sessões cloud (VMs remotas da Anthropic).

## 1. Conectar conta GitHub ao Claude Code (`/web-setup`)

Execute uma vez no Claude Code (web ou desktop):

```
/web-setup
```

Isso sincroniza seu token GitHub com a sessão cloud. Sem isso, operações `gh` não funcionam em VMs remotas.

**Quando rodar:** apenas uma vez por conta Anthropic. Persiste entre sessões.

## 2. Instalar o GitHub App

Acesse e instale o app do Claude Code na sua conta/organização GitHub:

> https://github.com/apps/claude

Permissões necessárias: leitura de repositórios, leitura de issues/PRs.

**Quando usar:** obrigatório para que o Claude Code em cloud acesse repositórios privados.

## 3. Selecionar ambiente cloud padrão (`/remote-env`)

No Claude Code web/desktop, execute:

```
/remote-env
```

Selecione o ambiente cloud padrão para este projeto (ex.: `default`, ou um ambiente configurado pela sua organização).

**Nota:** `/remote-env` lista ambientes disponíveis — não cria novos. Ambientes são provisionados pela Anthropic ou pelo admin da sua organização.

## 4. Como funciona a sessão cloud

- Cada sessão cloud inicia uma VM limpa (Ubuntu)
- O hook `SessionStart` (`scripts/hooks/session_start.sh`) instala dependências automaticamente quando `CLAUDE_CODE_REMOTE=true`
- Dependências instaladas: `requirements.txt` (Python) + `package.json` (Node)
- A VM é descartada ao encerrar a sessão — sem estado persistente

## 5. Fluxo recomendado

```
Local (desenvolvimento)   →  git push origin dev
Cloud (execução/revisão)  →  abrir sessão cloud, /advance ou /review
Cloud (análise pesada)    →  delegar ao agente especializado
```

## 6. Limitações em sessões cloud

- `/clear` não disponível — use `/compact` para comprimir o contexto
- Arquivos locais não são acessíveis na VM cloud
- Não há sincronização automática entre local e cloud — use git como ponte
- Se o ambiente cloud não tiver as dependências certas, verifique `requirements.txt` e `package.json`

## 7. Acesso remoto ao computador local (`--remote-control`)

Para acessar seu computador local remotamente via Claude Code mobile:

```bash
claude --remote-control
```

Isso expõe o Claude Code local como servidor remoto acessível pelo app mobile.

**Diferença:** `--remote-control` = acessa seu PC local. Sessão cloud = VM da Anthropic.

---

## TIER 3 — Configuração manual por conta (feita uma vez na UI cloud)

Esses passos vivem na sua conta Anthropic, não no repositório. Configure em: **claude.ai -> Environments -> seu ambiente**.

### D3 — Instalar GitHub App

Obrigatório para acessar repositórios privados na cloud:

> https://github.com/apps/claude

Após instalar: Settings -> Configure -> All repositories

### D4 — /web-setup (pré-requisito de tudo)

Execute uma vez no terminal Claude Code local:

```
/web-setup
```

Sincroniza seu token GitHub com a conta Anthropic. Sem isso, `gh` não funciona em VMs remotas.

### I6 — /remote-env (selecionar ambiente cloud padrão)

```
/remote-env
```

Lista e seleciona o ambiente cloud padrão para este projeto.

### F1 — Agent Teams (múltiplos agentes em paralelo)

Na UI cloud, adicione a variável de ambiente:

```
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

Permite rodar múltiplos agentes Claude em paralelo no mesmo projeto.
Padrão: `0` (desabilitado). Habilite só se precisar de paralelismo real.

### F2 — Compactação antecipada de contexto

```
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=70
```

Compacta o contexto quando atingir 70% (padrão: 95%). Recomendado para projetos longos — menos perda de contexto ao compactar mais cedo.

### F3 — Janela de compactação automática

```
CLAUDE_CODE_AUTO_COMPACT_WINDOW=<valor>
```

Controla o tamanho da janela de contexto preservada após compactação. Opcional.

### F4 — GH_TOKEN no ambiente cloud

Na UI cloud, adicione:

```
GH_TOKEN=<seu_token>
```

Necessário para operações `gh` em sessões cloud sem GitHub App configurado.

### F5 — CCR_FORCE_BUNDLE (repos privados sem GitHub App)

```
CCR_FORCE_BUNDLE=1
```

Alternativa ao GitHub App para repositórios privados. Use se não quiser instalar o GitHub App.

### J — Setup script: instalar gh CLI

Na UI cloud, campo "Setup script", adicione:

```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install gh -y
```

Garante que `gh` está disponível em toda sessão cloud.

### J2 — Níveis de acesso à rede

Na UI cloud, campo "Network access":

- **Trusted** (padrão): acesso completo à internet — necessário para `gh`, `pip`, `npm`
- **Restricted**: sem acesso externo — use só para análises isoladas

Mantenha **Trusted** para uso normal com este projeto.

### J3 — Docker Compose

Se gerou `docker-compose.yml` no wizard, adicione ao setup script da cloud:

```bash
docker compose pull
```

Pré-carrega as imagens no cache da VM, acelerando o primeiro `docker compose up`.

### D1 — Rotinas agendadas

Configure via UI cloud em "Schedules" ou use `/schedule` no terminal:

```
/schedule "Run /advance" --cron "0 9 * * 1-5"
```

Executa `/advance` automaticamente toda manhã de semana.

### D2 — Rotina API-triggered

Configure um webhook externo apontando para sua sessão cloud. Útil para disparar `/advance` a partir de eventos externos (ex: novo commit, nova issue criada).

---

## TIER 4 — Workflows por sessão

Esses comandos são usados dentro de sessões cloud ativas.

### I1 — Rodar /advance remotamente

Do terminal local, dispare uma sessão cloud sem abrir o browser:

```bash
claude --remote "Run /advance"
```

### I2 — Múltiplos agentes em paralelo (requer F1)

```bash
claude --remote "Run /advance" &
claude --remote "Run /review" &
```

Executa dois agentes simultâneos. Requer `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.

### I3 — /autofix-pr

Após instalar o GitHub App, o Claude Code pode corrigir PRs automaticamente quando solicitado:

```
/autofix-pr
```

Revisa o PR aberto, identifica problemas e aplica correções.

### I4 — --teleport / /teleport

Transfere o contexto atual de uma sessão local para uma sessão cloud:

```bash
claude --teleport
```

Ou dentro de uma sessão:

```
/teleport
```

Útil para continuar trabalho pesado na cloud sem perder contexto.

### I7 — /tasks (monitorar sessões cloud)

```
/tasks
```

Lista e monitora sessões cloud em andamento a partir do terminal local.

### I8 — check-tools (debug cloud)

Dentro de uma sessão cloud, verifique quais ferramentas estão disponíveis:

```
check-tools
```

Útil para diagnosticar quando um agente não consegue executar determinada operação.

### I9 — Plan mode + execução cloud autônoma

Planeje localmente, execute na cloud sem supervisão:

```bash
claude --remote "Enter plan mode, plan /advance, then execute autonomously"
```

### I10 — Diff review com comentários inline

Na UI web (claude.ai/code), abra um PR e use o painel de diff para comentar linha a linha antes de aprovar.

### I11 — Compartilhamento de sessão

Na UI web, ative o toggle de visibilidade da sessão para compartilhar o link com colaboradores. Eles podem acompanhar em tempo real sem editar.

### I12 — ultraplan

Modo de planejamento estendido no browser. O Claude elabora um plano detalhado que você revisa e aprova antes da execução:

```
/ultraplan
```

### I13 — ultrareview

Code review multi-agente em sandbox cloud. Analisa o PR com múltiplas perspectivas antes de submeter:

```
/ultrareview
```

### I14 — --remote-control (acesso à máquina local pelo celular)

Na sua máquina local, execute:

```bash
claude --remote-control
```

Isso expõe o Claude Code local como servidor remoto. Acesse pelo app Claude mobile para continuar trabalhando de qualquer lugar com controle total do seu ambiente local.

### D5 — Sessões em segundo plano + app mobile

1. Inicie uma sessão cloud no browser
2. Feche o browser — a sessão continua rodando em background
3. Abra o app Claude mobile -> "Sessions" -> sua sessão ativa
4. Monitore o progresso, aprove decisões ou cancele de qualquer lugar
"""
    setup_dir = destination / "docs" / "setup"
    setup_dir.mkdir(parents=True, exist_ok=True)
    (setup_dir / "cloud_guide.md").write_text(content, encoding="utf-8")


def generate_cloud_setup_script(destination: Path) -> None:
    """Gera scripts/cloud_setup.sh com instalação de gh CLI para VM cloud."""
    content = """\
#!/bin/bash
# Cloud setup script — instala gh CLI e autentica na VM cloud
set -e

echo "🔧 Instalando gh CLI..."
type -p curl >/dev/null || (apt update && apt install -y curl)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
apt update && apt install -y gh

echo "🔑 Autenticando gh CLI..."
if [ -n "$GH_TOKEN" ]; then
  echo "$GH_TOKEN" | gh auth login --with-token
  echo "✅ gh CLI autenticado via GH_TOKEN."
else
  echo "⚠️  GH_TOKEN não encontrado. Execute: export GH_TOKEN=<seu-token>"
fi

echo "✅ Setup cloud concluído."
"""
    scripts_dir = destination / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    script_path = scripts_dir / "cloud_setup.sh"
    script_path.write_text(content, encoding="utf-8")
    script_path.chmod(0o755)


def update_settings_env(
    destination: Path, autocompact: bool, agent_teams: bool
) -> None:
    """Edita .claude/settings.json do filho com valores escolhidos pelo usuário."""
    settings_path = destination / ".claude" / "settings.json"
    if not settings_path.exists():
        return
    data = json.loads(settings_path.read_text(encoding="utf-8"))
    env = data.setdefault("env", {})
    if autocompact:
        env["CLAUDE_AUTOCOMPACT_PCT_OVERRIDE"] = "70"
    if agent_teams:
        env["CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"] = "1"
    settings_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def generate_docker_compose(destination: Path) -> None:
    """Gera docker-compose.yml base para desenvolvimento."""
    content = """\
version: "3.9"

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev
      POSTGRES_DB: dev
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
"""
    (destination / "docker-compose.yml").write_text(content, encoding="utf-8")


def install_deps_in_child(destination: Path) -> None:
    """Roda npm install e pip install no repositório filho."""
    import shutil

    is_windows = sys.platform == "win32"
    npm_cmd = "npm.cmd" if is_windows else "npm"
    pip_cmd = [sys.executable, "-m", "pip"] if is_windows else ["pip"]

    if shutil.which(npm_cmd) or (is_windows and shutil.which("npm")):
        result = subprocess.run(
            [npm_cmd, "install", "--silent"],
            cwd=destination,
            capture_output=True,
            check=False,
        )
        if result.returncode == 0:
            print("- npm install concluido.")
        else:
            print("- npm install: aviso (pode nao ter node_modules ainda).")
    else:
        print("- npm nao encontrado — pule npm install ou instale Node.js.")

    req_path = destination / "requirements.txt"
    if req_path.exists():
        result = subprocess.run(
            pip_cmd + ["install", "-r", "requirements.txt", "--quiet"],
            cwd=destination,
            capture_output=True,
            check=False,
        )
        if result.returncode == 0:
            print("- pip install concluido.")
        else:
            print("- pip install: aviso — verifique requirements.txt.")
    else:
        print("- requirements.txt nao encontrado — pip install pulado.")


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    env = load_env()
    ensure_gh_scopes(env)
    env = bootstrap_local_credentials(env)
    interactive = is_interactive()
    prompt_enabled = should_prompt(args, interactive)
    template_repo = parse_origin_repo(env)
    owner = template_repo.split("/", maxsplit=1)[0]
    template_branch = args.template_branch or detect_template_branch()

    print("Wizard de criacao de repositorio")
    print(f"- Template atual: {template_repo} (branch: {template_branch})")

    advanced = args.advanced

    repo_name = build_repo_name(
        args.name or prompt_text("Nome do novo repositorio", required=True)
    )
    visibility = args.visibility
    if visibility is None:
        visibility = (
            prompt_choice(
                "Visibilidade do repositorio",
                [("private", "Privado"), ("public", "Publico")],
                default_key="private",
            )
            if prompt_enabled
            else "private"
        )
    description = (
        args.description
        if args.description is not None
        else (
            prompt_text("Descricao", default="", required=False)
            if prompt_enabled
            else ""
        )
    )

    configure_secret = not args.skip_secret
    run_workflow_now = not args.skip_workflow
    validate_result = not args.skip_validate
    clone_locally = not args.skip_clone
    local_clone_path = build_local_clone_path(repo_name)

    if args.skip_secret is False and prompt_enabled:
        configure_secret = (
            prompt_choice(
                "Configurar o secret GH_PAT no repo novo?",
                [("yes", "Sim"), ("no", "Nao")],
                default_key="yes",
            )
            == "yes"
        )
    if args.skip_workflow is False and prompt_enabled:
        run_workflow_now = (
            prompt_choice(
                "Rodar a workflow Setup Kanban agora?",
                [("yes", "Sim"), ("no", "Nao")],
                default_key="yes",
            )
            == "yes"
        )
    if args.skip_validate is False and prompt_enabled:
        validate_result = (
            prompt_choice(
                "Validar resultado no final?",
                [("yes", "Sim"), ("no", "Nao")],
                default_key="yes",
            )
            == "yes"
        )
    if args.skip_clone is False and prompt_enabled:
        clone_locally = (
            prompt_choice(
                "Clonar o repositorio novo localmente?",
                [("yes", "Sim"), ("no", "Nao")],
                default_key="yes",
            )
            == "yes"
        )

    install_caveman = False
    if not args.skip_caveman:
        if args.caveman:
            install_caveman = True
        elif prompt_enabled:
            install_caveman = (
                prompt_choice(
                    "Instalar Caveman? (modo ultra-comprimido de tokens, ~75% menos tokens)",
                    [("yes", "Sim"), ("no", "Nao")],
                    default_key="yes",
                )
                == "yes"
            )

    full_name = f"{owner}/{repo_name}"
    project_title = f"{repo_name} Kanban"

    print("\nResumo")
    print(f"- Modo: {'avancado (cloud)' if advanced else 'simples'}")
    print(f"- Novo repo: {full_name}")
    print(f"- Visibilidade: {visibility}")
    print(f"- Configurar GH_PAT: {'sim' if configure_secret else 'nao'}")
    print(f"- Rodar Setup Kanban: {'sim' if run_workflow_now else 'nao'}")
    print(f"- Validar ao final: {'sim' if validate_result else 'nao'}")
    print(f"- Clonar localmente: {'sim' if clone_locally else 'nao'}")
    if clone_locally:
        print(f"- Pasta local: {local_clone_path}")
    print("- Instalar dependencias (npm/pip): sim")
    if advanced:
        print("- Gerar cloud_guide.md: sim")
        print("- Orientacoes /web-setup + GitHub App: sim")
    print(f"- Instalar Caveman: {'sim' if install_caveman else 'nao'}")

    if should_confirm_creation(args, interactive):
        if (
            prompt_choice(
                "Deseja continuar?",
                [("yes", "Sim"), ("no", "Nao")],
                default_key="yes",
            )
            != "yes"
        ):
            print("Operacao cancelada.")
            return 0

    try:
        ensure_repo_absent(env, full_name)
        if clone_locally:
            ensure_local_clone_absent(local_clone_path)

        if template_branch == "main":
            create_command = [
                "gh",
                "repo",
                "create",
                full_name,
                "--template",
                template_repo,
                f"--{visibility}",
            ]
            if not clone_locally:
                create_command.append("--clone=false")
            if description:
                create_command.extend(["--description", description])
            repo_url = run_command(create_command, env)
        else:
            create_command = [
                "gh",
                "repo",
                "create",
                full_name,
                f"--{visibility}",
                "--clone=false",
            ]
            if description:
                create_command.extend(["--description", description])
            repo_url = run_command(create_command, env)
            push_url = f"https://github.com/{full_name}.git"
            run_command(
                ["git", "push", push_url, f"{template_branch}:main"],
                env,
            )
            print(f"- Conteudo do branch '{template_branch}' publicado como main.")
        print(f"\nRepositorio criado: {repo_url}")

        if configure_secret:
            gh_token = env.get("GH_TOKEN")
            if not gh_token:
                raise RuntimeError(
                    "GH_TOKEN nao encontrado para configurar o secret GH_PAT."
                )
            maybe_set_secret(env, full_name, "GH_PAT", gh_token)
            print("- Secret GH_PAT configurado.")

        if clone_locally:
            clone_repo_locally(env, full_name, local_clone_path)
            print(f"- Repositorio clonado em: {local_clone_path}")
            cleanup_template_files(local_clone_path, repo_name)
            if install_caveman:
                install_caveman_skill(local_clone_path)
                subprocess.run(
                    ["git", "add", "-A"],
                    cwd=local_clone_path,
                    check=True,
                    capture_output=True,
                )
                status = subprocess.run(
                    ["git", "diff", "--cached", "--quiet"],
                    cwd=local_clone_path,
                    capture_output=True,
                )
                if status.returncode != 0:
                    subprocess.run(
                        ["git", "commit", "-m", "chore: install caveman skills"],
                        cwd=local_clone_path,
                        check=True,
                        capture_output=True,
                    )
                    subprocess.run(
                        ["git", "push"],
                        cwd=local_clone_path,
                        check=True,
                        capture_output=True,
                    )
                print("- Caveman skill instalado.")

            # B4: instalar dependencias no filho (ambos os modos)
            print("\nInstalando dependencias no repositorio filho...")
            install_deps_in_child(local_clone_path)

            if advanced:
                generated = []

                # B6: gerar cloud_guide.md
                generate_cloud_guide(local_clone_path, repo_name)
                generated.append("docs/setup/cloud_guide.md")
                print("- cloud_guide.md gerado em docs/setup/.")

                # cloud_setup.sh
                if args.cloud_setup:
                    generate_cloud_setup_script(local_clone_path)
                    generated.append("scripts/cloud_setup.sh")
                    print("- cloud_setup.sh gerado em scripts/.")

                # settings.json: editar valores se pediu
                if args.autocompact or args.agent_teams:
                    update_settings_env(
                        local_clone_path, args.autocompact, args.agent_teams
                    )
                    generated.append(".claude/settings.json")
                    vars_set = []
                    if args.autocompact:
                        vars_set.append("AUTOCOMPACT_PCT_OVERRIDE=70")
                    if args.agent_teams:
                        vars_set.append("AGENT_TEAMS=1")
                    print(f"- settings.json atualizado: {', '.join(vars_set)}")

                # docker-compose.yml
                if args.docker:
                    generate_docker_compose(local_clone_path)
                    generated.append("docker-compose.yml")
                    print("- docker-compose.yml gerado.")

                # commit tudo junto
                for f in generated:
                    subprocess.run(
                        ["git", "add", f],
                        cwd=local_clone_path,
                        check=False,
                        capture_output=True,
                    )
                subprocess.run(
                    [
                        "git",
                        "commit",
                        "-m",
                        "chore: add cloud setup files (advanced mode)",
                    ],
                    cwd=local_clone_path,
                    check=False,
                    capture_output=True,
                )
                subprocess.run(
                    ["git", "push"],
                    cwd=local_clone_path,
                    check=False,
                    capture_output=True,
                )

                # Orientacoes cloud
                print("\n" + "=" * 60)
                print("PROXIMOS PASSOS — CONFIGURACAO CLOUD")
                print("=" * 60)
                print(
                    "\n[Passo 1] Instale o GitHub App (acesso a repos privados na cloud):"
                )
                print("  https://github.com/apps/claude")
                print("  Apos instalar: Settings -> Configure -> All repositories")
                print(
                    "\n[Passo 2] Instale o Claude Code CLI (desbloqueia sessoes cloud, /web-setup, --remote):"
                )
                print("  PowerShell: irm https://claude.ai/install.ps1 | iex")
                print("  WinGet:     winget install Anthropic.ClaudeCode")
                print("  Requer:     Git for Windows instalado")
                print(
                    "  Apos instalar: adicione ao PATH: C:\\Users\\<usuario>\\.local\\bin"
                )
                print(
                    "  (Painel de Controle -> Sistema -> Variaveis de Ambiente -> PATH)"
                )
                print(
                    "\n[Passo 2b] Autentique o gh CLI (em PowerShell externo, fora do Claude Code):"
                )
                print("  gh auth login")
                print("  (O Claude Code bloqueia gh auth login — use terminal externo)")
                print(
                    "\n[Passo 3] Com CLI e gh autenticados — execute no terminal Claude Code:"
                )
                print("  /web-setup   -> sincroniza token GitHub com a conta Anthropic")
                print("  /remote-env  -> seleciona ambiente cloud padrao")
                print("\nDetalhes completos: docs/setup/cloud_guide.md")
                print("=" * 60)
            else:
                if args.cloud_setup:
                    generate_cloud_setup_script(local_clone_path)
                    print("- scripts/cloud_setup.sh gerado.")
                if args.autocompact or args.agent_teams:
                    update_settings_env(local_clone_path, args.autocompact, args.agent_teams)
                    print("- settings.json atualizado com variaveis de ambiente.")
                if args.docker:
                    generate_docker_compose(local_clone_path)
                    print("- docker-compose.yml gerado.")

        if run_workflow_now:
            workflow_output = maybe_run_workflow(env, full_name, "Setup Kanban")
            print(f"- Workflow disparada: {workflow_output}")
        else:
            print("- Workflow Setup Kanban nao foi executada.")

        if validate_result:
            summarize_validation(env, full_name, project_title)
        else:
            if run_workflow_now:
                project_url = wait_for_project_url(env, project_title)
                if project_url:
                    print(f"- GitHub Project criado: {project_url}")
                else:
                    print("- GitHub Project ainda nao disponivel — acesse a aba Projects do repositorio em instantes.")
            print("- Validacao final pulada.")
    except Exception as exc:  # noqa: BLE001
        print(f"\nErro: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
