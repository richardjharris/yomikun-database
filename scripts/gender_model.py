"""
Train and check a gender model for Japanese given names.

TODO
 - consider kana w/o dots
 - vw-hyperscan
 - we don't dedupe names atm, so might be generating duplicate examples
   and overfitting the model for historical stuff
    - although this may be desirable (e.g. 'more males than females have this name')

VW cheatsheet
 label | feature_name:value (no value implies 1) feature is str or int
 label [weight] [prediction] ['tag]  weight defaults to 1, 0.5 is the initial predition (?)

 There are label namespaces, so this works. [recommended 1-character only]
 |kanji A B C |type post |stats views:10

 All features are numeric and have a name and a value.

 VW can create ngrams with -d2, which just combines sets of 2 adjacent
 tokens and adds a new feature for each.

 -q dt / -interactions dt does 'cross-features', ngrams across namespaces.

TO TEST
雅 - Masa (male name) or Miyabi (female name)
幸 - Kou (male name) or Miyuki (female name)
"""
import sys

from yomikun.gender.ml import GenderML, generate_examples

weights_file = 'data/gender.vw'
cache_file = 'data/gender.vw.cache'

if __name__ == '__main__':
    _script = sys.argv.pop(0)
    cmd = sys.argv.pop(0)

    if cmd == 'model':
        model = GenderML(cache_file)
        for example in generate_examples(sys.stdin):
            model.train_str(example)
        model.save(weights_file)
    elif cmd == 'query':
        model = GenderML(cache_file, weights_file)
        kaki, yomi = sys.argv
        print(model.predict(kaki, yomi))
    elif cmd == 'train':
        for example in generate_examples(sys.stdin):
            print(example)
    else:
        raise Exception(f'no such command "{cmd}"')
