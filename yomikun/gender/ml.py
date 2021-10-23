"""
ML-based model for guessing first name genders
"""
import json

from vowpalwabbit import pyvw

# --nn didn't help
# -q kk or other values didn't help (as expected)
# However n-grams on kana -did- help (-q cc)
vw_args = '-c --holdout_off --loss_function logistic -c -q kk --passes 5 -b 20 --l2 3e-6 -q cc --power_t 0.4'


class GenderML():
    def __init__(self, cache_file='gender.vw.cache', weights_file=None, quiet=False):
        self.cache_file = cache_file
        self.weights_file = weights_file
        if weights_file:
            self.model = pyvw.vw(initial_regressor=weights_file, quiet=quiet)
        else:
            self.model = pyvw.vw(
                f'{vw_args} --cache_file={cache_file}', quiet=quiet)

    def train_str(self, data):
        self.model.learn(data)

    def train(self, kaki: str, yomi: str, is_female: bool):
        ex = vw_example(vw_features(kaki, yomi), is_female)
        self.train_str(ex)

    def save(self, weights_file):
        self.model.save(weights_file)
        self.weights_file = weights_file

    def predict(self, kaki, yomi):
        test = vw_features(kaki, yomi)
        prediction = self.model.predict(test)
        return prediction


def generate_examples(jsonl_iterator):
    people = set()

    # Read jsonl from stdin
    for line in jsonl_iterator:
        data = json.loads(line)

        # Ignore non-people.
        if len(data['kaki'].split()) != 2 or len(data['yomi'].split()) != 2:
            continue

        # Ignore entries without a masc/fem tag, e.g. jmnedict
        if 'masc' not in data['tags'] and 'fem' not in data['tags']:
            continue

        if 'masc' in data['tags'] and 'fem' in data['tags']:
            # A few fem FPs left in, should be fixed later
            data['tags'].remove('fem')

        # Hash people to deduplicate them
        key = (data['kaki'], data.get('lifetime', {}).get('birth_year', None))
        if key in people:
            continue

        people.add(key)

        mei = data['kaki'].split()[1]
        mei_yomi = data['yomi'].split()[1]
        is_female = 'fem' in data['tags']
        example = vw_example(vw_features(mei, mei_yomi), is_female)
        yield example


def vw_example(features: str, is_female: bool):
    return f"{1 if is_female else -1} {features}"


def vw_features(kaki, yomi):
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
    ex = f"|y {yomi} |c {' '.join(yomi)} |k {' '.join(kaki)} |l {last_kaki} |m {last_yomi} |n {last_two_yomi}"
    ex += f" |stats kaki_len:{kaki_len} yomi_len:{yomi_len}"
    return ex
