# VW cheatsheet
# label | feature_name:value (no value implies 1) feature is str or int
#  label [weight] [prediction] ['tag]  weight defaults to 1, 0.5 is the initial predition (?)
#
# There are label namespaces, so this works. [recommended 1-character only]
# |kanji A B C |type post |stats views:10
#
# All features are numeric and have a name and a value.
#
# VW can create ngrams with -d2, which just combines sets of 2 adjacent
# tokens and adds a new feature for each.
#
# -q dt / -interactions dt does 'cross-features', ngrams across namespaces.
#
# TO TEST
# 雅 - Masa (male name) or Miyabi (female name)
# 幸 - Kou (male name) or Miyuki (female name)
import sys
import click
from yomikun.gender.ml import GenderML, generate_examples


@click.group()
@click.option(
    '--weights-file', default='data/gender.vw', help='Source/target VW weights file'
)
@click.option(
    '--cache-file',
    default='data/gender.vw.cache',
    help='Cache to assist in repeated rebuilds',
)
@click.pass_context
def gender_model(ctx, weights_file, cache_file):
    """
    Manage the ML gender predictor
    """
    ctx.ensure_object(dict)
    ctx.obj['WEIGHTS_FILE'] = weights_file
    ctx.obj['CACHE_FILE'] = cache_file


@gender_model.command()
@click.pass_context
def model(ctx):
    """
    Build Gender predictor model

    Build and train a model using NameData JSONL input on stdin, and save
    the model.
    """
    genderml = GenderML(ctx.obj['CACHE_FILE'])
    for example in generate_examples(sys.stdin):
        genderml.train_str(example)
    genderml.save(ctx.obj['WEIGHTS_FILE'])


@gender_model.command()
@click.argument('kaki')
@click.argument('yomi')
@click.pass_context
def query(ctx, kaki, yomi):
    """
    Query the gender predictor

    Queries the predictor given the written (KAKI) and reading (YOMI)
    form of a given name and returns the estimated gender score. Reading
    should be in full-width kana.
    """
    genderml = GenderML(ctx.obj['CACHE_FILE'], ctx.obj['WEIGHTS_FILE'])
    print(genderml.predict(kaki, yomi))


@gender_model.command()
def train():
    """
    Generate training data

    Given NameData JSONL on stdin, output Vowpal Wabbit training data.

    Normally the ML model is trained by `yomikun build-gender-db` so this
    command is not used.
    """
    for example in generate_examples(sys.stdin):
        print(example)
