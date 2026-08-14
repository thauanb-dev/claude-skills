# Guia de formatação — Segundo Cérebro

Estilo usado em todos os arquivos da pasta Deck. Seguir isto ao criar ou editar
qualquer arquivo de tema.

## Estrutura de um arquivo de tema

```markdown
# Nome do Tema

## Nome da seção (o "o quê")

Explicação curta de 1-2 linhas, se necessário.

### Variação ou caso específico (opcional)

Explicação curta.

```linguagem
comando ou código de exemplo
```
```

Regras:

- **H1 (`#`)**: um único, no topo do arquivo, é o nome do tema (ex.: `# Git`,
  `# PowerShell`). Nunca repetir H1 dentro do arquivo.
- **H2 (`##`)**: um subtema ou grupo de comandos (ex.: `## Criar alias de comandos`).
- **H3 (`###`)**: uma variação específica dentro do H2 (ex.: `### Alias simples (sem
  parâmetros)`). Não pular de H1 direto para H3.
- **Code fences**: sempre com a linguagem declarada logo após os três acentos graves —
  `powershell`, `bash`, `shell`, `python`, `text`, etc. Nunca usar ` ``` ` sozinho quando
  o bloco tem código/comando.
- **Prosa**: frases curtas, direto ao ponto, em português do Brasil. Não escrever
  parágrafos longos — isso é um cheat sheet, não um tutorial.
- **Exemplos**: preferir mostrar um comando pronto para copiar/colar a explicar em texto.

## Exemplo real (PowerShell.md)

```markdown
# PowerShell

## Criar alias de comandos

### Alias simples (sem parâmetros)

Só funciona para substituir um nome por outro comando existente, sem argumentos fixos:

​```powershell
Set-Alias ll Get-ChildItem
​```

### Alias com parâmetros fixos (função)

`Set-Alias` não aceita argumentos extras. Quando o comando tem flags fixas, use uma função:

​```powershell
function gcm { git commit --amend --no-edit }
​```
```

(o caractere invisível antes de cada ` ``` ` acima existe só para não fechar este bloco
de exemplo — não copiar esse detalhe.)

## Índice (README.md)

O `README.md` da pasta Deck é só um índice. Manter a seção `## Arquivos` com uma linha
por arquivo de tema, nesse formato:

```markdown
- [NomeDoTema.md](NomeDoTema.md) — descrição curta de uma linha
```

- O texto do link deve ser exatamente o nome do arquivo.
- O destino do link é sempre relativo (nunca caminho absoluto).
- Toda entrada precisa apontar para um arquivo que realmente existe na pasta — ao
  remover ou renomear um arquivo de tema, atualizar o índice no mesmo momento.
- Novo arquivo de tema → nova linha no índice, na mesma hora em que o arquivo é criado.

## Duplicação

Antes de adicionar um comando ou conceito, procurar (`grep`/leitura) se ele já existe em
algum arquivo do Deck. Se existir:

- Mesma informação, mesmo comando → não duplicar; se o novo conteúdo é mais completo,
  atualizar o trecho existente no lugar.
- Informação relacionada mas distinta → nova seção `##`/`###` no mesmo arquivo de tema.
