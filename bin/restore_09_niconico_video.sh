#!/bin/bash

#### Niconico Video Comment

## This process will takes about 4.5 minutes to complete except data downloading.

## Need to download original data:
## 1. Open the data download page:
##    - 「ニコニコ動画コメント等データ」
##    -> 旧データ「2018年12月14日版」
##   -> 動画メタデータ「ファイルリスト」
## 
## 2. Download files: 3251.zip ... 3410.zip
## 
## 3. Decompress the zip files and move jsonl files into a single directory.
##    e.g., NicoComm_data.20181214

## Need to create symbolic link to the original data directory
## e.g.: ln -s /path/to/original_data original/NicoComm_data.20181214

## Prepare
INDIR=original/NicoComm_data.20181214/video
OUTDIR=data/temp/niconico

mkdir -p $OUTDIR
python src/extract_sentence.py \
       -i data/id/09_NC-VID-rand.txt,data/id/09_NC-VID-ctrl.txt \
       -t $INDIR \
       -o $OUTDIR \
       --orig_data_type niconico_video \
       --normalize_characters \
       --html_unescape \
       --remove_html_tag

## Create word/sentence-level data
for FILE_NAME in `echo "09_NC-VID-ctrl.txt 09_NC-VID-rand.txt"`; do
    echo $FILE_NAME
    python src/merge_word_info.py \
           -im data/mask/$FILE_NAME \
           -is $OUTDIR/$FILE_NAME \
           -os data/tsv/sent_level/$FILE_NAME \
           -ow data/tsv/word_level/$FILE_NAME \
           --unsegmented_sentences
done
