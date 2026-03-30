import argparse
import csv
import json
import os

import logzero
from logzero import logger

from util import normalize


FLAG_PREPROC_DUP_ID = False


def read_id_list_data(
        input_path: str,
) -> dict[str, str]:

    new_senid_to_orig_senid = {}

    with open(input_path, encoding='utf-8') as f:
        logger.info(f'Read: {input_path}')
        for line in f:
            array = line.strip('\n').split('\t')
            new_senid_with_subid = array[0]
            new_senid = ''.join(new_senid_with_subid.split(':')[0:-1])
            orig_senid = array[1]
            new_senid_to_orig_senid[new_senid_with_subid] = orig_senid

    logger.info(f'Loaded {len(new_senid_to_orig_senid)} sentences.')
    return new_senid_to_orig_senid


def read_original_text(
        input_paths: str,
        target_orig_senids: set[str],
        index_sent_id: int,
        index_sent_text: int,
        orig_data_type: str = None,
):
    orig_senid_to_txts = {}

    target_orig_senids_wo_branch = set([oid.split('@')[0] for oid in target_orig_senids])

    for input_path in input_paths:
        ## set data_type
        data_type = None
        if orig_data_type == 'rakuten_ichiba':
            if os.path.basename(input_path).startswith('shop_review'):
                data_type = 'RK_ICB_S'
            elif os.path.basename(input_path).startswith('item_review'):
                data_type = 'RK_ICB_I'
            else:
                logger.info(f'Unsupported data type: {orig_data_type}')

        elif orig_data_type == 'rakuten_travel':
            data_type = 'RK_TRV'

        elif orig_data_type == 'rakuten_recipe':
            if os.path.basename(input_path).startswith('recipe01'):
                data_type = 'RK_RCP_I'
            elif os.path.basename(input_path).startswith('recipe03'):
                data_type = 'RK_RCP_P'
            elif os.path.basename(input_path).startswith('recipe04'):
                data_type = 'RK_RCP_T'
            else:
                logger.info(f'Unsupported data type: {orig_data_type}')

        elif orig_data_type == 'amazon':
            data_type = 'AM'

        elif orig_data_type == 'niconico_video':
            data_type = 'NC_V'

            if not input_path.endswith('.jsonl'):
                continue

            file_id = int(os.path.basename(input_path).split('.jsonl')[0])
            if file_id < 3251 or 3410 < file_id:
                continue

        elif orig_data_type == 'nicopedia':
            data_type = 'NC_P'

            if not (os.path.basename(input_path).startswith('res')
                    and input_path.endswith('.csv')
            ):
                continue

        elif orig_data_type == 'jwtd':
            data_type = 'JW'

        elif orig_data_type != None:
            logger.info(f'Unsupported data type: {orig_data_type}')

        ## read file
        if input_path.endswith('.csv'):
            if not data_type == 'NC_P':
                continue

            with open(input_path, encoding='utf-8') as f:
                logger.info(f'Read: {input_path}')
                for rows in csv.reader(f, escapechar='\\'):                    
                    art_id = int(rows[0])
                    res_id = int(rows[1])
                    txt    = rows[3]
                    orig_senid = f'a{art_id:07d}-r{res_id:07d}'
                    sid_txt_list = [(orig_senid, txt)]
     
                    for (orig_senid, txt) in sid_txt_list:
                        if orig_senid in target_orig_senids_wo_branch:
                            # there are multiple examples that have the same orig_senid
                            if not orig_senid in orig_senid_to_txts:
                                orig_senid_to_txts[orig_senid] = []
                            orig_senid_to_txts[orig_senid].append(txt)

        else:
            with open(input_path, encoding='utf-8') as f:
                logger.info(f'Read: {input_path}')
                for i, line in enumerate(f):
                    if i > 0 and i % 100000 == 0:
                        logger.info(f'Read: {i} lines')                
         
                    line = line.strip('\n')
                    array = line.split('\t')
                    sid_txt_list = None
     
                    if data_type == 'RK_ICB_S':
                        user_id = array[0]
                        shop_id = array[2]
                        date    = array[6].replace('-', '').replace(':', '').replace(' ', '-')
                        orig_senid = f'shop:{user_id}:{shop_id}:{date}'
                        txt     = array[4]
                        sid_txt_list = [(orig_senid, txt)]
     
                    elif data_type == 'RK_ICB_I':
                        user_id = array[0]
                        item_id = array[4]
                        date    = array[15].replace('-', '').replace(':', '').replace(' ', '-')
                        orig_senid = f'item:{user_id}:{item_id}:{date}'
                        txt     = array[13]
                        sid_txt_list = [(orig_senid, txt)]
     
                    elif data_type == 'RK_TRV':
                        user_id = array[0]
                        fac_id  = array[2]
                        date    = array[1].replace('-', '').replace(':', '').replace(' ', '-')
                        orig_senid = f'{user_id}:{fac_id}:{date}'
                        txt    = array[16]
                        sid_txt_list = [(orig_senid, txt)]
     
                    elif data_type == 'RK_RCP_I':
                        doc_id  = array[0]
                        orig_senid_trg = f'{doc_id}-T' # trigger
                        orig_senid_int = f'{doc_id}-I' # introduction
                        orig_senid_pt  = f'{doc_id}-P' # one point info
                        txt_trg = array[6]
                        txt_int = array[7]
                        txt_pt  = array[14]
                        sid_txt_list = [
                            (orig_senid_trg, txt_trg),
                            (orig_senid_int, txt_int),
                            (orig_senid_pt, txt_pt),
                        ]
     
                    elif data_type == 'RK_RCP_P':
                        doc_id = array[0]
                        step_n = array[1]
                        orig_senid = f'{doc_id}-S-{step_n}'
                        txt    = array[2]
                        sid_txt_list = [(orig_senid, txt)]
                        
                    elif data_type == 'RK_RCP_T':
                        doc_id  = array[0]
                        user_id = array[1]
                        date    = array[4].replace('/', '')
                        orig_senid = f'{doc_id}-R:{user_id}:{date}'
                        txt     = array[2]
                        sid_txt_list = [(orig_senid, txt)]
     
                    elif data_type == 'AM':
                        orig_senid = array[2]
                        txt1 = array[12] # title
                        txt2 = array[13] # main text
                        # @@1@@ will be replaced by "\" which means linebreak
                        txt  = f'{txt1}@@1@@{txt2}'.replace('<BR>', '')
                        sid_txt_list = [(orig_senid, txt)]
     
                    elif data_type == 'NC_V':
                        data_dict = json.loads(line)
                        vid = data_dict['video_id']
                        txt1 = data_dict['title']
                        txt2 = data_dict['description']
                        sid_txt_list = [(f'{vid}:T', txt1),
                                        (f'{vid}:D', txt2)]
     
                    elif data_type == 'JW':
                        data_dict = json.loads(line)
                        art_id  = int(data_dict['page'])
                        rev_id1 = int(data_dict['pre_rev'])
                        rev_id2 = int(data_dict['post_rev'])
                        pre_diff = data_dict['diffs'][0]['pre_str']
                        pos_diff = data_dict['diffs'][0]['post_str']
                        txt      = data_dict['pre_text']
                        txt_norm = normalize(txt)
                        ent_id = f'{art_id:07d}-{rev_id1:08d}-{rev_id2:08d}-{pre_diff}-{pos_diff}-{txt_norm[:5]}-{txt_norm[-5:]}'
                        sid_txt_list = [(ent_id, txt)]

                    else:
                        if len(array) <= index_sent_text-1:
                            logger.debug(f'Skipped {i}-th line w/o text in {input_path}.')
                            continue

                        orig_senid = array[index_sent_id-1]
                        txt = array[index_sent_text-1]
                            
                        sid_txt_list = [(orig_senid, txt)]
     
                    for (orig_senid, txt) in sid_txt_list:
                        if orig_senid in target_orig_senids_wo_branch:
                            # there are multiple examples that have the same orig_senid
                            if not orig_senid in orig_senid_to_txts:
                                orig_senid_to_txts[orig_senid] = []
                            orig_senid_to_txts[orig_senid].append(txt)


    orig_senid_to_txt = {}
    for orig_senid, txt_list in orig_senid_to_txts.items():
        if len(txt_list) == 1:
            orig_senid_to_txt[orig_senid] = txt_list[0]
        else:
            if FLAG_PREPROC_DUP_ID:
                orig_senid_to_txt[orig_senid] = txt_list
            else:
                for i, txt in enumerate(txt_list):
                    orig_senid_mod = f'{orig_senid}@{i+1}'
                    orig_senid_to_txt[orig_senid_mod] = txt

    logger.info(f'The total number of extracted texts: {len(orig_senid_to_txt)}')

    return orig_senid_to_txt


