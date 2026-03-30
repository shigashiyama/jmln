#!/bin/bash

#### Skype Corpus

## This process will takes about 10 seconds to complete.

## Need to create symbolic link to the original data directory
## e.g.: ln -s /path/to/original_data original/skype

## Prepare
INDIR=original/Skype_Corpus
OUTDIR=data/temp/skype

mkdir -p $OUTDIR/data_utf

: > $OUTDIR/SK_all.txt
for FILE_NAME in `ls $INDIR`; do
    echo "Convert to UTF-8 data: $INDIR/$FILE_NAME"
    nkf -w $INDIR/$FILE_NAME > $OUTDIR/data_utf/$FILE_NAME
    python src/preprocess_sk.py $OUTDIR/data_utf/$FILE_NAME >> $OUTDIR/SK_all.txt
done
echo "Saved: $OUTDIR/SK_all.txt"

python src/extract_sentence.py \
       -i data/id/14_SK-rand.txt,data/id/14_SK-ctrl.txt \
       -t $OUTDIR/SK_all.txt \
       -o $OUTDIR \
       --index_sent_id 1 \
       --index_sent_text 4

## Create word/sentence-level data
for FILE_NAME in `echo "14_SK-rand.txt 14_SK-ctrl.txt"`; do
    echo $FILE_NAME
    python src/merge_word_info.py \
           -im data/mask/$FILE_NAME \
           -is $OUTDIR/$FILE_NAME \
           -os data/tsv/sent_level/$FILE_NAME \
           -ow data/tsv/word_level/$FILE_NAME \
           --unsegmented_sentences
done
