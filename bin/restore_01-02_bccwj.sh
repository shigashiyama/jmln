#!/bin/bash

#### BCCWJ OC/OY

## This process will takes about 1.5 minutes to complete.

## Need to create symbolic link to the original data directory
## e.g.: ln -s /path/to/original_data original/BCCWJ1.1

## Prepare
INDIR=original/BCCWJ1.1/Disk4/TSV_SUW_OT
OUTDIR=data/temp/bccwj
CORE_LIST=data/id/bccwj_core.list

mkdir -p $OUTDIR
python src/preprocess_bccwj.py -i $INDIR/OC/OC.txt -c $CORE_LIST -o $OUTDIR/OC_non-core.txt
python src/preprocess_bccwj.py -i $INDIR/OY/OY.txt -c $CORE_LIST -o $OUTDIR/OY_non-core.txt

## Create sentence-level data
python src/extract_sentence.py \
       -i data/id/01_BJ-OC-ctrl.txt,data/id/01_BJ-OC-rand.txt,data/id/01_BJ-OC-bqnc.txt \
       -t data/temp/bccwj/OC_non-core.txt \
       -o data/tsv/sent_level

python src/extract_sentence.py \
       -i data/id/02_BJ-OY-ctrl.txt,data/id/02_BJ-OY-rand.txt,data/id/02_BJ-OY-bqnc.txt \
       -t data/temp/bccwj/OY_non-core.txt \
       -o data/tsv/sent_level

## Create word-level data
for FILE_NAME in `echo "01_BJ-OC-ctrl.txt 01_BJ-OC-rand.txt 01_BJ-OC-bqnc.txt 02_BJ-OY-ctrl.txt 02_BJ-OY-rand.txt 02_BJ-OY-bqnc.txt"`; do
    echo $FILE_NAME
    python src/merge_word_info.py \
           -im data/mask/$FILE_NAME \
           -is data/tsv/sent_level/$FILE_NAME \
           -ow data/tsv/word_level/$FILE_NAME
done
