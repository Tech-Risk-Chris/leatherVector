"""
    Combines multiple indices from various files. Since the words are sorted,
    we can do a one-pass merge sort.
"""

import sys
import gzip
import heapq


def index_line_generator(text_dir, book_id):
    with gzip.open(text_dir + '/index/mentions.csv.gz', mode='rt', encoding='utf-8') as f_in:
        first_line = True
        for line in f_in:
            if first_line:
                first_line = False
            else:
                spot = line.find(',')
                word = line[0:spot]
                trailer = line[spot:]
                yield word + ',' + book_id + trailer


if __name__ == "__main__":
    if len(sys.argv) == 1:
        text_dirs = ['text/novel/spy1821']
    else:
        text_dirs = sys.argv[1:]

    master_index = 'master-index.csv.gz'
    line_count = 0
    with gzip.open(master_index, mode='wt', encoding='utf-8') as f_out:
        print('Word,Work,Chapter,Sentence', file=f_out)
        index_iterators = []
        print(f'Preparing index iterators')
        for text_dir in text_dirs:
            id_file = f'{text_dir}/id'
            with open(id_file, 'r') as file:
                book_id = file.readline().strip()
                index_iterators.append(index_line_generator(text_dir, book_id))
        print(f'Writing master index tp {master_index}')
        for line in heapq.merge(*index_iterators):
            f_out.write(line)
            line_count += 1

    print(f'Processed {line_count} lines')


