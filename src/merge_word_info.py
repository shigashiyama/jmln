import argparse
import os

from logzero import logger


ORIG_SENTIDS_EXCLUDE = ['OY15_00054:1800-1860']


def sentence_reader(input_path):
    with open(input_path, encoding='utf-8') as f:
        logger.info(f'Read: {input_path}')
        for line in f:
            # [new_id, orig_id, text]
            yield line.strip('\n').split('\t')
    StopIteration


def read_and_write(
        input_sent_path: str,
        input_masked_path: str,
        output_sent_data_path: str,
        output_word_data_path: str,
        min_info: bool = True,
        not_output_orig_sentid: bool = False,
        do_sent_seg: bool = False,
) -> None:

    sent_reader = sentence_reader(input_sent_path)
    sent_info = sent_reader.__next__()
    new_sentid = sent_info[0]
    orig_sentid = sent_info[1]
    sent_text = sent_info[2]
    begin_offset = 0

    subsents = []

    if output_sent_data_path:
        fw_sent = open(output_sent_data_path, 'w', encoding='utf-8')

    with (open(input_masked_path, encoding='utf-8') as f,
          open(output_word_data_path, 'w', encoding='utf-8') as fw_word
    ):
        logger.info(f'Read: {input_masked_path}')
        for line in f:
            line = line.strip('\n')
            if line.startswith('#'):
                new_sentid_from_masked = line.split('# ')[1]
                while (new_sentid_from_masked != orig_sentid # tmp
                       and new_sentid_from_masked != new_sentid
                       and new_sentid_from_masked.split(':')[0] != new_sentid.split(':')[0]
                ):
                    new_sentid_tmp = new_sentid.split(':')[0]
                    # logger.info(f'Skip: {new_sentid_tmp}. Next: {new_sentid_from_masked}')

                    sent_info = sent_reader.__next__()
                    new_sentid = sent_info[0]
                    orig_sentid = sent_info[1]
                    sent_text = sent_info[2]
                    begin_offset = 0

            elif not line:
                if not do_sent_seg:
                    if not_output_orig_sentid:
                        fw_word.write(f'# SENT_ID={new_sentid}\n')
                    else:
                        fw_word.write(f'# SENT_ID={new_sentid} ORIG_SENT_ID={orig_sentid}\n')

                for i, subsent in enumerate(subsents):
                    if len(subsent) > 0:
                        if do_sent_seg:
                            if not_output_orig_sentid:
                                fw_word.write(f'# SENT_ID={new_sentid}:{i+1}\n')
                            else:
                                fw_word.write(f'# SENT_ID={new_sentid}:{i+1} ORIG_SENT_ID={orig_sentid}\n')

                        for surf, word_line in subsent:
                            # if surf != '\\': # skip newline character
                            fw_word.write(f'{word_line}\n')

                        if do_sent_seg or i+1 == len(subsents):
                            fw_word.write(f'\n')

                        if output_sent_data_path:
                            # skip newline character
                            #subsent_text = ''.join([word[0] for word in subsent if word[0] != '\\'])
                            subsent_text = ''.join([word[0] for word in subsent])
                            if not_output_orig_sentid:
                                fw_sent.write(f'{new_sentid}:{i+1}\t\t{subsent_text}\n')
                            else:
                                fw_sent.write(f'{new_sentid}:{i+1}\t{orig_sentid}\t{subsent_text}\n')

                subsents = []

                try:
                    sent_info = sent_reader.__next__()
                    new_sentid = sent_info[0]
                    orig_sentid = sent_info[1]
                    sent_text = sent_info[2]
                    begin_offset = 0

                except StopIteration:
                    pass

            else:
                array     = line.split('\t')
                surf_mask = array[0]
                pos       = array[1]
                ctype     = array[2]
                cform     = array[3]

                if min_info:
                    cate     = array[4]
                    norm_id  = array[5]
                    flags    = array[6]
                else:
                    yomi     = array[4]
                    base     = array[5]
                    lemma    = array[6]
                    lemma_id = array[7]
                    cate     = array[8]
                    norm_id  = array[9]
                    flags    = array[10]

                if '<BOS>' in flags:
                    subsents.append([])

                surf = sent_text[begin_offset:begin_offset+len(surf_mask)]
                begin_offset += len(surf_mask)

                if ('<IGN>' in flags
                    or '\\' in surf
                ):
                    pass
                elif min_info:
                    word_line = f'{surf}\t{pos}\t{ctype}\t{cform}\t{cate}\t{norm_id}'
                    subsents[-1].append((surf, word_line))
                else:
                    word_line = f'{surf}\t{pos}\t{ctype}\t{cform}\t{yomi}\t{base}\t{lemma}\t{lemma_id}\t{cate}\t{norm_id}'
                    subsents[-1].append((surf, word_line))

    if subsents:
        if not do_sent_seg:
            fw_word.write(f'# SENT_ID={new_sentid} ORIG_SENT_ID={orig_sentid}\n')

        for i, subsent in enumerate(subsents):
            if len(subsent) > 0:
                fw_word.write(f'# SENT_ID={new_sentid}:{i+1} ORIG_SENT_ID={orig_sentid}\n')

                for surf, word_line in subsent:
                    fw_word.write(f'{word_line}\n')

                if do_sent_seg or i+1 == len(subsents):
                    fw_word.write(f'\n')

                if output_sent_data_path:
                    subsent_text = ''.join([word[0] for word in subsent])
                    fw_sent.write(f'{new_sentid}:{i+1}\t{orig_sentid}\t{subsent_text}\n')

    logger.info(f'Saved: {output_word_data_path}')
    if output_sent_data_path:
        fw_sent.close()
        logger.info(f'Saved: {output_sent_data_path}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_sent_path', '-is', type=str, required=True)
    parser.add_argument('--input_masked_path', '-im', type=str, required=True)
    parser.add_argument('--output_sent_data_path', '-os', type=str)
    parser.add_argument('--output_word_data_path', '-ow', type=str, required=True)
    parser.add_argument('--not_output_orig_sentid', action='store_true')
    parser.add_argument('--unsegmented_sentences', action='store_true')
    args = parser.parse_args()
                        
    read_and_write(
        args.input_sent_path,
        args.input_masked_path,
        args.output_sent_data_path,
        args.output_word_data_path,
        not_output_orig_sentid=args.not_output_orig_sentid,
        do_sent_seg=args.unsegmented_sentences,
    )
    

if __name__ == '__main__':
    main()
