#!/usr/bin/env python3
"""Valida a integridade Markdown dos arquivos da pasta Segundo Cerebro (Deck).

Checagens feitas em cada arquivo .md da pasta:
  - Exatamente um H1 (#), e ele deve ser a primeira linha nao vazia do arquivo.
  - Hierarquia de headers sem pular nivel (ex.: H1 -> H3 sem H2 no meio).
  - Headers duplicados (mesmo texto) dentro do mesmo arquivo.
  - Code fences (```) sem linguagem declarada quando parecem conter codigo/comando.
  - Code fences nao fechados (numero impar de ``` no arquivo).

Checagem extra no README.md (indice):
  - Todo link markdown [texto](arquivo.md) deve apontar para um arquivo existente
    na mesma pasta.
  - Todo outro arquivo .md da pasta (exceto o proprio README) deveria estar linkado
    no indice (aviso, nao erro).

Uso:
    python validar_deck.py "<caminho-da-pasta-deck>"

Saida: lista de problemas por arquivo. Exit code 0 se nada encontrado, 1 caso
contrario.
"""

import re
import sys
from pathlib import Path

HEADER_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
FENCE_RE = re.compile(r"^\s*```(\S*)\s*$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def check_headers(lines, problems):
    headers = []  # (level, text, line_no)
    in_fence = False
    for i, line in enumerate(lines, start=1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADER_RE.match(line)
        if m:
            headers.append((len(m.group(1)), m.group(2), i))

    if not headers:
        problems.append("nenhum header encontrado (arquivo sem titulo H1)")
        return

    h1s = [h for h in headers if h[0] == 1]
    if len(h1s) == 0:
        problems.append("falta um titulo H1 (#) no topo do arquivo")
    elif len(h1s) > 1:
        linhas = ", ".join(str(h[2]) for h in h1s)
        problems.append(f"mais de um H1 no arquivo (linhas {linhas}) — deve haver so um")

    first_nonblank = next((ln for ln in lines if ln.strip()), "")
    if h1s and not HEADER_RE.match(first_nonblank):
        problems.append("o H1 deve ser a primeira linha nao vazia do arquivo")

    prev_level = None
    for level, text, line_no in headers:
        if prev_level is not None and level > prev_level + 1:
            problems.append(
                f"linha {line_no}: pulo de nivel de header (H{prev_level} -> H{level}) "
                f'em "{text}"'
            )
        prev_level = level

    seen = {}
    for level, text, line_no in headers:
        key = (level, text.strip().lower())
        if key in seen:
            problems.append(
                f'linha {line_no}: header duplicado "{text}" (ja aparece na linha {seen[key]})'
            )
        else:
            seen[key] = line_no


def check_fences(lines, problems):
    fence_lines = [(i, FENCE_RE.match(line)) for i, line in enumerate(lines, start=1)]
    fence_lines = [(i, m) for i, m in fence_lines if m]

    if len(fence_lines) % 2 != 0:
        problems.append(
            f"numero impar de marcadores de code fence (```) — bloco nao fechado "
            f"(ultimo em linha {fence_lines[-1][0]})"
        )
        fence_lines = fence_lines[:-1]

    for idx in range(0, len(fence_lines), 2):
        line_no, m = fence_lines[idx]
        lang = m.group(1)
        if not lang:
            close_line_no = fence_lines[idx + 1][0]
            block = lines[line_no:close_line_no - 1]
            content = "\n".join(block).strip()
            looks_like_code = bool(content) and not content.startswith(("- ", "* ", "#"))
            if looks_like_code:
                problems.append(
                    f"linha {line_no}: code fence sem linguagem declarada "
                    f'(usar ```powershell, ```bash, ```python, etc.)'
                )


def check_readme_links(deck_dir, readme_path, problems_by_file):
    text = readme_path.read_text(encoding="utf-8")
    linked_targets = set()
    problems = []

    for m in LINK_RE.finditer(text):
        target = m.group(1)
        if target.startswith(("http://", "https://", "#")):
            continue
        linked_targets.add(target)
        target_path = deck_dir / target
        if not target_path.exists():
            problems.append(f'link quebrado no indice: "{target}" nao existe na pasta Deck')

    all_md = {p.name for p in deck_dir.glob("*.md") if p.name.lower() != "readme.md"}
    missing_from_index = sorted(all_md - linked_targets)
    for name in missing_from_index:
        problems.append(f'aviso: "{name}" existe na pasta mas nao esta linkado no indice')

    if problems:
        problems_by_file["README.md"] = problems


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)

    deck_dir = Path(sys.argv[1])
    if not deck_dir.is_dir():
        print(f"Pasta nao encontrada: {deck_dir}")
        sys.exit(2)

    md_files = sorted(deck_dir.glob("*.md"))
    if not md_files:
        print(f"Nenhum arquivo .md encontrado em {deck_dir}")
        sys.exit(0)

    problems_by_file = {}

    for path in md_files:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        problems = []
        check_headers(lines, problems)
        check_fences(lines, problems)
        if problems:
            problems_by_file[path.name] = problems

    readme_path = deck_dir / "README.md"
    if readme_path.exists():
        check_readme_links(deck_dir, readme_path, problems_by_file)

    if not problems_by_file:
        print(f"OK — nenhum problema encontrado em {len(md_files)} arquivo(s).")
        sys.exit(0)

    for filename, problems in problems_by_file.items():
        print(f"\n{filename}:")
        for p in problems:
            print(f"  - {p}")

    sys.exit(1)


if __name__ == "__main__":
    main()
