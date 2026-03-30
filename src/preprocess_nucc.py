import argparse
import re

import zenhan
from logzero import logger


HEAD_SYM = '＠'
HEAD_SYM2 = '％'
SEP_SYM = '：'


def proc_text(text: str) -> str:
    text = re.sub('Ｆ060', 'F060', text)
    text = re.sub('[FM][0-9]{3}', 'Ｘ', text)
    text = re.sub('（[^）]*）', '', text)
    text = re.sub('＜[^＞]*＞', '', text)
    text = re.sub('【[^】]*】', '', text)
    text = zenhan.h2z(text)
    text = re.sub('＊＊＊', '*', text)
    text = re.sub('＊([^＊]+)＊', '*', text)
    text = text.strip('　')
    return text


def read_and_write(input_path: str, output_path: str) -> None:
    line_num = 1
    prev_per = None
    next_per = None
    next_text = None

    with (
            open(input_path, encoding='utf-8') as f,
            open(output_path, 'w', encoding='utf-8') as fw,
    ):
        logger.info(f'Read: {input_path}')
        doc_id = input_path.split('/')[-1].split('.')[0]
        for line in f:
            line = line.strip('\n')

            if line.startswith(HEAD_SYM) or line.startswith(HEAD_SYM2):
                continue

            if SEP_SYM in line:
                array = line.split(SEP_SYM)
                per  = array[0]
                text = array[1]

                if line[0] in ('M', 'F', 'X'):
                    pass
                elif per == 'Ｘ':
                    per = 'X'
                elif per == '　F128':
                    per = 'F128'
                elif per == '＊F150':
                    per = 'F150'
                elif per == 'おF114':
                    per = 'F114'
                elif per == 'ＭＳ':
                    per = 'MS'

                elif line.startswith('＜笑い＞F'):
                    per = array[0].split('＞')[1]

                elif line.startswith('：F141'):
                    per = array[1]
                    text = array[2]

                elif line.startswith('＜中略') or line.startswith('＜録音不良'):
                    per = ''
                    text = '<NO_TEXT>'

                elif line.startswith('（ふーん、そうかー）あの、何かさ、何だっけ、「ミッション：インポッシブル'):
                    per = ''
                    text = line

                elif (line.index(SEP_SYM) >= 10 or line.startswith('（うん）：')):
                    if line.startswith('（うん）：'):
                        line = line[5:]
                    
                    bos_idxs = [m.span()[0] for m in re.finditer('[FM][0-9]+：', line)]
                    if len(bos_idxs) == 1:
                        sep_idx = bos_idxs[0]
                    elif len(bos_idxs) == 2 and bos_idxs[0] == 0:
                        sep_idx = bos_idxs[1]
                    else:
                        logger.error(f'Error_1 - {line_num}:{line}')
                        continue

                    subline1 = line[:sep_idx]
                    if SEP_SYM in subline1:
                        per, text = subline1.split(SEP_SYM)
                    else:
                        per = prev_per
                        text = subline1

                    subline2 = line[sep_idx:]
                    next_per, next_text = subline2.split(SEP_SYM)                    

                else:
                    logger.error(f'Error_2 - {line_num}:{line}')
                    continue

            else:
                per = prev_per
                text = line

            text_tmp = proc_text(text)
            if not text_tmp:
                text_tmp = '<NO_TEXT>'
                per = ''
            sen_id = f'NUCC-{doc_id}-{line_num:04d}'
            fw.write(f'{sen_id}\t{per}\t{text}\t{text_tmp}\n')

            prev_per = per
            line_num += 1

            if next_text:
                text_tmp = proc_text(next_text)
                if not text_tmp:
                    text_tmp = '<NO_TEXT>'
                    next_per = ''
                sen_id = f'NUCC-{doc_id}-{line_num:04d}'
                fw.write(f'{sen_id}\t{next_per}\t{text_tmp}\n')

                prev_per = next_per
                next_per = None
                next_text = None
                line_num += 1                

        logger.info(f'Saved: {output_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', '-i', type=str, required=True)
    parser.add_argument('--output_path', '-o', type=str, required=True)
    args = parser.parse_args()

    read_and_write(args.input_path, args.output_path)
