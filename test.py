import os
import re

from bs4 import BeautifulSoup

from config import HTML_PATH
from common.log import get_logger
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


def get_dicts():
    ret = list()
    with open('dicts.txt', 'w') as f:
        with open('dictionary.txt') as fr:
            for item in fr.read().split('\n'):
                if not item:
                    continue
                ret.append(item)

        f.write(str(ret))


baidu = BaiduHandler()


#
# fpath = 'files/分词后的数据-json-修正'
# for fname in os.listdir(fpath):
#     kw = fname.split('/')[-1].strip('.json')
#     with open(fpath + '/' + kw + '.json') as f:
#         baidu.write_to_excel(f'{SLICED_EXCEL_PATH}/{kw}.xlsx', **json.loads(f.read()))


def get_body_not_found():
    root = '/Users/joeyon/Desktop/files/修正后的-json'

    for file in os.listdir(root):
        name = file.replace('.json', '')
        with open(HTML_PATH + '/' + name + '.html') as f:
            html = f.read()
            soup = BeautifulSoup(html, features='lxml')
            no_result = soup.find('div', class_='errorBox')
            if no_result:
                return {}

            content_tag = soup.find('div', class_='content')
            h2_name, h3_name = '', ''

            # class如果有多个，只能根据第一个来查找
            tag = content_tag.find('div', class_='para-title')

            while True:
                try:
                    tag_attrs = getattr(tag, 'attrs', {})
                    tag_cls_list = tag_attrs.get('class', [])
                    if not tag_cls_list:
                        print(name)
                        break
                except Exception as e:
                    print(e)
                finally:
                    tag = getattr(tag, 'next_sibling', None)
                    if not tag:
                        break


get_body_not_found()
