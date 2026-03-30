#!/bin/bash

#### RecruiteData Blog/Review

## This process will takes about 2 minutes to complete.

## Need to create symbolic link to the original data directory
## e.g.: ln -s /path/to/original_data original/RecruiteData

## Prepare
INDIR=original/RecruiteData
OUTDIR=data/temp/recruite

mkdir -p $OUTDIR

python src/extract_sentence.py \
       -i data/id/03_RC-BLG-rand.txt,data/id/03_RC-BLG-ctrl.txt \
       -t $INDIR/2_BlogData_rev.tsv \
       -o $OUTDIR \
       --index_sent_id 2 \
       --index_sent_text 6 \
       --normalize_characters \
       --html_unescape

python src/extract_sentence.py \
       -i data/id/04_RC-REV-rand.txt,data/id/04_RC-REV-ctrl.txt \
       -t $INDIR/7_ReviewData_rev.tsv \
       -o $OUTDIR \
       --index_sent_id 2 \
       --index_sent_text 8 \
       --normalize_characters \
       --html_unescape

## Create word/sentence-level data
for FILE_NAME in `echo "03_RC-BLG-rand.txt 03_RC-BLG-ctrl.txt 04_RC-REV-rand.txt 04_RC-REV-ctrl.txt"`; do
    echo $FILE_NAME
    python src/merge_word_info.py \
           -im data/mask/$FILE_NAME \
           -is $OUTDIR/$FILE_NAME \
           -os data/tsv/sent_level/$FILE_NAME \
           -ow data/tsv/word_level/$FILE_NAME \
           --unsegmented_sentences
done
