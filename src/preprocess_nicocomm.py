import html
import pandas as pd
import re
import sys
import zenhan


COLUMNS = {0: 'video_id', 1: 'watch_num', 2: 'comment_num', 3: 'mylist_num', 
           4: 'title', 5: 'description', 6: 'category', 7: 'tags', 8: 'upload_time', 
           9: 'file_type', 10: 'length', 11: 'size_high', 12: 'size_low'}

pat_br    = re.compile('<br ?/?>')
pat_html  = re.compile('</?[0-9a-zA-Z_/:;%#$&@\?\(\)~\.,=\+\-"\'`“”‘’ ]+ ?>')
pat_html2 = re.compile('<font ?[^>]+>')

CATES = {1: 'エンタメ・音楽', 2: '生活・一般・スポ', 3: '科学・技術',
         4: '政治', 5: 'アニメ・ゲーム・絵', 6: 'その他',}

SUBCATES = {'ASMR': 1, 'MMD': 1, 'VOCALOID': 1, 'ニコニコインディーズ': 1, 'バーチャル': 1, 
            '音楽': 1, '演奏シテミタ': 1, '歌ッテミタ': 1, '踊ッテミタ': 1,
            'スポーツ': 2, '車載動画': 2, '鉄道': 2, '動物': 2, '旅行': 2, '料理': 2, 
            '歴史': 2, 'ニコニコ動画講座': 2,
            'ニコニコ技術部': 3, 'ニコニコ手芸部': 3, '科学': 3, '作ッテミタ': 3,
            '政治': 4,
            'TRPG': 5, 'アイドルマスター': 5, 'アニメ': 5, 'エンターテイメント': 5,
            'ゲーム': 5, '東方': 5, '描イテミタ': 5, '実況プレイ動画': 5, 'ラジオ': 5,
            'ソノ他': 6, '例ノアレ': 6, '日記': 6, '': 6,}


def normalize(text):
    text = html.unescape(text)
    text = pat_br.sub('@@1@@', text)
    text = pat_html.sub('', text)
    text = pat_html2.sub('', text)
    text = zenhan.h2z(text, mode=7)
    text = text.replace('～', '〜')
    text = re.sub('＠＠１＠＠', '\\\\', text)
    text = re.sub('\\\\+', '\\\\', text)
    return text


def read_jsonl(path):
    df = pd.read_json(path, orient='records', lines=True)
    for i in df.index:
        title = normalize(df.loc[i,COLUMNS[4]])
        desc  = normalize(df.loc[i,COLUMNS[5]])
        subcate = df.loc[i,COLUMNS[6]]
        cate = CATES[SUBCATES[subcate]] if subcate in SUBCATES else None

        row = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(
            df.loc[i,COLUMNS[0]], df.loc[i,COLUMNS[1]], df.loc[i,COLUMNS[2]],
            df.loc[i,COLUMNS[3]], df.loc[i,COLUMNS[8]], df.loc[i,COLUMNS[10]],
            cate, subcate, title, desc,
        )
        print(row)


if __name__ == '__main__':
    path = sys.argv[1]
    read_jsonl(path)
