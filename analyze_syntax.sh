#!/usr/bin/env bash
#
# Assumes that it is run from inside text/category/publication (eg text/novel/spy1821)
#
# sends all of the chapters off to GCloud's syntax analysis program
# requires a separate gCloud installation with Account &Project set
#
# Notice that GCloud has a 1M limit on file size. If the chapters are too long,
# you may have to hand-split them to make the analysis succeed.
#
for file in chapter/[0-9]*.txt; do
  syntax_file="syntax-raw/$(basename ${file%.txt}).json"
  echo $(date) 'Writing syntax analysis for' ${file} 'to' ${syntax_file} '...'
  rm -vf ${syntax_file} "${syntax_file}.gz"
  gcloud ml language analyze-syntax --content-file=${file} > ${syntax_file}
  gzip --best --verbose ${syntax_file}
done
