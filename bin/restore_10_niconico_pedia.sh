#!/bin/bash

#### Niconico Pedia

## This process will takes about 3 minutes to complete except data downloading.

## Need to download original data:
## 1. Open the data download page:
##    - 「ニコニコ大百科データ」ダウンロード
## 
## 2. Download files: head.zip, rev2008.zip, ..., and rev2014.zip
## 
## 3. Decompress the zip files and move csv files into a single directory.
##    e.g., NicoPedia

## Need to create symbolic link to the original data directory
## e.g.: ln -s /path/to/original_data original/NicoPedia

## Prepare
INDIR=original/NicoPedia
OUTDIR=data/temp/niconico

mkdir -p $OUTDIR
python src/extract_sentence.py \
       -i data/id/10_NC-PED-rand.txt,data/id/10_NC-PED-ctrl.txt \
       -t $INDIR \
       -o $OUTDIR \
       --orig_data_type nicopedia \
       --normalize_characters \
       --html_unescape \
       --remove_html_tag

## Create word/sentence-level data
for FILE_NAME in `echo "10_NC-PED-ctrl.txt 10_NC-PED-rand.txt"`; do
    echo $FILE_NAME
    python src/merge_word_info.py \
           -im data/mask/$FILE_NAME \
           -is $OUTDIR/$FILE_NAME \
           -os data/tsv/sent_level/$FILE_NAME \
           -ow data/tsv/word_level/$FILE_NAME \
           --unsegmented_sentences
done
