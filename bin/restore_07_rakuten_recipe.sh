#!/bin/bash

#### RaktenData Recipe

## This process will takes about 1 minute to complete.

## Need to create symbolic link to the original data directory
## e.g.: ln -s /path/to/original_data original/RakutenData

## Prepare
INDIR=original/RakutenData/recipe_20170118
OUTDIR=data/temp/rakuten

mkdir -p $OUTDIR
python src/extract_sentence.py \
       -i data/id/07_RK-RCP-rand.txt,data/id/07_RK-RCP-ctrl.txt \
       -t $INDIR/recipe01_all_20170118.txt,$INDIR/recipe03_process_20160112.txt,$INDIR/recipe04_tsukurepo_20160112.txt \
       -o $OUTDIR \
       --orig_data_type rakuten_recipe \
       --normalize_characters \
       --html_unescape

## Create word/sentence-level data
for FILE_NAME in `echo "07_RK-RCP-ctrl.txt 07_RK-RCP-rand.txt"`; do
    echo $FILE_NAME
    python src/merge_word_info.py \
           -im data/mask/$FILE_NAME \
           -is $OUTDIR/$FILE_NAME \
           -os data/tsv/sent_level/$FILE_NAME \
           -ow data/tsv/word_level/$FILE_NAME \
           --unsegmented_sentences
done
