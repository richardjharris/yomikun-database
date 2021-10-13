# Wikipedia articles are stored in a test directory (test_pages)
# with metadata (including expected results) at the top of each
# article.

from __future__ import annotations
import itertools
from pathlib import Path
from yomikun.models.lifetime import Lifetime

import yaml

from yomikun.models import NameAuthenticity, NameData
import yomikun.wikipedia_en.parser
import yomikun.wikipedia_ja.parser


def load_test(file: Path) -> tuple[str, dict]:
    content = []
    header = []
    in_header = True

    for line in file.open():
        if line.startswith('---'):
            in_header = False
            continue

        if in_header:
            header.append(line)
        else:
            content.append(line)

    assert len(content)

    metadata: dict = yaml.load(''.join(header), Loader=yaml.BaseLoader)

    return ''.join(content), metadata


def pytest_generate_tests(metafunc):
    def get_id(test_page: tuple[Path, str]):
        path, lang = test_page
        return f"{lang}_{path.name}"

    if 'test_page' in metafunc.fixturenames:
        ja_files = ((file, 'ja') for file in Path(
            __file__).parent.glob('wikipedia_ja_pages/*'))
        en_files = ((file, 'en') for file in Path(
            __file__).parent.glob("wikipedia_en_pages/*"))

        files = itertools.chain(ja_files, en_files)

        metafunc.parametrize("test_page", files, ids=get_id)


def test_parser(test_page: tuple[Path, str]):
    path, lang = test_page
    content, metadata = load_test(path)

    if lang == 'en':
        module = yomikun.wikipedia_en.parser
    elif lang == 'ja':
        module = yomikun.wikipedia_ja.parser
    else:
        raise Exception('invalid lang')

    result = module.parse_wikipedia_article(
        path.name, content, add_source=False)

    result.remove_tag('xx-romaji')
    result.remove_tag('xx-split')

    expected = build_namedata_from_test_header(metadata)

    assert result == expected


def build_namedata_from_test_header(metadata: dict) -> NameData | None:
    # TODO this should probably go in NameData.from_yaml or similar
    namedata = NameData()
    for key, value in metadata.items():
        if key == 'name':
            namedata.kaki = value
        elif key == 'reading':
            namedata.yomi = value
        elif key == 'type':
            namedata.authenticity = NameAuthenticity[value.upper()]
        elif key == 'lifetime':
            namedata.lifetime = Lifetime.from_string(value)
        elif key == 'title':
            # Article title, unused
            pass
        elif key == 'gender':
            # If gender is specified, it must match. Otherwise any gender
            # is accepted.
            if value == 'M':
                namedata.add_tag('masc')
            elif value == 'F':
                namedata.add_tag('fem')
            else:
                raise Exception(f"Unknown gender value '{value}'")
        elif key == 'tags':
            for tag in value:
                namedata.add_tag(tag)
        elif key == 'source':
            # Article source URL
            pass
        elif key == 'subreadings':
            for subreading_data in value:
                subreading = build_namedata_from_test_header(subreading_data)
                assert subreading is not None
                namedata.add_subreading(subreading)
        else:
            raise Exception(f"invalid test key '{key}'")

    return namedata
