from __future__ import annotations

from dataclasses import dataclass, field

import regex
from mediawiki_dump.tokenizer import clean

from yomikun.models import NameData
from yomikun.utils.patterns import name_paren_start, name_pat, reading_pat
from yomikun.utils.split import split_kanji_name


@dataclass
class Infobox:
    name: str
    data: dict[str, str] = field(default_factory=dict)

    def add(self, key: str, value: str):
        key = key.strip()
        value = value.strip()
        if len(key) and len(value):
            self.data[key] = value

    def first_set(self, *keys: str) -> str | None:
        for key in keys:
            if key in self.data:
                return key
        return None

    def __getitem__(self, key: str) -> str:
        return self.data[key]

    def __contains__(self, key: str) -> bool:
        return key in self.data


def extract_year(value: str) -> int | None:
    # year by itself
    if regex.fullmatch(r'\d{4}', value):
        return int(value)
    # year followed by 年 kanji
    elif m := regex.search(r'(\d{4})年', value):
        return int(m[1])
    # gotcha: this template takes a second year
    elif m := regex.search(r'\{\{死亡年月日と没年齢\|\d{4}\|\d+\|\d+\|(\d{4})\|', value):
        return int(m[1])
    # year inside a template declaration
    elif m := regex.search(r'\|(\d{4})\|', value):
        return int(m[1])
    else:
        return


def extract_infoboxes(wikitext: str) -> list[Infobox]:
    """
    Rudimentary infobox parser and extractor.

    This is very basic: it will look for lines beginning with a template
    declaration ({{) followed by '| name = value' pairs, and a close template
    declaration (}}). It does not handle anything complex like recursive
    templates. This is generally enough for most pages.

    For better parsing, the remote Wikipedia API can be used directly to
    return infobox data.
    """
    infoboxes = []
    cur = None

    for line in wikitext.splitlines():
        # Match start of new template. Would check if line contains }} but there is
        # one counter-example: '{{Anchors|坪田愛華}}{{Infobox 人物'
        if m := regex.search(r'^\{\{\s*(\S+.*?)$', line):
            if cur is None:
                cur = Infobox(name=m[1])
        elif m := regex.search(r'^\s*\|\s*(\S+)\s*=\s*(.*)$', line):
            key, value = m.groups()
            if cur:
                cur.add(key, value)
        elif m := regex.search(r'^\}\}', line):
            if cur is not None:
                infoboxes.append(cur)
            cur = None

    if cur:
        infoboxes.append(cur)

    return infoboxes


def parse_infoboxes(boxes: list[Infobox]) -> NameData:
    """
    Extract infoboxes and produce a result containing all extracted
    information.
    """
    result = NameData()
    lifetime = result.lifetime
    name_set = False

    for box in boxes:
        if not name_set:
            if key := box.first_set('人名', '名前', '芸名', '氏名', 'name'):
                if m := regex.search(
                    r'^[\p{Han}]+\s+[\p{Han}\p{Hiragana}\p{Katakana}]+$', box[key]
                ):
                    result.kaki = box[key]
                    name_set = True

            if key := box.first_set('ふりがな', '各国語表記', 'native_name'):
                if m := regex.search(r'^\p{Hiragana}+\s+\p{Hiragana}+$', box[key]):
                    result.yomi = box[key]
                    name_set = True

        if (
            key := box.first_set('生年月日', '生年', '生誕', 'birth_date', 'Born', 'birthdate')
        ) and not lifetime.birth_year:
            lifetime.birth_year = extract_year(box[key])

        if (
            key := box.first_set(
                '没年月日', '没年', '死没', 'death_date', '失踪年月日', 'Died', 'deathdate'
            )
        ) and not lifetime.death_year:
            lifetime.death_year = extract_year(box[key])

        if key := box.first_set('性別'):
            value = clean(box[key])
            if value in ('女性', '女'):
                result.add_tag("fem")
            elif value in ('男性', '男'):
                result.add_tag("masc")

        if key := box.first_set('職業'):
            if regex.search('女優', clean(box[key])):
                result.add_tag("fem")

        if key := box.first_set('フリーサイズ', 'カップサイズ'):
            result.add_tag('fem')

        if key := box.first_set('本名'):
            value = clean(box[key])
            if m := regex.search(
                fr'^({name_pat})\s*{name_paren_start}({reading_pat})', value
            ):
                kaki, yomi = m.groups()
                kaki = split_kanji_name(kaki, yomi)
                subreading = NameData(kaki, yomi)
                result.add_honmyo(subreading)

        # 公家 entries are quite old, so safe to assume that if 妻 is populated then it's a man.
        if box.name == '基礎情報 公家' and '妻' in box:
            value = clean(box['妻'])
            if value:
                result.add_tag('masc')

    result.clean()
    return result
