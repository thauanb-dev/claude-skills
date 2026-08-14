## `generate_report.py`

```
python generate_report.py config.json
```

Sem dependências externas (só a biblioteca padrão do Python 3).

### Schema do `config.json`

```jsonc
{
  // obrigatorio: data da visita, formato DD/MM/AAAA
  "visit_date": "07/08/2026",

  // obrigatorio: caminho completo do .docx de saida
  "output_path": "C:\\...\\Comissão para Desocupação do Jequitaia\\Agosto\\07-08-2026\\Relatório Fotográfico - SIMOV NI 579 _ 07-08-26.docx",

  // narrativa do dia: lista de paragrafos (texto livre, sem HTML/XML).
  // tambem aceita uma unica string com paragrafos separados por linha em branco.
  "narrative": [
    "Primeiro paragrafo do relato da visita.",
    "Segundo paragrafo, se houver."
  ],

  // secoes de fotos, na ordem em que devem aparecer no documento.
  // a numeracao "Foto NN" e sequencial e automatica ao longo de todas as secoes.
  "sections": [
    {
      "title": "Área Externa",
      "photos": [
        {"path": "C:\\...\\photo_1.jpg", "caption": "Área Externa"},
        {"path": "C:\\...\\photo_2.jpg", "caption": "Área Externa – embarcação sem lona"}
      ]
    },
    {
      "title": "Galpão",
      "photos": [
        {"path": "C:\\...\\photo_3.jpg", "caption": "Galpão – bens do Estaleiro 05"}
      ]
    }
  ],

  // opcional: numero da primeira foto (padrao 1)
  "start_photo_number": 1,

  // opcional: usar um template.docx diferente do padrao (assets/template.docx)
  "template_path": null
}
```

### O que o script faz

1. Copia `assets/template.docx` (ou `template_path`) inteiro.
2. Troca a sentinela `__DATA_VISITA__` pela data informada.
3. Troca o parágrafo-sentinela da narrativa pelos parágrafos de `narrative`.
4. Troca o parágrafo-sentinela das fotos pelas seções/fotos de `sections`:
   para cada foto, copia o arquivo para `word/media/`, cria a relação de
   imagem (`word/_rels/document.xml.rels`), garante que a extensão está
   registrada em `[Content_Types].xml`, calcula a proporção da imagem (lendo
   o cabeçalho JPEG/PNG) para não distorcer, e insere a legenda
   "Foto NN – legenda".
5. Grava o `.docx` final em `output_path` (cria as pastas que faltarem).

Tudo o que já está fixo no template (timbre, brasão, parágrafo de abertura,
rodapé com endereço/paginação, imagem final de assinatura) permanece
inalterado — o script só mexe nas três sentinelas.

### Erros comuns

- `FileNotFoundError: Foto nao encontrada` — confira o caminho da foto.
- `ValueError: Sentinela ... nao encontrada` — o `template_path` apontado não
  é o template desta skill (não tem as sentinelas), ou já foi processado
  antes.
