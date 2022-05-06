"""
Parsers for EPWING-format dictionaries. Because EPWING is a very
complicated format, dictionaries must first be converted to JSON
using Zero-EPWING ( https://github.com/FooSoft/zero-epwing ).

Example command:

  zero-epwing -p -e /path/to/epwing | gzip > dict.json.gz
"""
