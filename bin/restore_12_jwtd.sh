#!/bin/bash

#### JWTD (v2)

## These steps are not necessary because this repository originaly contains the complete anntation data: data/tsv/{word,sent}_level/12_JW-ctrl.txt

## This process will takes within 1 minute to complete.

## Need to download original data (JWTDv2.0.tar.gz) and decompress it.

## Need to create symbolic link to the original data directory
## e.g.: ln -s /path/to/original_data original/JWTD2.0

## Prepare
INDIR=original/JWTD2.0
OUTDIR=data/temp/jwtd

mkdir -p $OUTDIR
python src/extract_sentence.py \
       -i data/id/12_JW-ctrl.txt \
       -t $INDIR/train.jsonl,$INDIR/test.jsonl \
       -o $OUTDIR \
       --orig_data_type jwtd \
       --normalize_characters \
       --html_unescape \
       --remove_html_tag

## Create word/sentence-level data
FILE_NAME=12_JW-ctrl.txt
python src/merge_word_info.py \
       -im data/mask/$FILE_NAME \
       -is $OUTDIR/$FILE_NAME \
       -os data/tsv/sent_level/$FILE_NAME \
       -ow data/tsv/word_level/$FILE_NAME \
       --not_output_orig_sentid
