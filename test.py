import json
import os
import re

from config import SLICED_EXCEL_PATH, HTML_PATH
from log import get_logger
from spider import BaiduHandler, WikiSpider, WikiHandler


def wiki():
    wiki_logger = get_logger('wiki')
    with open('未处理列表.txt') as f:
        kws = re.split(r'-\d\n', f.read())
        for kw in kws:
            html = WikiSpider().search_by_keyword(kw)
            data = WikiHandler().handle(html)
            if not data:
                wiki_logger.error(f'未找到：{kw}')

            fp = 'wiki'
            if not os.path.exists(fp):
                os.makedirs(fp)

            with open(f'{fp}/{kw}.html', 'w') as fw:
                fw.write(html)


baidu = BaiduHandler()


#
# fpath = 'files/分词后的数据-json-修正'
# for fname in os.listdir(fpath):
#     kw = fname.split('/')[-1].strip('.json')
#     with open(fpath + '/' + kw + '.json') as f:
#         baidu.write_to_excel(f'{SLICED_EXCEL_PATH}/{kw}.xlsx', **json.loads(f.read()))


def update():
    root = '/Users/joeyon/PycharmProjects/tmp/2-分词后的数据-json'
    for file in os.listdir(root):
        name = file.replace('.json', '')
        with open(HTML_PATH + '/' + name + '.html') as f:
            html = f.read()
            baidu.handle(name, html)


update()
