import glob
import re
import sys
import zenhan


SEP_SYM = '：'


def proc_text(text):
    text = re.sub('［', '', text)
    text = re.sub('\[', '', text)
    text = zenhan.h2z(text)
    text = re.sub('●+', '*', text)
    text = re.sub('〓.*〓', '*', text)
    text = re.sub('《[^《]*》', '', text)
    text = re.sub('》', '', text)
    text = re.sub('＜[^＞]*＞', '', text)
    text = re.sub('【[^】]*】', '', text)
    text = re.sub('｛[^｝]*｝', '', text)
    text = re.sub('（[^）]*）', '', text)
    text = re.sub('｛笑」', '', text)
    text = text.strip('　')
    return text


def read_and_write(path):
    line_num = 1
    with open(path) as f:
        doc_id = path.split('/')[-1].split('.')[0]
        for line in f:
            line = line.strip('\n')

            if re.match('[0-9: /]+', line):
                continue

            if SEP_SYM in line:
                array = line.split(SEP_SYM)
                per  = zenhan.z2h(array[0])
                text = array[1]
            else:
                per = ''
                text = line

            text_tmp = proc_text(text)
            if (not text_tmp or 
                re.match('^[、。\*]+$', text_tmp)
            ):
                text_tmp = '<NO_TEXT>'

            sen_id = f'JCSC-{doc_id}-{line_num:04d}'
            print(f'{sen_id}\t{per}\t{text}\t{text_tmp}')
            line_num += 1


if __name__ == '__main__':
    path = sys.argv[1]
    read_and_write(path)
