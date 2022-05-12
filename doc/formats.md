## JSONL (NameData)

Name information is collected in NameData python objects and serialised to and from JSONL
(JSON Lines) format. This is simply JSON except the file contains one JSON object per line,
and the object is serialised to only occupy one line (i.e. compact format).

There are several advantages to this format:
 1) As it is line based it is easy to split or aggregate the files, for example using `head`
    to test a script with a small number of inputs, or `parallel --pipe` to parallelise a
    script automatically, or `cat` to join inputs together.
 2) It can be filtered or queried using the `jq` tool, or in a pinch, `grep`.
 3) It is human readable

## Custom Data

A simpler CSV-based format for quick writing.

Comments (beginning with \#) and empty lines are ignored.

The five fields are:

* kaki - kanji form of name
* yomi - written form of name (in hiragana, although romaji is supported)
* tags:
 * 'm' for male given name or person
 * 'f' for female name or person
 * 's' for a surname
 * 'pseudo' for pseudonyms
 * 'fict' or 'fictional' for fictional characters
 * 'dict' for entries that do not represent a real person but should still be included
   for completeness as they are a possible valid reading.
* lifetime: birth year and death year separated by '-'. Either one is optional.
* notes: Description of the person. Currently unused.
