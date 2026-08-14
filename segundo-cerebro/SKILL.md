---
name: segundo-cerebro
description: This skill should be used when the user asks to save, add, or store technical knowledge, terminal commands, or concepts into their personal knowledge base ("segundo cérebro"), a folder of topic Markdown files at Z:\SUPAT\Diretoria da Administração dos Bens Imóveis\COPENG\THAUAN\Deck. Triggers on phrases like "adiciona isso no segundo cérebro", "guarda isso", "salva isso no Deck", "anota isso pra eu não esquecer", or whenever a useful command/concept surfaces in conversation and the user wants it persisted for later reference. Also use it to check or fix the integrity (Markdown errors, broken index links, formatting drift) of the Deck files.
---

# Segundo Cérebro

## Propósito

Manter uma base de conhecimento técnico pessoal em Markdown, organizada por tema (um
arquivo `.md` por assunto), com um `README.md` como índice central. Cada arquivo é um
"cheat sheet" curto e prático — comandos, exemplos, conceitos — não um documento longo.

## Diretório base

```
Z:\SUPAT\Diretoria da Administração dos Bens Imóveis\COPENG\THAUAN\Deck
```

Tratar este caminho como fixo. Não perguntar ao usuário onde salvar, a menos que o
próprio usuário peça para mudar de pasta.

## Workflow

1. **Ler antes de escrever.** Abrir `README.md` (índice) e o arquivo de tema candidato
   (se existir) antes de editar. Isso evita duplicar conteúdo já registrado e mantém o
   estilo consistente com o que já está lá.

2. **Decidir o destino do conteúdo:**
   - Se já existe um arquivo para o tema (ex.: `Git.md`, `PowerShell.md`,
     `Claude-Code.md`), adicionar o conteúdo lá como uma nova seção `##`/`###`.
     - Se o comando/conceito já está documentado, **atualizar** a seção existente em vez
       de duplicá-la.
   - Se não existe arquivo para o tema, criar `NomeDoTema.md` seguindo o guia de estilo
     (`references/formatacao.md`) e adicionar uma linha em `README.md`, na seção
     `## Arquivos`, no formato:
     `- [NomeDoTema.md](NomeDoTema.md) — descrição curta de uma linha`

3. **Escrever em português do Brasil**, seguindo `references/formatacao.md` (hierarquia
   de headers, code fences com linguagem, tom direto e prático).

4. **Editar de forma cirúrgica.** Usar edição incremental (inserir/alterar a seção
   relevante) em vez de reescrever o arquivo inteiro, preservando o conteúdo já existente.

5. **Validar antes de finalizar.** Rodar o script de validação sobre a pasta Deck e
   corrigir qualquer problema reportado:

   ```bash
   python scripts/validar_deck.py "Z:\SUPAT\Diretoria da Administração dos Bens Imóveis\COPENG\THAUAN\Deck"
   ```

   O script verifica, em todos os `.md` da pasta: hierarquia de headers (H1 único no
   topo, sem pular nível), code fences sem linguagem declarada, headers duplicados dentro
   do mesmo arquivo, e links do `README.md` que apontam para arquivos inexistentes.

6. **Confirmar em uma frase** o que foi salvo e em qual arquivo — não é preciso mostrar o
   arquivo inteiro de volta ao usuário.

## Guia de estilo (resumo)

Detalhes completos e exemplos em `references/formatacao.md`. Regras essenciais:

- Um único `#` (H1) por arquivo, no topo, com o nome do tema.
- Seções em `##`, subseções em `###` — nunca pular de `#` para `###`.
- Blocos de código sempre com a linguagem declarada (` ```powershell `, ` ```bash `,
  ` ```shell `, ` ```python `, etc.).
- Sem texto duplicado entre seções do mesmo arquivo ou entre arquivos.
- Links no `README.md` sempre relativos ao próprio arquivo (`[Nome.md](Nome.md)`).
- Revisar ortografia e acentuação antes de salvar.

## Recursos

- `references/formatacao.md` — guia de estilo completo, com exemplos reais tirados dos
  arquivos já existentes no Deck.
- `scripts/validar_deck.py` — validador de integridade Markdown da pasta Deck (sem
  dependências externas, só biblioteca padrão do Python).
