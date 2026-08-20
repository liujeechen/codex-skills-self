#!/usr/bin/env python3
import argparse
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, BadZipFile
import xml.etree.ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
CHAPTERS = {'修改说明', '自测结论', '自测方案', '自测记录'}
MANUAL_PREFIXES = ('一、修改说明', '二、自测结论', '三、自测方案', '四、自测记录')


def paragraph_text(p):
    return ''.join(t.text or '' for t in p.iter(W + 't')).strip()


def ensure_rpr(r):
    rpr = r.find(W + 'rPr')
    if rpr is None:
        rpr = ET.Element(W + 'rPr')
        r.insert(0, rpr)
    return rpr


def remove_bold(r):
    rpr = ensure_rpr(r)
    for tag in (W + 'b', W + 'bCs'):
        for node in rpr.findall(tag):
            rpr.remove(node)


def set_black(r):
    rpr = ensure_rpr(r)
    color = rpr.find(W + 'color')
    if color is None:
        color = ET.SubElement(rpr, W + 'color')
    color.set(W + 'val', '000000')
    for key in ('themeColor', 'themeTint', 'themeShade'):
        color.attrib.pop(W + key, None)


def indent_two_chars(p):
    ppr = p.find(W + 'pPr')
    if ppr is None:
        ppr = ET.Element(W + 'pPr')
        p.insert(0, ppr)
    ind = ppr.find(W + 'ind')
    if ind is None:
        ind = ET.SubElement(ppr, W + 'ind')
    ind.set(W + 'firstLineChars', '200')
    for key in ('hanging', 'hangingChars'):
        ind.attrib.pop(W + key, None)


def normalize(doc):
    body = doc.find(W + 'body')
    table_paragraphs = {id(p) for tc in doc.iter(W + 'tc') for p in tc.iter(W + 'p')}
    for p in doc.iter(W + 'p'):
        text = paragraph_text(p)
        is_title = text.endswith('自测报告') and text not in CHAPTERS
        is_chapter = text in CHAPTERS
        is_subhead = text.startswith(('TC', '1. ', '2. ', '3. ', '4. ', '5. ', '6. '))
        is_label = text.endswith('：')
        is_hint = text.startswith(('对应提交：', '备注说明：'))
        for r in p.iter(W + 'r'):
            set_black(r)
            if not (is_title or is_chapter or is_subhead or is_label):
                remove_bold(r)
        if text and id(p) not in table_paragraphs and not (is_title or is_chapter or is_subhead or is_label or is_hint):
            indent_two_chars(p)
    for tbl in doc.iter(W + 'tbl'):
        rows = tbl.findall(W + 'tr')
        for row in rows[1:]:
            for r in row.iter(W + 'r'):
                remove_bold(r)


def validate(doc):
    errors = []
    texts = [paragraph_text(p) for p in doc.iter(W + 'p')]
    for chapter in CHAPTERS:
        if chapter not in texts:
            errors.append(f'缺少章节：{chapter}')
    for text in texts:
        if text.startswith(MANUAL_PREFIXES):
            errors.append(f'章节标题含手工编号：{text}')
    for r in doc.iter(W + 'r'):
        if not paragraph_text(r):
            continue
        color = r.find('./' + W + 'rPr/' + W + 'color')
        if color is None or color.get(W + 'val', '').upper() != '000000':
            errors.append('存在非纯黑色文字')
            break
    tables = list(doc.iter(W + 'tbl'))
    if not tables:
        errors.append('缺少自测结论表格')
    else:
        rows = tables[0].findall(W + 'tr')
        if not rows:
            errors.append('自测结论表格为空')
        else:
            header = [''.join(t.text or '' for t in tc.iter(W + 't')).strip() for tc in rows[0].findall(W + 'tc')]
            expected = ['测试模块', '测试方案', '测试用例', '测试结果', '备注说明']
            if header != expected:
                errors.append('自测结论表头不符合模板')
            for row in rows[1:]:
                cells = row.findall(W + 'tc')
                if len(cells) >= 4 and ''.join(t.text or '' for t in cells[3].iter(W + 't')).strip():
                    errors.append('测试结果列必须留空')
                    break
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('docx', type=Path)
    args = parser.parse_args()
    try:
        with ZipFile(args.docx, 'r') as zin:
            files = {name: zin.read(name) for name in zin.namelist()}
    except (FileNotFoundError, BadZipFile) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2
    try:
        doc = ET.fromstring(files['word/document.xml'])
    except (KeyError, ET.ParseError) as exc:
        print(f'ERROR: 非有效DOCX文档: {exc}', file=sys.stderr)
        return 2
    normalize(doc)
    ET.register_namespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')
    files['word/document.xml'] = ET.tostring(doc, encoding='utf-8', xml_declaration=True)
    temp = Path(tempfile.mkstemp(suffix='.docx', dir=args.docx.parent)[1])
    try:
        with ZipFile(temp, 'w', ZIP_DEFLATED) as zout:
            for name, data in files.items():
                zout.writestr(name, data)
        temp.replace(args.docx)
    finally:
        if temp.exists():
            temp.unlink()
    errors = validate(doc)
    if errors:
        for error in errors:
            print(f'ERROR: {error}', file=sys.stderr)
        return 1
    print(f'OK: {args.docx}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