def write_restored_data(
        data_name_to_idmap: dict[str, dict[str, str]],
        orig_senid_to_txt: dict[str, str],
        output_dir: str,
        normalize_char: bool = False,
        html_unescape: bool = False,
        remove_html_tag: bool = False,
) -> None:

    n_warn = 0
    for data_name, new_senid_to_orig_senid in data_name_to_idmap.items():
        output_path = os.path.join(output_dir, f'{data_name}.txt')
        with open(output_path, 'w', encoding='utf-8') as fw:
            for new_senid in sorted(new_senid_to_orig_senid.keys()):
                orig_senid = new_senid_to_orig_senid[new_senid]

                if orig_senid in orig_senid_to_txt:
                    txt = orig_senid_to_txt[orig_senid]

                    if type(txt) == str:
                        txt_list = [txt]
                    elif type(txt) == list: # only when FLAG_PREPROC_DUP_ID == True
                        txt_list = txt
                    else:
                        assert False

                    if normalize_char:
                        norm_txt_list = [
                            normalize(
                                txt,
                                replace_linebreak=True,
                                html_unescape=html_unescape,
                                remove_html_tag=remove_html_tag,
                            ) for txt in txt_list]
                        txt_list = norm_txt_list

                    txt = ';'.join(txt_list)
                    fw.write(f'{new_senid}\t{orig_senid}\t{txt}\n')

                else:
                    n_warn += 1
                    logger.debug(f'{new_senid} -> {orig_senid} not in orig_senid_to_txt')
                    fw.write(f'{new_senid}\t{orig_senid}\tNOT_FOUND\n')

            if n_warn > 0:
                logger.debug(f'Num of NOT_FOUND: {n_warn}')
            logger.info(f'Saved: {output_path}')


