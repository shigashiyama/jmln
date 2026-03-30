#!/bin/bash

#### RaktenData Ichiba

## This process will takes about 2 minutes to complete.

## Need to create symbolic link to the original data directory
## e.g.: ln -s /path/to/original_data original/RakutenData

## Prepare
INDIR=original/RakutenData/02_Travel_2020
OUTDIR=data/temp/rakuten

mkdir -p $OUTDIR
python src/extract_sentence.py \
       -i data/id/06_RK-TRV-rand.txt,data/id/06_RK-TRV-ctrl.txt \
       -t $INDIR/01_Travel_Review.2017.tsv,$INDIR/01_Travel_Review.2018.tsv,$INDIR/01_Travel_Review.2019.tsv \
       -o $OUTDIR \
       --orig_data_type rakuten_travel \
       --normalize_characters \
       --html_unescape

## Create word/sentence-level data
for FILE_NAME in `echo "06_RK-TRV-ctrl.txt 06_RK-TRV-rand.txt"`; do
    echo $FILE_NAME
    python src/merge_word_info.py \
           -im data/mask/$FILE_NAME \
           -is $OUTDIR/$FILE_NAME \
           -os data/tsv/sent_level/$FILE_NAME \
           -ow data/tsv/word_level/$FILE_NAME \
           --unsegmented_sentences
done
