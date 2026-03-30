#!/bin/bash

#### RaktenData Ichiba

## This process will takes about 13 minutes to complete.

## Need to create symbolic link to the original data directory
## e.g.: ln -s /path/to/original_data original/RakutenData

## Prepare
INDIR=original/RakutenData/01_ichiba_2020
OUTDIR=data/temp/rakuten

mkdir -p $OUTDIR
python src/extract_sentence.py \
       -i data/id/05_RK-ICB-rand.txt,data/id/05_RK-ICB-ctrl.txt \
       -t $INDIR/shop_review/shop_review.2019-01.tsv,$INDIR/shop_review/shop_review.2019-02.tsv,$INDIR/shop_review/shop_review.2019-03.tsv,$INDIR/shop_review/shop_review.2019-04.tsv,$INDIR/shop_review/shop_review.2019-05.tsv,$INDIR/shop_review/shop_review.2019-06.tsv,$INDIR/shop_review/shop_review.2019-07.tsv,$INDIR/shop_review/shop_review.2019-08.tsv,$INDIR/shop_review/shop_review.2019-09.tsv,$INDIR/shop_review/shop_review.2019-10.tsv,$INDIR/shop_review/shop_review.2019-11.tsv,$INDIR/shop_review/shop_review.2019-12.tsv,$INDIR/item_review/item_review.2019-01.tsv,$INDIR/item_review/item_review.2019-02.tsv,$INDIR/item_review/item_review.2019-03.tsv,$INDIR/item_review/item_review.2019-04.tsv,$INDIR/item_review/item_review.2019-05.tsv,$INDIR/item_review/item_review.2019-06.tsv,$INDIR/item_review/item_review.2019-07.tsv,$INDIR/item_review/item_review.2019-08.tsv,$INDIR/item_review/item_review.2019-09.tsv,$INDIR/item_review/item_review.2019-10.tsv,$INDIR/item_review/item_review.2019-11.tsv,$INDIR/item_review/item_review.2019-12.tsv \
       -o $OUTDIR \
       --orig_data_type rakuten_ichiba \
       --normalize_characters \
       --html_unescape

## Create word/sentence-level data
for FILE_NAME in `echo "05_RK-ICB-ctrl.txt 05_RK-ICB-rand.txt"`; do
    echo $FILE_NAME
    python src/merge_word_info.py \
           -im data/mask/$FILE_NAME \
           -is $OUTDIR/$FILE_NAME \
           -os data/tsv/sent_level/$FILE_NAME \
           -ow data/tsv/word_level/$FILE_NAME \
           --unsegmented_sentences
done
