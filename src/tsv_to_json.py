import argparse
import json
import os
import random
from typing import Tuple

from logzero import logger


def get_split_type(sent_id: str, sid2type: dict[str, str], is_rand_file: bool):
    if is_rand_file:
        return 'test2'

    assert sent_id in sid2type, sent_id
    return sid2type[sent_id]


def get_json_data_for_words(
        words: dict,
        feats: dict,
        
) -> Tuple[str, list[dict]]:

    text = ''
    words_json = []

    begin_idx = 0
    for word, feats, in zip(words, feats):
        text += word

        if len(feats) == 6:
            pos, ctype, cform, cates, nid, stds = feats
            yomi = base = lemma = lemma_id = None
        else:
            pos, ctype, cform, yomi, base, lemma, lemma_id, cates, nid, stds = feats

        words_json.append(
            {
                'surface'    : word,
                'span'       : [begin_idx, begin_idx+len(word)],
                'pos'        : pos,
                'conj_type'  : ctype,
                'conj_form'  : cform,
                'pron'       : yomi,
                'base'       : base,
                'lemma'      : lemma,
                'lemma_id'   : lemma_id,
                'word_cates' : cates,
                'norm_id'    : nid,
                'norm_forms' : stds,
            }
        )

        begin_idx += len(word)

    return text, words_json


def read_tsv_and_get_json(
        input_path: str,
        sid2type: dict[str, str],
        nid2stds: dict[str, set[str]],
        data: dict[str, dict] = None,
        min_info: bool = False,
) -> dict[str, dict]:

    if data is None:
        data = {'train': [],
                'dev'  : [],
                'test' : [],
                'test2': [],
        }

    sent_id = None
    words = []
    feats = []

    with open(input_path) as f:
        logger.info(f'Read: {input_path}')
        for line in f:
            line = line.rstrip('\n')

            if line.startswith('#'):
                if words:
                    stype = get_split_type(sent_id, sid2type, 'rand' in input_path)
                    text, words_info = get_json_data_for_words(words, feats)
                    data[stype].append({
                        'sent_id': sent_id,
                        'text': text,
                        'words': words_info,
                    })

                sent_id = line.split(' ')[1].split('=')[1]
                if not ':' in sent_id:
                    sent_id = f'{sent_id}:1'

                words = []
                feats = []
                continue

            elif line:
                array  = line.split('\t')
                # Note: for bert-japanese-char, which remove white spaces
                surf   = array[0].replace('\xa0', '　').replace('　', '_')
                pos    = array[1]
                ctype  = array[2]
                cform  = array[3]

                if min_info:
                    cates  = array[4]
                    nid    = array[5]
                else:
                    yomi     = array[4]
                    # Note: for bert-japanese-char, which remove white spaces
                    base     = array[5].replace('\xa0', '　').replace('　', '_')
                    lemma    = array[6]
                    lemma_id = array[7]
                    cates    = array[8]
                    nid      = array[9]

                if cates:
                    cates = [cate.strip(' ') for cate in cates.split(';')]
                else:
                    cates = []

                stds = []
                if nid == '<EMPTY>':
                    stds = ['']
                elif nid in nid2stds:
                    stds = nid2stds[nid]
                    
                words.append(surf)
                if min_info:
                    feats.append((pos, ctype, cform, cates, nid, stds))
                else:
                    feats.append((pos, ctype, cform, yomi, base, lemma, lemma_id, cates, nid, stds))

            else:
                if words:
                    stype = get_split_type(sent_id, sid2type, 'rand' in input_path)
                    text, words_info = get_json_data_for_words(words, feats)
                    data[stype].append({
                        'sent_id': sent_id,
                        'text': text,
                        'words': words_info,
                    })

                sent_id = None
                words = []
                feats = []

    return data


def read_norm_id_file(input_path: str):
    nid2stds = {}

    with open(input_path) as f:
        for li, line in enumerate(f):
            line = line.strip()
            if line.startswith('#'):
                continue

            array = line.split('\t')
            nid        = array[0]
            pos        = array[1]
            norm_strs  = array[2].split(',')
            nid2stds[nid] = norm_strs

    return nid2stds


def read_split_id_file(input_path: str) -> list[str]:
    sid2type = {}

    logger.info(f'Read: {input_path}')
    with open(input_path, encoding='utf-8') as f:
        for line in f:
            sid, split_type = line.rstrip('\n').split('\t')
            sid2type[sid] = split_type

    return sid2type


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_tsv_dir', '-i', type=str, required=True)
    parser.add_argument('--output_json_dir', '-o', type=str, required=True)
    parser.add_argument('--split_id_file_dir', '-s', type=str, required=True)
    parser.add_argument('--norm_id_file', '-n', type=str, required=True)
    args = parser.parse_args()

    domid2data = {}

    nid2stds = read_norm_id_file(args.norm_id_file)        

    for file_name in sorted(os.listdir(f'{args.input_tsv_dir}')):
        domain_id = '-'.join(file_name.split('-')[:-1])
        input_path = os.path.join(args.input_tsv_dir, file_name)

        if not file_name.endswith('.txt'):
            continue

        if file_name.endswith('rand.txt'):
            sid2type = {}       # all -> 'test2'
        else:
            split_id_file_path = os.path.join(args.split_id_file_dir, file_name)
            sid2type = read_split_id_file(split_id_file_path)

        if not domain_id in domid2data:
            data = read_tsv_and_get_json(input_path, sid2type, nid2stds, min_info=True)
            domid2data[domain_id] = data

        else:
            data = read_tsv_and_get_json(input_path, sid2type, nid2stds, min_info=True,
                                         data=domid2data[domain_id])

        logger.info(f'Convert tsv to json: train={len(data["train"])}, dev={len(data["dev"])}, test={len(data["test"])}, test2={len(data["test2"])}')

    for domain_id in domid2data:
        output_path = os.path.join(args.output_json_dir, f'{domain_id}.json')
        with open(output_path, 'w', encoding='utf-8') as fw:
            json.dump(domid2data[domain_id], fw, indent=2, ensure_ascii=False)
        logger.info(f'Saved: {output_path}')


if __name__ == '__main__':
    main()
