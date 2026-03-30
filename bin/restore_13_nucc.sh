#!/bin/bash

#### NUCC

## This process will takes about 20 seconds to complete.

## Need to download original data (nucc.zip) and decompress it.

## Need to create symbolic link to the original data directory
## e.g.: ln -s /path/to/original_data original/nucc

## Prepare
INDIR=original/nucc
OUTDIR=data/temp/nucc
TARGET_FILE_LIST=data/id/13_NU_target_files.txt

mkdir -p $OUTDIR
for FILE_NAME in `cat $TARGET_FILE_LIST`; do
    python src/preprocess_nucc.py -i $INDIR/$FILE_NAME -o $OUTDIR/$FILE_NAME
done

python src/extract_sentence.py \
       -i data/id/13_NU-rand.txt,data/id/13_NU-ctrl.txt \
       -t $OUTDIR \
       -o $OUTDIR \
       --index_sent_id 1 \
       --index_sent_text 4

## Create word/sentence-level data
for FILE_NAME in `echo "13_NU-rand.txt 13_NU-ctrl.txt"`; do
    echo $FILE_NAME
    python src/merge_word_info.py \
           -im data/mask/$FILE_NAME \
           -is $OUTDIR/$FILE_NAME \
           -os data/tsv/sent_level/$FILE_NAME \
           -ow data/tsv/word_level/$FILE_NAME
done
