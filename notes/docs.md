## Makefile process

 - db/deduped.json is deduped people + other records
    {kaki, yomi, authenticity, lifetime, source, tags} for people + non-people

 - db/gender.json genderated from above
    {kaki, yomi, ml_Score, ct_score, hits_male etc}

- db/final.json takes deduped and converts to sqlite schema
    {kaki, yomi, part, ml_score, hits_*}   - no people

 - db/final.db loads json into sqlite