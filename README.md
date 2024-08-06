# leatherVector
This project is trying to build an LLM for James Fenimoor Cooper questions
that is super-on-top of the actual contents of his novels.

For this purpose, the project is segmenting JFC's novels into sentences
for feeding into a RAG store.

# Preparation

## Get the Text

The project uses Gutenberg transcriptions of the Cooper novels.
The Gutenberg license is preserved in the `backm.txt` file of
every novel.

## Split into Sections

This uses `CHAPTER` and some form of `END OF GUTENBERG ...` markers
to slice out the front-matter, the chapters, and the back-matter
(which will contain the Gutenberg.org license and is therefore preserved.)

```bash
 python3 section.py pg9845.txt text/novel/spy1821
```
For some of the older texts, the back-matter won't get recognized properly;
you may have to hand-split the final chapter.

## Syntax Analyis

*Note:* This needs a GCP account, `gcloud` utilities installed, 
a project that has access to the syntax analysis API, and funding
(not a free API).

```bash
 cd text/novel/spy1821 && \
   source ../../../analyze_syntax.sh
```

## Indexing

The indexing works of the lemmata of the syntax and produces a `gzip`-compressed
`CSV` file of the lemmata in their chapter and sentence context.

```bash
  python3 index_text.py text/novel/spy1821
```


## Index Catenation

This step combines the sorted `gzip` compressed CSV files, prefixing each
with its `id` file, into one continuous master index.

```bash
  python3 combine_indices.py text/novel/* 
```

## Index Packing

This step converts and index into a Parquet file, so it can be used for
querying in a context that supports Presto (e.g. AWS Redshift).

```bash
  python3 pack_index.py pg9845 text/novel/spy1821
```

# RAG Import

_todo_
