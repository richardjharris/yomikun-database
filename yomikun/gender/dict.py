import dataclasses
import json
from dataclasses import dataclass

DEFAULT_JSONL_PATH = 'db/gender.jsonl'


@dataclass
class GenderInfo:
    ml_score: float
    ct_score: float
    ct_confidence: float

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


class GenderDict:
    def __init__(self, file: str = DEFAULT_JSONL_PATH):
        self.dict = {}
        with open(file, encoding='utf-8') as fh:
            for line in fh:
                row = json.loads(line)
                key = (row['kaki'], row['yomi'])
                self.dict[key] = GenderInfo(
                    ml_score=row['ml_score'],
                    ct_score=row['ct_score'],
                    ct_confidence=row['ct_confidence'],
                )

    def lookup(self, kaki: str, yomi: str) -> GenderInfo | None:
        key = (kaki, yomi)
        return self.dict.get(key, None)
