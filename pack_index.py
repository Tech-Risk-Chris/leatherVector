"""
    Converts a set of compressed mentions indices (see index_text) into
    a single Parquet file that is sorted by words and has a separate
    column for the book in question (which is implied in the mentions index).

    The current implementation does the SORT in-memory ... this is eventually
    going to become unsustainable. Some Presto implementations repack
    the Parquet files during import (e.g AWS Redshift) ... there it
    would not matter.

    There is a way for serial appending, though
    @see https://stackoverflow.com/questions/75468395/merge-small-parquet-files-into-a-single-large-parquet-file
"""
import os
import sys
import pandas as pd
import gzip

if __name__ == "__main__":
    if len(sys.argv) > 1:
        book_id = sys.argv[1]
        if len(sys.argv) > 2:
            source_directory = sys.argv[2]
        else:
            source_directory = 'text/novel/spy1821'
    else:
        book_id = 'pg9845'

    # Path to your compressed CSV file
    csv_gz_path = f'{source_directory}/index/mentions.csv.gz'

    # Read the compressed CSV file
    with gzip.open(csv_gz_path, 'rt', encoding='utf-8') as f:
        df = pd.read_csv(f)

    print(f'Loaded {len(df)} rows from {csv_gz_path}')

    # insert the file designation and reorder
    print(f'Inserting column for work ID with ID {book_id}')
    old_columns = df.columns.tolist()
    df['Work'] = book_id
    df = df[ ['Work'] + old_columns ]

    # Sort the DataFrame by the desired columns
    print(f'Sorting columns ... ')
    sorted_df = df.sort_values(by=['Word','Chapter','Sentence'])
    print(f' ... done')

    """
  Which deflater to use?
  
  The raw CSV index is the baseline, but that is unfair, since
  it is generated without a 'Work' column ...
  
    420K	text/novel/spy1821/index/mentions.csv.gz

  For Parquet compression, one can use 'snappy, 'gzip', 'brotli' (2024/07)
  - w/out work column
    552K	text/novel/spy1821/index/mentions.brotli.parquet
    604K	text/novel/spy1821/index/mentions.gzip.parquet
    844K	text/novel/spy1821/index/mentions.snappy.parquet

  - with work column
    616K	text/novel/spy1821/index/mentions.brotli.parquet
    668K	text/novel/spy1821/index/mentions.gzip.parquet 
    908K	text/novel/spy1821/index/mentions.snappy.parquet

  Unsurprisingly, given these numbers, we use brotli as our default deflater.
"""

    deflater = 'brotli'

    # Convert the sorted DataFrame to a Parquet file
    parquet_path = f'{source_directory}/index/mentions.parquet'
    print(f'Writing columns to {parquet_path} using {deflater} compression')
    # required by Amazon Redshift, possibly by Athena too, to suppress the
    # __index_level_0__ column; cf. https://pandas.pydata.org/docs/user_guide/io.html#handling-indexes
    sorted_df.to_parquet(parquet_path, compression=deflater, index=False)
    print('Done, done, and done.')
