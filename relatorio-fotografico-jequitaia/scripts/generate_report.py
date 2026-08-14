#!/usr/bin/env python3
"""Gera um "Relatorio Fotografico" (docx) da Comissao para Desocupacao do
Jequitaia a partir de um template com o timbre/rodape fixos (assets/template.docx).

Uso:
    python generate_report.py config.json

O config.json descreve a data da visita, o texto narrativo e as secoes de
fotos. Ver README.md nesta pasta para o formato completo e um exemplo.

Sem dependencias externas (so biblioteca padrao do Python).
"""
import json
import os
import re
import struct
import sys
import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE = os.path.join(SCRIPT_DIR, "..", "assets", "template.docx")

SENT_NARR = (
    '<w:p><w:pPr><w:jc w:val="both"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" '
    'w:cs="Arial"/><w:sz w:val="24"/></w:rPr></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Arial" '
    'w:hAnsi="Arial" w:cs="Arial"/><w:sz w:val="24"/></w:rPr>'
    '<w:t>__NARRATIVA__</w:t></w:r></w:p>'
)
SENT_FOTOS = '<w:p><w:r><w:t>__FOTOS__</w:t></w:r></w:p>'
SENT_DATA = '__DATA_VISITA__'

TARGET_W_LANDSCAPE = 3600000   # EMU (~3.75in)
TARGET_H_PORTRAIT = 4200000    # EMU (~4.38in)
MAX_W = 5500000                # EMU, largura util maxima da pagina


def xml_escape(text):
    return (
        text.replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
    )


def image_size(path):
    """Retorna (largura, altura) em pixels lendo o cabecalho do arquivo.
    Suporta JPEG e PNG. Se falhar, retorna None."""
    try:
        with open(path, 'rb') as f:
            head = f.read(32)
            if head[:8] == b'\x89PNG\r\n\x1a\n':
                w, h = struct.unpack('>II', head[16:24])
                return w, h
            if head[:2] == b'\xff\xd8':
                f.seek(2)
                while True:
                    marker = f.read(2)
                    if len(marker) < 2 or marker[0] != 0xFF:
                        break
                    if marker[1] in (0xC0, 0xC1, 0xC2, 0xC3):
                        f.read(3)
                        h, w = struct.unpack('>HH', f.read(4))
                        return w, h
                    seg_len = struct.unpack('>H', f.read(2))[0]
                    f.seek(seg_len - 2, 1)
    except Exception:
        pass
    return None


def extent_for(path):
    size = image_size(path)
    if not size or size[0] <= 0 or size[1] <= 0:
        return TARGET_W_LANDSCAPE, int(TARGET_W_LANDSCAPE * 0.62)
    w, h = size
    aspect = w / h
    if aspect >= 1:
        cx = TARGET_W_LANDSCAPE
        cy = int(cx / aspect)
    else:
        cy = TARGET_H_PORTRAIT
        cx = int(cy * aspect)
        if cx > MAX_W:
            cx = MAX_W
            cy = int(cx / aspect)
    return cx, cy


def build_photo_paragraphs(path, rid, doc_pr_id, cx, cy, ext_name):
    drawing_p = (
        '<w:p><w:pPr><w:keepNext/><w:jc w:val="both"/></w:pPr><w:r>'
        '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:noProof/>'
        '<w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="pt-BR" w:eastAsia="pt-BR"/></w:rPr>'
        '<w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
        '<wp:extent cx="%d" cy="%d"/>'
        '<wp:effectExtent l="57150" t="38100" r="33061" b="13527"/>'
        '<wp:docPr id="%d" name="%s"/>'
        '<wp:cNvGraphicFramePr><a:graphicFrameLocks '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>'
        '</wp:cNvGraphicFramePr><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:nvPicPr><pic:cNvPr id="0" name="%s"/><pic:cNvPicPr/></pic:nvPicPr>'
        '<pic:blipFill><a:blip r:embed="%s" cstate="print"/><a:stretch><a:fillRect/></a:stretch>'
        '</pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        '<a:ln w="28575"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill></a:ln>'
        '</pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'
    ) % (cx, cy, doc_pr_id, xml_escape(ext_name), xml_escape(ext_name), rid, cx, cy)
    return drawing_p


def build_caption_paragraph(number, caption):
    text = 'Foto %02d – %s' % (number, caption) if caption else 'Foto %02d' % number
    return (
        '<w:p><w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>'
        '<w:szCs w:val="24"/></w:rPr></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Arial" '
        'w:hAnsi="Arial" w:cs="Arial"/><w:szCs w:val="24"/></w:rPr><w:t xml:space="preserve">%s</w:t>'
        '</w:r></w:p>'
    ) % xml_escape(text)


