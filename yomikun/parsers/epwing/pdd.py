# Parses PDD (public domain dictionary) 人名辞典.


import logging

import regex

from yomikun.models import NameData
from yomikun.utils.patterns import (
    hiragana_pat,
    name_pat,
    name_pat_with_space,
    reading_pat,
)


def name_from_entry(heading: str, text: str) -> NameData | None:
    """
    Extract NameData from a PDD (public domain dictionary) name database entry.

    Heading format: "いのうえ　ああ【井上　唖々】"
    Text format: (as above) + \n + 1878. 1.30(明治11) 〜 1923. 7.11(大正12)

    We currently ignore the (useful) text that follows the birth/death dates.

    * Start date is often 生年不詳 but the tilde always separates them.

    * Sometimes header contains a second form of the name:
      梅原　竜三郎(梅原　龍三郎)
      or a generation:
      [1]うめわか　みのる【梅若　実(初世)】
      [2]うめわか　みのる【梅若　実(二世)】
      さんゆうてい　えんしょう【三遊亭　円生(６代)】

      A few lack spaces:
      みなもとのたかあきら【源　高明】
    """
    namedata = None
    if m := regex.search(fr'^(?:\[\d+\])?(.*?)【({name_pat})(?:\((.*?)\))?】', heading):
        yomi, kaki, alt_kaki = m.groups()

        # Determine if alternate kanji is actually a name, and not just 二世 or
        # similar.
        if alt_kaki and regex.match(fr'^({name_pat_with_space})$', alt_kaki):
            logging.info(f'Found alternate name for {kaki}: {alt_kaki}')
        else:
            alt_kaki = None

        if regex.match(reading_pat, yomi):
            pass
        elif regex.match(hiragana_pat, yomi) and yomi.count('の') == 1:
            yomi = yomi.replace('の', ' ')
        else:
            logging.warning(f'Unrecognized yomi: {yomi}')
            return

        # Some entries have a '??' suffix after the reading - remove them.
        yomi = regex.sub(r'\s*\?+$', '', yomi)
        yomi = regex.sub(r'子$', 'こ', yomi)

        namedata = NameData.person(kaki, yomi)

        if alt_kaki:
            namedata.add_subreading(NameData.person(alt_kaki, yomi))

    if not namedata:
        logging.warning(f"Cannot parse heading {heading}")
        return

    lines = text.splitlines()

    if len(lines) < 2:
        return

    result = text.splitlines()[1].split('〜')
    if len(result) == 2:
        left, right = result
        if m := regex.search(r'^\s*(\d{3,4})[\.\(]', left):
            namedata.lifetime.birth_year = int(m[1])
        if m := regex.search(r'^\s*(\d{3,4})[\.\(]', right):
            namedata.lifetime.death_year = int(m[1])

    namedata.source = f'pdd:{heading}'

    namedata.validate()
    return namedata
