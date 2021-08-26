# Wikipedia articles are stored in a test directory (test_pages)
# with metadata (including expected results) at the top of each
# article.

from pathlib import Path

from wikipedia.parser import parse_wikipedia_article


def load_test(file: Path) -> tuple[str, str]:
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

    return ''.join(content), ''.join(header)


def pytest_generate_tests(metafunc):
    def get_id(path: Path):
        return str(path.name)

    if 'test_page' in metafunc.fixturenames:
        files = Path(__file__).parent.glob('test_pages/*')
        metafunc.parametrize("test_page", files, ids=get_id)


def test_parser(test_page: Path):
    content, header = load_test(test_page)

    result = parse_wikipedia_article(content)
    if result:
        assert str(result) == header
    else:
        assert header == "\n"