def build_heading_paragraph(title):
    return (
        '<w:p><w:pPr><w:jc w:val="both"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" '
        'w:cs="Arial"/><w:b/><w:sz w:val="28"/><w:szCs w:val="24"/></w:rPr></w:pPr>'
        '<w:r><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:b/>'
        '<w:sz w:val="24"/></w:rPr><w:t xml:space="preserve">%s</w:t></w:r></w:p>'
    ) % xml_escape(title)


def build_narrative_paragraphs(paragraphs):
    out = []
    for p in paragraphs:
        out.append((
            '<w:p><w:pPr><w:jc w:val="both"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" '
            'w:cs="Arial"/><w:sz w:val="24"/></w:rPr></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Arial" '
            'w:hAnsi="Arial" w:cs="Arial"/><w:sz w:val="24"/></w:rPr><w:t xml:space="preserve">%s</w:t>'
            '</w:r></w:p>'
        ) % xml_escape(p))
    if not out:
        out.append('<w:p/>')
    return ''.join(out)


def next_rid(rels_xml):
    ids = [int(m) for m in re.findall(r'Id="rId(\d+)"', rels_xml)]
    return (max(ids) if ids else 0) + 1


def content_type_extension(ext, content_types_xml):
    ext = ext.lower().lstrip('.')
    if re.search(r'Extension="%s"' % re.escape(ext), content_types_xml):
        return content_types_xml
    mime = {
        'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
        'gif': 'image/gif', 'bmp': 'image/bmp',
    }.get(ext, 'application/octet-stream')
    insert = '<Default Extension="%s" ContentType="%s"/>' % (ext, mime)
    return content_types_xml.replace('</Types>', insert + '</Types>')


def generate(config, template_path, out_path):
    with zipfile.ZipFile(template_path) as zin:
        names = zin.namelist()
        data = {n: zin.read(n) for n in names}

    document_xml = data['word/document.xml'].decode('utf-8')
    rels_xml = data['word/_rels/document.xml.rels'].decode('utf-8')
    content_types_xml = data['[Content_Types].xml'].decode('utf-8')

    # 1. Data da visita
    visit_date = config['visit_date']
    if SENT_DATA not in document_xml:
        raise ValueError('Sentinela de data nao encontrada no template (ja foi usado?)')
    document_xml = document_xml.replace(SENT_DATA, xml_escape(visit_date))

    # 2. Narrativa
    narrative = config.get('narrative', [])
    if isinstance(narrative, str):
        narrative = [p for p in narrative.split('\n\n') if p.strip()]
    narr_xml = build_narrative_paragraphs(narrative)
    if SENT_NARR not in document_xml:
        raise ValueError('Sentinela de narrativa nao encontrada no template')
    document_xml = document_xml.replace(SENT_NARR, narr_xml)

    # 3. Fotos
    sections = config.get('sections', [])
    photo_number = config.get('start_photo_number', 1)
    doc_pr_id = 900
    new_media = {}
    parts = []
    for section in sections:
        title = section.get('title', '')
        if title:
            parts.append(build_heading_paragraph(title))
        for photo in section.get('photos', []):
            path = photo['path']
            if not os.path.isfile(path):
                raise FileNotFoundError('Foto nao encontrada: %s' % path)
            ext = os.path.splitext(path)[1].lstrip('.').lower() or 'jpeg'
            rid = 'rId%d' % next_rid(rels_xml)
            media_name = 'image_%03d.%s' % (photo_number, ext)
            with open(path, 'rb') as f:
                new_media['word/media/%s' % media_name] = f.read()
            rels_xml = rels_xml.replace(
                '</Relationships>',
                '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/%s"/></Relationships>'
                % (rid, media_name),
            )
            content_types_xml = content_type_extension(ext, content_types_xml)
            cx, cy = extent_for(path)
            doc_pr_id += 1
            parts.append(build_photo_paragraphs(path, rid, doc_pr_id, cx, cy, media_name))
            parts.append(build_caption_paragraph(photo_number, photo.get('caption', '')))
            photo_number += 1
    fotos_xml = ''.join(parts) if parts else '<w:p/>'
    if SENT_FOTOS not in document_xml:
        raise ValueError('Sentinela de fotos nao encontrada no template')
    document_xml = document_xml.replace(SENT_FOTOS, fotos_xml)

    data['word/document.xml'] = document_xml.encode('utf-8')
    data['word/_rels/document.xml.rels'] = rels_xml.encode('utf-8')
    data['[Content_Types].xml'] = content_types_xml.encode('utf-8')
    data.update(new_media)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, content in data.items():
            zout.writestr(name, content)

    return photo_number - config.get('start_photo_number', 1)


def main():
    if len(sys.argv) < 2:
        print('Uso: python generate_report.py config.json', file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1], encoding='utf-8') as f:
        config = json.load(f)
    template_path = config.get('template_path') or DEFAULT_TEMPLATE
    out_path = config['output_path']
    count = generate(config, template_path, out_path)
    print(json.dumps({'output_path': out_path, 'photos_embedded': count}, ensure_ascii=False))


if __name__ == '__main__':
    main()
