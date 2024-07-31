"""
  index a text chapter by chapter from the gzipped JSON syntax

  The first chapter of _The Spy_ has the following lemmata
  (via <code>grep '"tag": ' | sort | uniq -c</code>)

      389         "tag": "ADJ",
      762         "tag": "ADP",
      247         "tag": "ADV",
      184         "tag": "CONJ",
      700         "tag": "DET",
     1176         "tag": "NOUN",
      17         "tag": "NUM",
     409         "tag": "PRON",
     100         "tag": "PRT",
     824         "tag": "PUNCT",
     803         "tag": "VERB",
       8         "tag": "X",

  Of these, ADJ, ADP, ADV, NOUN, NUM, PRT and VERB seem to be the only useful cases.
  Though ADP is sometimes "for" and ADV is sometimes "tough" ...
"""
import gzip
import json
import os
import sys
from collections import defaultdict

from common_utils import SectionType, file_name_generator

FOCAL_TAGS = ['ADJ', 'ADP', 'ADV', 'NOUN', 'NUM', 'PRT', 'VERB']


def LemmaStore():
    lemma_store = {}
    for focal_tag in FOCAL_TAGS:
        lemma_store[focal_tag] = defaultdict(lambda: defaultdict(int))
    return lemma_store


def load_syntax_analysis(file_path:str):
    if file_path.endswith('.gz'):
        # IntelliJ suggested: mode='rb'
        # copilot suggested: mode='rt', encoding='utf-8'
        with gzip.open(file_path, mode='rt', encoding='utf-8') as f:
            return json.load(f)
    else:
        with open(file_path, 'r') as f:
            return json.load(f)


def sentence_start_generator(sentences):
    for s_id, sentence in enumerate(sentences):
        details = sentence['text']
        offset = details['beginOffset']
        yield s_id, offset
    yield len(sentences), 2**60
    raise ValueError('Sentence start generator exhausted')


def analyze_tokens(tokens, s_start_generator, downcase=True):
    lemma_store = LemmaStore()
    s_id, _ = next(s_start_generator)
    s_next_id, s_next_offset = next(s_start_generator)
    for token in tokens:
        pos_tag = token['partOfSpeech']['tag']
        if pos_tag in lemma_store:
            offset = token['text']['beginOffset']
            lemma = token['lemma']
            # in case of degenerate sequences like: "Why?" "Because?"
            while offset > s_next_offset:
                s_id = s_next_id
                s_next_id, s_next_offset = next(s_start_generator)
            if downcase:
                lemma = lemma.lower()
            lemma_store[pos_tag][lemma][s_id] += 1
    return lemma_store, s_next_id


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = 'text/novel/spy1821'

    raw_syntax_path = f'{file_path}/syntax-raw'
    index_path = f'{file_path}/index'

    index_file = f'{index_path}/mentions.csv.gz'

    if os.path.exists(index_file):
        os.remove(index_file)

    records = 0
    total_sentences = 0
    with gzip.open(index_file, 'wt') as fidx:
        chapter_number = 1
        syntax_file = f'{raw_syntax_path}/{chapter_number:03}.json.gz'
        while os.path.exists(syntax_file):
            # load up the interpretation
            parse = load_syntax_analysis(syntax_file)
            sentence_generator = sentence_start_generator(parse['sentences'])
            lemma_store, sentence_count = analyze_tokens(parse['tokens'], sentence_generator)
            parse = None
            print(f'Analyzed {sentence_count} sentences from {syntax_file}')
            total_sentences += sentence_count
            # generate the index
            for focal_tag in FOCAL_TAGS:
                lemmata = lemma_store[focal_tag]
                for word in sorted(lemmata.keys()):
                    s_ids = lemmata[word]
                    for s_id in sorted(s_ids.keys()):
                        print(f'{word},{chapter_number},{s_id}', file=fidx)
                        records += 1
            # check for more work
            chapter_number += 1
            syntax_file = f'{raw_syntax_path}/{chapter_number:03}.json.gz'

    print(f'Processed {chapter_number-1} chapters with {total_sentences} sentences.')
    print(f'Wrote {records} records to {index_file}.')
