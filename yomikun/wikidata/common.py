"""
Common helper methods for wikidata parsing.
"""


def extract(data: dict, path: str) -> str | None:
    """
    Extracts an item from a nested dictionary. Example:

    extract({"foo": {"bar": "hello"}}, "foo.bar") == "hello"

    Returns None if the item does not exist. Throws AssertionError
    if the value was found but was not a string. Throws TypeError
    if a string is encountered where a dict was expected.
    """
    parts = path.split('.')
    try:
        while parts:
            data = data[parts.pop(0)]
        assert isinstance(data, str)
        return data
    except KeyError:
        return None


def year(date: str | None):
    """
    Extracts the year out of a wikidata date value. Returns None if the
    data does not exist or is a bnode.
    """
    if date:
        if date.startswith('t'):
            # Is a bnode
            return None
        return int(date[0:4])
    else:
        return None
