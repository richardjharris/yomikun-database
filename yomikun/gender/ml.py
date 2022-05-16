"""
ML-based model for guessing first name genders
"""
from typing import cast

import vowpalwabbit

from yomikun.models.gender import Gender
from yomikun.models.name_position import NamePosition
from yomikun.models.namedata import NameData

# --nn didn't help
# -q kk or other values didn't help (as expected)
# However n-grams on kana -did- help (-q cc)
vw_args = (
    '-c --holdout_off --loss_function logistic -c -q kk --passes 5 '
    '-b 20 --l2 3e-6 -q cc --power_t 0.4'
)


class GenderML:
    def __init__(self, cache_file='gender.vw.cache', weights_file=None, quiet=False):
        self.cache_file = cache_file
        self.weights_file = weights_file
        if weights_file:
            self.model = vowpalwabbit.Workspace(
                initial_regressor=weights_file, quiet=quiet
            )
        else:
            self.model = vowpalwabbit.Workspace(
                f'{vw_args} --cache_file={cache_file}', quiet=quiet
            )

    def train_str(self, data):
        self.model.learn(data)

    def train(self, kaki: str, yomi: str, is_female: bool):
        ex = vw_example(vw_features(kaki, yomi), is_female)
        self.train_str(ex)

    def save(self, weights_file):
        self.model.save(weights_file)
        self.weights_file = weights_file

    def predict(self, kaki, yomi) -> float:
        test = vw_features(kaki, yomi)
        # `predict` function can return many types based on input, but in our case
        # it is a float.
        prediction = cast(float, self.model.predict(test))
        return prediction


# FIXME this has duplicate code with make.py
def generate_examples(jsonl_iterator):
    # Read jsonl from stdin
    for line in jsonl_iterator:
        data = NameData.from_jsonl(line)
        if data.is_dict:
            continue

        for part in data.extract_name_parts():
            if part.position != NamePosition.mei:
                continue
            if part.gender not in {Gender.male, Gender.female}:
                continue

            example = vw_example(
                vw_features(part.kaki, part.yomi), part.gender == Gender.female
            )
            yield example


def vw_example(features: str, is_female: bool):
    return f"{1 if is_female else -1} {features}"


def vw_features(kaki: str, yomi: str):
    """
    Vowpal Wabbit features for a name:
    |y yomi
    |c yomi kana characters
    |k kaki characters         - this is also bigrammed
    |l last_kaki
    |m last_yomi
    |n last_two_yomi           - new, may not really help
    |stats kaki_len:(kaki_len) yomi_len:(yomi_len)
    """

    last_kaki = kaki[-1]
    last_yomi = yomi[-1]
    last_two_yomi = yomi[-2:]
    kaki_len = len(kaki)
    yomi_len = len(yomi)
    ex = ' '.join(
        [
            f"|y {yomi}",
            f"|c {' '.join(yomi)}",
            f"|k {' '.join(kaki)}",
            f"|l {last_kaki}",
            f"|m {last_yomi}",
            f"|n {last_two_yomi}",
        ]
    )
    ex += f" |stats kaki_len:{kaki_len} yomi_len:{yomi_len}"
    return ex
