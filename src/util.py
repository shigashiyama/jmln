import argparse
import html
from collections.abc import Iterable
import re
import sys

import zenhan


def normalize(
        text: str,
        target_column: int = -1,
        normalize_space: bool = True,
        normalize_tilde: bool = True,
        html_unescape: bool = True,
        remove_html_tag: bool = False,
        replace_url: bool = False,
        replace_linebreak: bool = False,
) -> str:

    ngen = normalized_text_generator(
        [text],
        target_column=target_column,
        normalize_space=normalize_space,
        normalize_tilde=normalize_tilde,
        html_unescape=html_unescape,
        remove_html_tag=remove_html_tag,
        replace_url=replace_url,
        replace_linebreak=replace_linebreak,
    )
    return ngen.__next__()


def normalized_text_generator(
        stream: Iterable,
        target_column: int = -1,
        normalize_space: bool = True,
        normalize_tilde: bool = True,
        html_unescape: bool = True,
        #replace_html_tag: bool = False,
        remove_html_tag: bool = False,
        replace_url: bool = False,
        replace_linebreak: bool = False,
):
        
    #pat_html = re.compile('</?[0-9a-zA-Z_/:%#$&\?\(\)~\.=\+\- ]+ ?>')
    pat_html = re.compile('</?[0-9a-zA-Z_/:;%#$&@\?\(\)~\.,=\+\-"\'`“”‘’ ]+ ?>')
    pat_html2 = re.compile('<font ?[^>]+>')
    pat_br   = re.compile('<br ?/?>')
    pat_url  = re.compile('http(s)?://[0-9a-zA-Z_/:%#$&\?\(\)~\.=\+\-]+')

    for line in stream:
        line = line.rstrip('\n')
        if target_column > -1:
            array = line.split('\t')
            text = array[target_column]
        else:
            text = line

        if html_unescape:
            text = html.unescape(text)

        if replace_linebreak:
            text = pat_br.sub('@@1@@', text)
            text = re.sub('\n', '@@1@@', text)
            text = re.sub('\\\\n', '@@1@@', text)

        # if replace_html_tag:
        #     text = pat_html.sub('@@2@@', text)
        if remove_html_tag:
            text = pat_html.sub('', text)
            text = pat_html2.sub('', text)

        if replace_url:
            text = pat_url.sub('@@3@@', text)

        if normalize_space:
            text = zenhan.h2z(text, mode=7, ignore='')
        else:
            text = zenhan.h2z(text, mode=7, ignore=' ')

        if normalize_tilde:
            text = text.replace('～', '〜')

        # postprocessing
        if replace_linebreak:
            text = re.sub('＠＠１＠＠', '\\\\', text)
            text = re.sub('\\\\+', '\\\\', text)

        # if replace_html_tag:
        #     text = re.sub('＠＠２＠＠', '@', text)
        
        if replace_url:
            text = re.sub('＠＠３＠＠', '<URL>', text)

        if target_column > -1:
            columns = []
            if target_column > 0:
                columns.extend(array[0:target_column])
            columns.append(text)
            if target_column < len(array)-1:
                columns.extend(array[target_column+1:])
            yield '\t'.join(columns)
        else:
            yield text

    StopIteration


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target_column', '-c', type=int, default=-1)
    parser.add_argument('--replace_html_tag', '-t', action='store_true')
    parser.add_argument('--replace_linebreak', '-l', action='store_true')
    args = parser.parse_args()

    ngen = normalized_text_generator(
        iter(sys.stdin.readline, ''), 
        target_column=args.target_column,
        normalize_space=True,
        normalize_tilde=True,
        html_unescape=True,
        replace_html_tag=args.replace_html_tag,
        replace_linebreak=args.replace_linebreak,
    )

    for text in ngen:
        print(text)


if __name__ == '__main__':
    main()
