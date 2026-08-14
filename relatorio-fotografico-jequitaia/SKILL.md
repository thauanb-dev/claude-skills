---
name: relatorio-fotografico-jequitaia
description: Gera o "Relatório de Acompanhamento ao Recebimento de Bens Móveis" (relatório fotográfico diário da Comissão para Desocupação do Jequitaia, SIMOV NI 579) em .docx, com timbre oficial (SAEB/SUPAT/DBI), preenchendo data, narrativa e fotos com legendas numeradas automaticamente. Use quando o usuário pedir para montar/gerar o relatório fotográfico do dia, da vistoria, do Jequitaia, ou mencionar "SIMOV NI 579".
---

# Relatório Fotográfico – Comissão Jequitaia (SIMOV NI 579)

Gera o relatório .docx diário de acompanhamento do recebimento de bens móveis
oriundos da desocupação do Espaço Jequitaia (Comissão instituída pela Portaria
SAEB/SVPONTE/SEINFRA), reproduzindo fielmente o timbre, o texto fixo e o
rodapé usados nos relatórios já produzidos (pasta
`Comissão para Desocupação do Jequitaia\Julho` e `\Agosto`).

Não usa nenhuma dependência externa — só a biblioteca padrão do Python 3
(`zipfile`, `json`, `struct`, `re`). Funciona mesmo numa máquina sem `pip`.

## Como funciona

Um `.docx`-modelo (`assets/template.docx`) já contém o timbre, o parágrafo de
abertura fixo (sobre o desforço incontinenti de 24/07/2026), o rodapé com
endereço e numeração de página, e a imagem final fixa (assinatura/carimbo).
Esse modelo tem três marcadores de texto (sentinelas) que o script
`scripts/generate_report.py` substitui:

- `__DATA_VISITA__` → a data da visita (parágrafo "No dia DD/MM/AAAA, foi
  realizado acompanhamento técnico...")
- parágrafo `__NARRATIVA__` → um ou mais parágrafos de texto livre (o relato
  da visita do dia)
- parágrafo `__FOTOS__` → as seções de fotos (título da seção + fotos com
  legenda "Foto NN – descrição", numeradas sequencialmente a partir de 1)

## Workflow

1. **Reunir as fotos do dia.** Elas normalmente já estão na pasta datada,
   ex.: `Comissão para Desocupação do Jequitaia\Agosto\DD-MM-AAAA\photo_*.jpg`.
   Pergunte ao usuário como as fotos devem ser agrupadas em seções (ex.:
   "Área Externa", "Galpão") e a legenda de cada uma — ou proponha um
   agrupamento razoável a partir dos nomes/ordem dos arquivos e confirme.

2. **Reunir a narrativa do dia.** Peça ao usuário (ou, se ele já descreveu a
   visita na conversa, use isso) um relato em texto corrido do que ocorreu:
   apoio logístico, alterações em relação ao relatório anterior, ocorrências
   (retirada de embarcação por terceiro, etc). Isso vira os parágrafos de
   `narrative`. **Não invente fatos da vistoria** — só formate o que o
   usuário informou.

3. **Montar o `config.json`** (ver `scripts/README.md` para o schema
   completo) e rodar:
   ```
   python scripts/generate_report.py config.json
   ```

4. **Salvar no lugar certo.** Pelo padrão observado nos relatórios
   anteriores, o arquivo de saída deve ir para dentro da própria pasta datada
   e se chamar
   `Relatório Fotográfico - SIMOV NI 579 _ DD-MM-AA.docx`
   (dois dígitos de ano), ex.:
   `Comissão para Desocupação do Jequitaia\Agosto\07-08-2026\Relatório Fotográfico - SIMOV NI 579 _ 07-08-26.docx`.
   Use esse caminho como `output_path` no config.

5. **Conferir o resultado.** Depois de gerar, é recomendável abrir o .docx
   (ou ao menos relatar ao usuário quantas fotos/seções entraram) antes de
   considerar a tarefa concluída — o script não tem como validar visualmente
   o layout.

## Reuso para outros casos/imóveis

O parágrafo de abertura fixo (desforço incontinenti / Espaço Jequitaia /
CPSI) está embutido no `template.docx` porque é comum a todos os relatórios
dessa Comissão específica. Se um dia for necessário gerar um relatório
fotográfico parecido para **outro processo/imóvel**, não edite este template
— copie a pasta da skill, gere um novo `template.docx` a partir de um
`.docx` de referência do novo caso (mesmo processo de 3 sentinelas descrito
acima) e ajuste este SKILL.md.
