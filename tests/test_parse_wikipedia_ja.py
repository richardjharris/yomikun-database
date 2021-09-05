# Wikipedia articles are stored in a test directory (test_pages)
# with metadata (including expected results) at the top of each
# article.

from __future__ import annotations
from pathlib import Path

import yaml

from yomikun.models import NameAuthenticity, NameData, Lifetime
from yomikun.wikipedia_ja.parser import parse_wikipedia_article


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
    def get_id(path: Path):
        return str(path.name)

    if 'test_page' in metafunc.fixturenames:
        files = Path(__file__).parent.glob('wikipedia_ja_pages/*')
        metafunc.parametrize("test_page", files, ids=get_id)


def test_parser(test_page: Path):
    content, metadata = load_test(test_page)

    result = parse_wikipedia_article(test_page.name, content, add_source=False)
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
            birth, death = value.split('~')
            if len(birth.strip()):
                namedata.lifetime.birth_year = int(birth)
            if len(death.strip()):
                namedata.lifetime.death_year = int(death)
        elif key == 'title':
            # Article title, unused
            pass
        elif key == 'gender':
            # Gender tag, unused as gender detection is unimplemented
            pass
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
