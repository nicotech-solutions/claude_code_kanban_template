#!/usr/bin/env bash
# Verifica se o ambiente local está pronto para desenvolvimento

set -euo pipefail

OK="✓"
FAIL="✗"
WARN="⚠"
errors=0

check() {
    local name="$1"
    local cmd="$2"
    local expected="${3:-}"

    if output=$(eval "$cmd" 2>/dev/null); then
        if [[ -n "$expected" ]] && ! echo "$output" | grep -q "$expected"; then
            echo "$WARN  $name — versão inesperada: $output (esperado: $expected)"
        else
            echo "$OK  $name — $output"
        fi
    else
        echo "$FAIL  $name — não encontrado"
        ((errors++))
    fi
}

check_file() {
    local name="$1"
    local path="$2"
    local hint="$3"
    if [[ -f "$path" ]]; then
        echo "$OK  $name — $path"
    else
        echo "$WARN  $name — $path não existe ($hint)"
    fi
}

echo "=== Verificação do ambiente ==="
echo ""

echo "-- Ferramentas principais --"
check "Python"  "python3 --version"  "3.1"
check "uv"      "uv --version"
check "git"     "git --version"
check "gh CLI"  "gh --version"

echo ""
echo "-- Ferramentas de qualidade --"
check "pytest"  "python3 -m pytest --version"
check "ruff"    "ruff --version"
check "black"   "black --version"

echo ""
echo "-- Arquivos locais (não commitados) --"
check_file ".mcp.json"        ".mcp.json"        "copie de .mcp.json.example e preencha o token"
check_file "CLAUDE.local.md"  "CLAUDE.local.md"  "copie de CLAUDE.local.md.example e personalize"

echo ""
echo "-- Autenticação GitHub --"
if gh auth status &>/dev/null; then
    echo "$OK  gh auth — $(gh api user --jq '.login' 2>/dev/null || echo 'autenticado')"
else
    echo "$WARN  gh auth — não autenticado (rode: gh auth login)"
fi

echo ""
if [[ $errors -eq 0 ]]; then
    echo "Ambiente OK. Rode 'uv sync' para instalar dependências e 'claude' para abrir o Claude Code."
else
    echo "$FAIL  $errors ferramenta(s) ausente(s). Instale antes de continuar."
    exit 1
fi
