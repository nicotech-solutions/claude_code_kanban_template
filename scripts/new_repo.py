from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable


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
        raise RuntimeError("Nao foi possivel identificar o repositorio de origem do template.")
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
]

TEMPLATE_ONLY_DIRS = [
    "scripts/templates",
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
            content = tpl_path.read_text(encoding="utf-8").replace("{repo_name}", repo_name)
            (destination / tpl_name).write_text(content, encoding="utf-8")

    # Copia README.md para o filho
    readme_tpl = templates_dir / "README.md"
    if readme_tpl.exists():
        (destination / "README.md").write_text(readme_tpl.read_text(encoding="utf-8"), encoding="utf-8")

    # Copia todos os commands de scripts/templates/commands/ para .claude/commands/ do filho
    commands_dir = templates_dir / "commands"
    if commands_dir.exists():
        dest_commands = destination / ".claude" / "commands"
        dest_commands.mkdir(parents=True, exist_ok=True)
        for cmd_file in commands_dir.glob("*.md"):
            (dest_commands / cmd_file.name).write_text(cmd_file.read_text(encoding="utf-8"), encoding="utf-8")

    subprocess.run(["git", "add", "-A"], cwd=destination, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "chore: initialize project files from template"],
        cwd=destination, check=True, capture_output=True,
    )
    subprocess.run(["git", "push"], cwd=destination, check=True, capture_output=True)

    # Cria branch dev a partir de main
    subprocess.run(["git", "checkout", "-b", "dev"], cwd=destination, check=True, capture_output=True)
    subprocess.run(["git", "push", "-u", "origin", "dev"], cwd=destination, check=True, capture_output=True)
    subprocess.run(["git", "checkout", "main"], cwd=destination, check=True, capture_output=True)

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
            str(workflow.get("name") or workflow.get("path") or workflow.get("id") or "")
            for workflow in workflows
        ]
        for workflow in workflows:
            name = str(workflow.get("name", ""))
            path = str(workflow.get("path", ""))
            if name == workflow_name or path == expected_path or path.endswith(
                f"/{expected_path}"
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
    max_wait_seconds: int = 180,
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


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    env = load_env()
    interactive = is_interactive()
    prompt_enabled = should_prompt(args, interactive)
    template_repo = parse_origin_repo(env)
    owner = template_repo.split("/", maxsplit=1)[0]
    template_branch = args.template_branch or detect_template_branch()

    print("Wizard de criacao de repositorio")
    print(f"- Template atual: {template_repo} (branch: {template_branch})")

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

    if args.skip_secret is False and args.name is None and prompt_enabled:
        configure_secret = (
            prompt_choice(
                "Configurar o secret GH_PAT no repo novo?",
                [("yes", "Sim"), ("no", "Nao")],
                default_key="yes",
            )
            == "yes"
        )
    if args.skip_workflow is False and args.name is None and prompt_enabled:
        run_workflow_now = (
            prompt_choice(
                "Rodar a workflow Setup Kanban agora?",
                [("yes", "Sim"), ("no", "Nao")],
                default_key="yes",
            )
            == "yes"
        )
    if args.skip_validate is False and args.name is None and prompt_enabled:
        validate_result = (
            prompt_choice(
                "Validar resultado no final?",
                [("yes", "Sim"), ("no", "Nao")],
                default_key="yes",
            )
            == "yes"
        )
    if args.skip_clone is False and args.name is None and prompt_enabled:
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
    print(f"- Novo repo: {full_name}")
    print(f"- Visibilidade: {visibility}")
    print(f"- Configurar GH_PAT: {'sim' if configure_secret else 'nao'}")
    print(f"- Rodar Setup Kanban: {'sim' if run_workflow_now else 'nao'}")
    print(f"- Validar ao final: {'sim' if validate_result else 'nao'}")
    print(f"- Clonar localmente: {'sim' if clone_locally else 'nao'}")
    if clone_locally:
        print(f"- Pasta local: {local_clone_path}")
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

        if clone_locally:
            clone_repo_locally(env, full_name, local_clone_path)
            print(f"- Repositorio clonado em: {local_clone_path}")
            cleanup_template_files(local_clone_path, repo_name)
            if install_caveman:
                install_caveman_skill(local_clone_path)
                print("- Caveman skill instalado.")

        if configure_secret:
            gh_token = env.get("GH_TOKEN")
            if not gh_token:
                raise RuntimeError("GH_TOKEN nao encontrado para configurar o secret GH_PAT.")
            maybe_set_secret(env, full_name, "GH_PAT", gh_token)
            print("- Secret GH_PAT configurado.")

        if run_workflow_now:
            workflow_output = maybe_run_workflow(env, full_name, "Setup Kanban")
            print(f"- Workflow disparada: {workflow_output}")
        else:
            print("- Workflow Setup Kanban nao foi executada.")

        if validate_result:
            summarize_validation(env, full_name, project_title)
        else:
            print("- Validacao final pulada.")
    except Exception as exc:  # noqa: BLE001
        print(f"\nErro: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
