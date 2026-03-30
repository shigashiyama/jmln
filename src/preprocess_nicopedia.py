import html
import pandas as pd
import re
import sys
import zenhan


pat_br    = re.compile('<br ?/?>')
pat_html  = re.compile('</?[0-9a-zA-Z_/:;%#$&@\?\(\)~\.,=\+\-"\'` ]+ ?>')


def normalize(text):
    text = html.unescape(text)
    text = text.replace('\\', '@@1@@')
    text = pat_br.sub('@@1@@', text)
    text = pat_html.sub('', text)
    text = zenhan.h2z(text, mode=7)
    text = text.replace('～', '〜')
    text = re.sub('＠＠１＠＠', '\\\\', text)
    text = re.sub('\\\\+', '\\\\', text)
    return text


def read_head(path):
    aid2title = {}
    with open(path) as f:
        for line in f:
            line = line.rstrip()
            art_id = -1
            title = atype = ''
            line = line.replace(',\\N', ',""').replace('",', '"\t')
            array = line.split('\t')
            for i in range(0, 4):
                if len(array[i]) == 0:
                    print(line, file=sys.stderr)
                    continue

                if array[i][0] == '"' and array[i][-1] == '"':
                    elem = array[i][1:-1]
                elem = elem.replace('\\"', '"')

                if i == 0: 
                    art_id = int(elem) # 記事ID
                elif i == 1:
                    title = elem # 記事タイトル
                elif i == 3:
                    atype = elem # 記事種類(a:単語,v:動画,i:商品,l:生放送)
                # 2: 記事ヨミ
                # 4: 記事作成日時

            aid2title[art_id] = (atype, title)

    return aid2title
    

def read_res(path, aid2title):
    with open(path) as f:
        for line in f:
            line = line.rstrip()
            array = line.replace('",', '"\t').split('\t')
            for i in range(0, 4):
                if len(array[i]) == 0:
                    print(line, file=sys.stderr)
                    continue

                if array[i][0] == '"' and array[i][-1] == '"':
                    elem = array[i][1:-1]
                elem = elem.replace('\\"', '"')

                if i == 0: 
                    art_id = int(elem) # 記事ID
                elif i == 1:
                    res_id = elem # レスID
                elif i == 2:
                    date   = elem # レス投稿日時
                    date   = f'{date[0:8]}-{date[8:]}'
                elif i == 3:
                    text   = normalize(elem) # レス本文

            atype = atitle = ''
            if art_id in aid2title:
                ent = aid2title[art_id]
                atype = ent[0]
                atitle = normalize(ent[1])
                
            print('{}\t{}\t{}\t{}\t{}\t{}'.format(
                art_id, atype, atitle, res_id, date, text))


if __name__ == '__main__':
    path1 = sys.argv[1]
    path2 = sys.argv[2]
    amap = read_head(path1)
    print('Load', path1, file=sys.stderr)
    read_res(path2, amap)
