#!/usr/bin/env python3

"""
Extracts names from the EN wikipedia categories for male/female/unisex
Japanese given names. To be used in gender classification.
"""

import json
import logging

import mwclient
import regex

categories = (
    'Japanese masculine given names',
    'Japanese unisex given names',
    'Japanese feminine given names',
    'Japanese-language surnames',
)

site = mwclient.Site('en.wikipedia.org')

output = {}
for category in categories:
    names = {}
    continue_token = ''
    while True:
        result = site.get(
            'query',
            list='categorymembers',
            cmtitle='Category:' + category,
            cmlimit=500,
            cmcontinue=continue_token,
        )
        if 'warnings' in result:
            logging.exception(result['warnings'])

        for item in result['query']['categorymembers']:
            pageid = item['pageid']
            title = item['title']
            # Strip parens
            title = regex.sub(r'\s*\(.*?\)$', '', title)
            if len(title.split()) > 1:
                logging.warning(f"Skipping multi-word name '{title}'")
                continue

            names[pageid] = title

        if 'continue' in result:
            continue_token = result['continue']['cmcontinue']
        else:
            break

    output[category] = names

print(json.dumps(output, ensure_ascii=True))