def main():
    logzero.loglevel(20)

    parser = argparse.ArgumentParser()
    parser.add_argument('--id_list_paths', '-i', type=str, required=True)
    parser.add_argument('--txt_paths', '-t', type=str, required=True)
    parser.add_argument('--output_dir', '-o', type=str, required=True)
    parser.add_argument('--index_sent_id', type=int, default=1)
    parser.add_argument('--index_sent_text', type=int, default=2)
    parser.add_argument('--orig_data_type', type=str, choices=('rakuten_ichiba', 'rakuten_travel', 'rakuten_recipe', 'amazon', 'niconico_video', 'nicopedia', 'jwtd'))
    parser.add_argument('--normalize_characters', '-n', action='store_true')
    parser.add_argument('--html_unescape', action='store_true')
    parser.add_argument('--remove_html_tag', action='store_true')
    args = parser.parse_args()

    data_name_to_idmap: dict[str, dict[str, str]] = {}

    for id_list_path in args.id_list_paths.split(','):
        data_name = os.path.basename(id_list_path).split('.txt')[0]
        data_name_to_idmap[data_name] = read_id_list_data(id_list_path)

    target_orig_senids = set()
    for new_senid_to_orig_senid in data_name_to_idmap.values():
        target_orig_senids |= set(new_senid_to_orig_senid.values())

    input_paths = []
    for path in args.txt_paths.split(','):
        if os.path.isdir(path):
            input_paths.extend([
                os.path.join(path, child_file)
                for child_file in os.listdir(path)
                if os.path.isfile(os.path.join(path, child_file))
            ])
        else:
            input_paths.append(path)
    assert len(input_paths) > 0

    orig_senid_to_txt = read_original_text(
        input_paths,
        target_orig_senids,
        args.index_sent_id,
        args.index_sent_text,
        args.orig_data_type,
    )

    write_restored_data(
        data_name_to_idmap,
        orig_senid_to_txt,
        args.output_dir,
        args.normalize_characters,
        args.html_unescape,
        args.remove_html_tag,
    )


if __name__ == '__main__':
    main()
